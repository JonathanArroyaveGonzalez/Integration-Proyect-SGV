"""MercadoLibre API service for centralized authentication and requests."""

import logging
from typing import Dict, Any, Optional
from functools import wraps
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

#from setting.config_db import MeliConfigRepository
from project.config_db.repository import MeliConfigRepository

logger = logging.getLogger(__name__)


class MeliService:
    """Service for MercadoLibre API interactions with automatic token refresh."""
    
    BASE_URL = "https://api.mercadolibre.com"
    TOKEN_URL = "https://api.mercadolibre.com/oauth/token"
    
    def __init__(self):
        """Initialize MeLi service with repository and session."""
        self.repo = MeliConfigRepository()
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
    
    def _refresh_token(self) -> Dict[str, str]:
        """
        Refresh the access token using refresh token.
        
        Returns:
            Dict with new access_token and refresh_token
            
        Raises:
            RuntimeError: If refresh fails
        """
        try:
            tokens = self._get_tokens()
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
            
            logger.info("Token refreshed successfully")
            return {
                'access_token': new_access_token,
                'refresh_token': new_refresh_token
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Token refresh failed: {str(e)}")
            raise RuntimeError(f"Token refresh failed: {str(e)}")
    
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
            RuntimeError: If request fails after retry
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
        
        response = self.session.request(method, url, **kwargs)
        
        # If unauthorized and auto_refresh is enabled, try refreshing token
        if response.status_code == 401 and auto_refresh:
            logger.info("Received 401, refreshing token and retrying...")
            
            try:
                new_tokens = self._refresh_token()
                
                # Retry with new token
                kwargs['headers'] = self._get_headers(new_tokens['access_token'])
                response = self.session.request(method, url, **kwargs)
                
            except Exception as e:
                logger.error(f"Token refresh failed: {str(e)}")
                # Return original 401 response if refresh fails
        
        return response
    
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
