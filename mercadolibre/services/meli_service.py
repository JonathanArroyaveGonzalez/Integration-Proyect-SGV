"""MercadoLibre API service for centralized authentication and requests."""

import logging
import time
import uuid
from typing import Dict, Any, Optional, List
from functools import wraps
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from project.config_db.repository import MeliConfigRepository
from mercadolibre.utils.exceptions import (
    MeliError, MeliAuthError, MeliNotFoundError,
    MeliBadRequestError, MeliRateLimitError, MeliServerError
)

logger = logging.getLogger(__name__)


def retry_on_rate_limit(max_retries: int = 3, delay: int = 5):
    """Decorator for retrying functions on rate limit errors."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except MeliRateLimitError:
                    retries += 1
                    if retries == max_retries:
                        raise
                    logger.warning(f"Rate limit hit, retrying in {delay} seconds...")
                    time.sleep(delay)
            return func(*args, **kwargs)
        return wrapper
    return decorator


class MeliService:
    """Service for MercadoLibre API interactions with automatic token refresh."""
    
    BASE_URL = "https://api.mercadolibre.com"
    TOKEN_URL = "https://api.mercadolibre.com/oauth/token"
    
    def __init__(self):
        """Initialize MeLi service with repository and session."""
        self.repo = MeliConfigRepository()
        self.request_id = str(uuid.uuid4())
        self._setup_session()
    
    def _setup_session(self):
        """Configure requests session with retry strategy."""
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.3,
            status_forcelist=[500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def _get_tokens(self) -> Dict[str, str]:
        """
        Get current tokens from database.
        
        Returns:
            Dict with access_token and refresh_token
            
        Raises:
            RuntimeError: If tokens not found
        """
        tokens = self.repo.get_tokens()
        if not tokens:
            raise RuntimeError("No tokens found in database")
        return tokens
    
    def _refresh_token(self, current_tokens: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """
        Refresh the access token using refresh token.
        
        Args:
            current_tokens: Optional dict with current tokens. If not provided, will fetch from DB.
            
        Returns:
            Dict with new access_token and refresh_token
            
        Raises:
            RuntimeError: If refresh fails
        """
        try:
            tokens = current_tokens or self._get_tokens()
            config = self.repo.get_config()
            
            if not config or not config.client_id or not config.client_secret:
                raise RuntimeError("Missing client credentials for token refresh")
            
            payload = {
                "grant_type": "refresh_token",
                "client_id": config.client_id,
                "client_secret": config.client_secret,
                "refresh_token": tokens['refresh_token']
            }
            
            response = self.session.post(self.TOKEN_URL, data=payload)
            response.raise_for_status()
            
            data = response.json()
            new_access_token = data['access_token']
            new_refresh_token = data['refresh_token']
            
            # Update tokens in database
            self.repo.update_tokens(new_access_token, new_refresh_token)
            
            logger.info(
                "Token refreshed successfully",
                extra={'request_id': self.request_id}
            )
            return {
                'access_token': new_access_token,
                'refresh_token': new_refresh_token
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(
                f"Token refresh failed: {str(e)}",
                extra={'request_id': self.request_id}
            )
            raise RuntimeError(f"Token refresh failed: {str(e)}")
    
    def _handle_api_error(self, response: requests.Response) -> None:
        """
        Handle API errors and raise appropriate exceptions.
        
        Args:
            response: Response object from the API
            
        Raises:
            MeliAuthError: For 401, 403 errors
            MeliNotFoundError: For 404 errors
            MeliBadRequestError: For 400 errors
            MeliRateLimitError: For 429 errors
            MeliServerError: For 5xx errors
        """
        error_data = {}
        try:
            error_data = response.json()
        except Exception:
            error_data = {'message': response.text}

        message = error_data.get('message', 'Unknown error')
        
        if response.status_code in (401, 403):
            raise MeliAuthError(
                f"Authentication error: {message}",
                status_code=response.status_code,
                response_data=error_data
            )
        elif response.status_code == 404:
            raise MeliNotFoundError(
                f"Resource not found: {message}",
                status_code=response.status_code,
                response_data=error_data
            )
        elif response.status_code == 400:
            raise MeliBadRequestError(
                f"Bad request: {message}",
                status_code=response.status_code,
                response_data=error_data
            )
        elif response.status_code == 429:
            raise MeliRateLimitError(
                f"Rate limit exceeded: {message}",
                status_code=response.status_code,
                response_data=error_data
            )
        elif response.status_code >= 500:
            raise MeliServerError(
                f"Server error: {message}",
                status_code=response.status_code,
                response_data=error_data
            )
        else:
            raise MeliError(
                f"Unexpected error: {message}",
                status_code=response.status_code,
                response_data=error_data
            )

    def _log_request(self, method: str, endpoint: str, **kwargs) -> None:
        """Log request details with correlation ID."""
        logger.info(
            f"API Request: {method} {endpoint}",
            extra={
                'request_id': self.request_id,
                'method': method,
                'endpoint': endpoint,
                'params': kwargs.get('params'),
                'headers': {k: v for k, v in kwargs.get('headers', {}).items() 
                          if k.lower() != 'authorization'}
            }
        )

    def _get_headers(self, access_token: str) -> Dict[str, str]:
        """
        Build request headers with authentication.
        
        Args:
            access_token: MercadoLibre access token
            
        Returns:
            Headers dictionary
        """
        return {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
    
    @retry_on_rate_limit()
    def request(
        self, 
        method: str, 
        endpoint: str, 
        auto_refresh: bool = True,
        **kwargs
    ) -> requests.Response:
        """
        Make authenticated request to MercadoLibre API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (without base URL)
            auto_refresh: Automatically refresh token on 401
            **kwargs: Additional arguments for requests
            
        Returns:
            Response object
            
        Raises:
            MeliError: Base class for all MercadoLibre API errors
            MeliAuthError: For authentication errors
            MeliNotFoundError: When resource is not found
            MeliBadRequestError: For invalid requests
            MeliRateLimitError: When rate limit is exceeded
            MeliServerError: For server-side errors
        """
        # Ensure endpoint starts with /
        if not endpoint.startswith('/'):
            endpoint = f'/{endpoint}'
        
        url = f"{self.BASE_URL}{endpoint}"
        tokens = self._get_tokens()
        
        # First attempt with current token
        headers = self._get_headers(tokens['access_token'])
        if 'headers' in kwargs:
            headers.update(kwargs['headers'])
        kwargs['headers'] = headers
        
        # Log request details
        self._log_request(method, endpoint, **kwargs)
        
        try:
            response = self.session.request(method, url, **kwargs)
            
            # If unauthorized and auto_refresh is enabled, try refreshing token
            if response.status_code == 401 and auto_refresh:
                logger.info(
                    "Token expired, refreshing...",
                    extra={'request_id': self.request_id}
                )
                try:
                    # Pass current tokens to avoid unnecessary DB query
                    new_tokens = self._refresh_token(current_tokens=tokens)
                    kwargs['headers'] = self._get_headers(new_tokens['access_token'])
                    response = self.session.request(method, url, **kwargs)
                except Exception as refresh_error:
                    logger.error(
                        f"Token refresh failed: {str(refresh_error)}",
                        extra={'request_id': self.request_id}
                    )
                    # Re-raise as MeliAuthError for consistent error handling
                    raise MeliAuthError(
                        f"Authentication failed: {str(refresh_error)}",
                        status_code=401
                    )
            
            if response.status_code != 200:
                self._handle_api_error(response)
                
            return response
            
        except requests.exceptions.RequestException as e:
            logger.error(
                f"Request failed: {str(e)}",
                extra={'request_id': self.request_id}
            )
            raise MeliError(f"Request failed: {str(e)}")
    
    def get(self, endpoint: str, **kwargs) -> requests.Response:
        """Make GET request to MercadoLibre API."""
        return self.request('GET', endpoint, **kwargs)
    
    def post(self, endpoint: str, **kwargs) -> requests.Response:
        """Make POST request to MercadoLibre API."""
        return self.request('POST', endpoint, **kwargs)
    
    def put(self, endpoint: str, **kwargs) -> requests.Response:
        """Make PUT request to MercadoLibre API."""
        return self.request('PUT', endpoint, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        """Make DELETE request to MercadoLibre API."""
        return self.request('DELETE', endpoint, **kwargs)

    # Customer-related methods
    def get_customer(self, customer_id: str) -> Dict[str, Any]:
        """
        Get customer information from MercadoLibre.
        
        Args:
            customer_id: MercadoLibre customer ID
            
        Returns:
            Customer data dictionary
            
        Raises:
            requests.exceptions.RequestException: If API request fails
        """
        response = self.get(f'/users/{customer_id}')
        if response.status_code != 200:
            logger.error(f"Failed to get customer {customer_id}: {response.status_code}")
            response.raise_for_status()
        return response.json()

    # Product-related methods
    def get_user_products(self, user_id: str) -> List[str]:
        """
        Get all product IDs for a MercadoLibre user.
        
        Args:
            user_id: MercadoLibre user ID
            
        Returns:
            List of product IDs
            
        Raises:
            requests.exceptions.RequestException: If API request fails
        """
        response = self.get(f'/users/{user_id}/items/search')
        if response.status_code != 200:
            logger.error(f"Failed to get products for user {user_id}: {response.status_code}")
            response.raise_for_status()
        return response.json().get('results', [])

    def get_product_description(self, product_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed description for a product.
        
        Args:
            product_id: MercadoLibre product ID
            
        Returns:
            Description data dictionary or None if not found
            
        Raises:
            requests.exceptions.RequestException: If API request fails
        """
        try:
            response = self.get(f'/items/{product_id}/description')
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Could not get description for product {product_id}: {response.status_code}")
                return None
        except Exception as e:
            logger.warning(f"Error getting description for product {product_id}: {e}")
            return None

    def _get_batch_products(self, batch_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Get detailed information for a batch of products (max 20).
        
        Args:
            batch_ids: List of product IDs (max 20)
            
        Returns:
            List of product details dictionaries
        """
        ids_param = ','.join(batch_ids)
        response = self.get('/items', params={'ids': ids_param})
        if response.status_code == 200:
            result = response.json()
            # Filter out any invalid responses and extract only valid products
            valid_products = [
                item['body'] for item in result 
                if item.get('code') == 200 and isinstance(item.get('body'), dict) and 'id' in item.get('body')
            ]
            return valid_products
        else:
            logger.error(f"Failed to get products batch: {response.status_code}")
            response.raise_for_status()
        return []

    def get_products_batch(self, product_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Get detailed information for multiple products including descriptions.
        MercadoLibre allows max 20 IDs per request.
        
        Args:
            product_ids: List of product IDs
            
        Returns:
            List of product details dictionaries with descriptions
            
        Raises:
            requests.exceptions.RequestException: If API request fails
        """
        if not product_ids:
            return []
            
        products = []
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        # Process in batches of 20
        for i in range(0, len(product_ids), 20):
            batch = product_ids[i:i+20]
            try:
                # Get basic product information
                batch_products = self._get_batch_products(batch)
                
                if batch_products:  # Only process if we have valid products
                    # Get descriptions in parallel
                    with ThreadPoolExecutor(max_workers=5) as executor:
                        future_to_product = {}
                        for product in batch_products:
                            if product and isinstance(product, dict) and 'id' in product:
                                future = executor.submit(self.get_product_description, product['id'])
                                future_to_product[future] = product
                    
                        for future in as_completed(future_to_product):
                            product = future_to_product[future]
                            try:
                                description = future.result()
                                if description:
                                    product['description_data'] = description
                            except Exception as e:
                                logger.warning(f"Could not get description for product {product.get('id', 'unknown')}: {e}")
                    
                    products.extend(batch_products)
                
            except Exception as e:
                logger.error(f"Error getting products batch: {e}")
                raise
                
        return products

    def get_product(self, product_id: str) -> Dict[str, Any]:
        """
        Get detailed information for a single product including description.
        
        Args:
            product_id: MercadoLibre product ID
            
        Returns:
            Product details dictionary
            
        Raises:
            requests.exceptions.RequestException: If API request fails
        """
        response = self.get(f'/items/{product_id}')
        if response.status_code != 200:
            logger.error(f"Failed to get product {product_id}: {response.status_code}")
            response.raise_for_status()
            
        product_data = response.json()
        
        # Try to get detailed description
        try:
            desc_response = self.get(f'/items/{product_id}/description')
            if desc_response.status_code == 200:
                product_data['description_data'] = desc_response.json()
        except Exception as desc_error:
            logger.warning(f"Could not get description for {product_id}: {desc_error}")
            
        return product_data


# Singleton instance
_meli_service: Optional[MeliService] = None


def get_meli_service() -> MeliService:
    """
    Get or create MeLi service singleton instance.
    
    Returns:
        MeliService instance
    """
    global _meli_service
    if _meli_service is None:
        _meli_service = MeliService()
    return _meli_service


# Convenience functions for backward compatibility
def make_authenticated_request(
    method: str, 
    endpoint: str, 
    **kwargs
) -> requests.Response:
    """
    Make authenticated request to MercadoLibre API.
    
    Args:
        method: HTTP method
        endpoint: API endpoint
        **kwargs: Additional request arguments
        
    Returns:
        Response object
    """
    service = get_meli_service()
    return service.request(method, endpoint, **kwargs)
