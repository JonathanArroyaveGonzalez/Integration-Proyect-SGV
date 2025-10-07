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
    MeliError,
    MeliAuthError,
    MeliNotFoundError,
    MeliBadRequestError,
    MeliRateLimitError,
    MeliServerError,
)

logger = logging.getLogger(__name__)


# -------------------------------------------------------------------
# Decoradores
# -------------------------------------------------------------------
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


# -------------------------------------------------------------------
# Clase principal del servicio
# -------------------------------------------------------------------
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
        tokens = self.repo.get_tokens()
        if not tokens:
            raise RuntimeError("No tokens found in database")
        return tokens

    def _refresh_token(
        self, current_tokens: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        try:
            tokens = current_tokens or self._get_tokens()
            config = self.repo.get_config()

            if not config or not config.client_id or not config.client_secret:
                raise RuntimeError("Missing client credentials for token refresh")

            payload = {
                "grant_type": "refresh_token",
                "client_id": config.client_id,
                "client_secret": config.client_secret,
                "refresh_token": tokens["refresh_token"],
            }

            response = self.session.post(self.TOKEN_URL, data=payload)
            response.raise_for_status()

            data = response.json()
            new_access_token = data["access_token"]
            new_refresh_token = data["refresh_token"]

            # Update tokens in database
            self.repo.update_tokens(new_access_token, new_refresh_token)

            logger.info(
                "Token refreshed successfully", extra={"request_id": self.request_id}
            )
            return {
                "access_token": new_access_token,
                "refresh_token": new_refresh_token,
            }

        except requests.exceptions.RequestException as e:
            logger.error(
                f"Token refresh failed: {str(e)}", extra={"request_id": self.request_id}
            )
            raise RuntimeError(f"Token refresh failed: {str(e)}")

    def _handle_api_error(self, response: requests.Response) -> None:
        error_data = {}
        try:
            error_data = response.json()
        except Exception:
            error_data = {"message": response.text}

        message = error_data.get("message", "Unknown error")

        if response.status_code in (401, 403):
            raise MeliAuthError(
                message, status_code=response.status_code, response_data=error_data
            )
        elif response.status_code == 404:
            raise MeliNotFoundError(
                message, status_code=response.status_code, response_data=error_data
            )
        elif response.status_code == 400:
            raise MeliBadRequestError(
                message, status_code=response.status_code, response_data=error_data
            )
        elif response.status_code == 429:
            raise MeliRateLimitError(
                message, status_code=response.status_code, response_data=error_data
            )
        elif response.status_code >= 500:
            raise MeliServerError(
                message, status_code=response.status_code, response_data=error_data
            )
        else:
            raise MeliError(
                message, status_code=response.status_code, response_data=error_data
            )

    def _log_request(self, method: str, endpoint: str, **kwargs) -> None:
        logger.info(
            f"API Request: {method} {endpoint}",
            extra={
                "request_id": self.request_id,
                "method": method,
                "endpoint": endpoint,
                "params": kwargs.get("params"),
                "headers": {
                    k: v
                    for k, v in kwargs.get("headers", {}).items()
                    if k.lower() != "authorization"
                },
            },
        )

    def _get_headers(self, access_token: str) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    @retry_on_rate_limit()
    def request(
        self, method: str, endpoint: str, auto_refresh: bool = True, **kwargs
    ) -> requests.Response:
        if not endpoint.startswith("/"):
            endpoint = f"/{endpoint}"

        url = f"{self.BASE_URL}{endpoint}"
        tokens = self._get_tokens()

        headers = self._get_headers(tokens["access_token"])
        if "headers" in kwargs:
            headers.update(kwargs["headers"])
        kwargs["headers"] = headers

        self._log_request(method, endpoint, **kwargs)

        try:
            response = self.session.request(method, url, **kwargs)

            if response.status_code == 401 and auto_refresh:
                logger.info(
                    "Token expired, refreshing...",
                    extra={"request_id": self.request_id},
                )
                new_tokens = self._refresh_token(current_tokens=tokens)
                kwargs["headers"] = self._get_headers(new_tokens["access_token"])
                response = self.session.request(method, url, **kwargs)

            if response.status_code != 200:
                self._handle_api_error(response)

            return response

        except requests.exceptions.RequestException as e:
            logger.error(
                f"Request failed: {str(e)}", extra={"request_id": self.request_id}
            )
            raise MeliError(f"Request failed: {str(e)}")

    # Métodos convenientes
    def get(self, endpoint: str, **kwargs) -> requests.Response:
        return self.request("GET", endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs) -> requests.Response:
        return self.request("POST", endpoint, **kwargs)

    def put(self, endpoint: str, **kwargs) -> requests.Response:
        return self.request("PUT", endpoint, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        return self.request("DELETE", endpoint, **kwargs)

    # -------------------
    # Funciones de negocio
    # -------------------
    def get_customer(self, customer_id: str) -> Dict[str, Any]:
        response = self.get(f"/users/{customer_id}")
        if response.status_code != 200:
            response.raise_for_status()
        return response.json()

    def get_user_products(self, user_id: str) -> List[str]:
        response = self.get(f"/users/{user_id}/items/search")
        if response.status_code != 200:
            response.raise_for_status()
        return response.json().get("results", [])

    def get_product_description(self, product_id: str) -> Optional[Dict[str, Any]]:
        try:
            response = self.get(f"/items/{product_id}/description")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception:
            return None

    def _get_batch_products(self, batch_ids: List[str]) -> List[Dict[str, Any]]:
        ids_param = ",".join(batch_ids)
        response = self.get("/items", params={"ids": ids_param})
        if response.status_code == 200:
            result = response.json()
            return [
                item["body"]
                for item in result
                if item.get("code") == 200 and isinstance(item.get("body"), dict)
            ]
        else:
            response.raise_for_status()
        return []

    def get_products_batch(self, product_ids: List[str]) -> List[Dict[str, Any]]:
        if not product_ids:
            return []

        products = []
        from concurrent.futures import ThreadPoolExecutor, as_completed

        for i in range(0, len(product_ids), 20):
            batch = product_ids[i : i + 20]
            batch_products = self._get_batch_products(batch)

            with ThreadPoolExecutor(max_workers=5) as executor:
                future_to_product = {
                    executor.submit(
                        self.get_product_description, product["id"]
                    ): product
                    for product in batch_products
                    if "id" in product
                }

                for future in as_completed(future_to_product):
                    product = future_to_product[future]
                    try:
                        description = future.result()
                        if description:
                            product["description_data"] = description
                    except Exception:
                        pass

            products.extend(batch_products)

        return products

    def get_product(self, product_id: str) -> Dict[str, Any]:
        response = self.get(f"/items/{product_id}")
        if response.status_code != 200:
            response.raise_for_status()
        product_data = response.json()

        try:
            desc_response = self.get(f"/items/{product_id}/description")
            if desc_response.status_code == 200:
                product_data["description_data"] = desc_response.json()
        except Exception:
            pass

        return product_data

    # Order-related methods

    def get_order(self, order_id: str) -> Dict[str, Any]:
        """
        Get order information from MercadoLibre.

        Args:
            order_id: MercadoLibre order ID

        Returns:
            Order data dictionary

        Raises:
            requests.exceptions.RequestException: If API request fails
        """
        response = self.get(f"/orders/{order_id}")
        if response.status_code != 200:
            logger.error(f"Failed to get order {order_id}: {response.status_code}")
            response.raise_for_status()
        return response.json()

    def get_orders_batch(self, order_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Get detailed information for multiple orders.

        Args:
            order_ids: List of order IDs

        Returns:
            List of order details dictionaries

        Raises:
            requests.exceptions.RequestException: If API request fails
        """
        if not order_ids:
            return []

        orders = []
        from concurrent.futures import ThreadPoolExecutor, as_completed

        # Process orders in parallel
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_order = {
                executor.submit(self.get_order, order_id): order_id
                for order_id in order_ids
            }

            for future in as_completed(future_to_order):
                order_id = future_to_order[future]
                try:
                    order_data = future.result()
                    orders.append(order_data)
                except Exception as e:
                    logger.error(f"Error getting order {order_id}: {e}")

        return orders

    def get_user_orders(
        self, user_id: str, status: Optional[str] = None, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get orders for a specific user (seller).

        Args:
            user_id: MercadoLibre user ID
            status: Optional order status filter (paid, cancelled, etc.)
            limit: Maximum number of orders to retrieve

        Returns:
            List of order dictionaries

        Raises:
            requests.exceptions.RequestException: If API request fails
        """
        params = {"seller": user_id, "limit": limit}

        if status:
            params["order.status"] = status

        response = self.get("/orders/search", params=params)
        if response.status_code != 200:
            logger.error(
                f"Failed to get orders for user {user_id}: {response.status_code}"
            )
            response.raise_for_status()

        data = response.json()
        return data.get("results", [])


# -------------------------------------------------------------------
# Singleton y funciones auxiliares
# -------------------------------------------------------------------
_meli_service: Optional[MeliService] = None


def get_meli_service() -> MeliService:
    global _meli_service
    if _meli_service is None:
        _meli_service = MeliService()
    return _meli_service


def make_authenticated_request(
    method: str, endpoint: str, **kwargs
) -> requests.Response:
    service = get_meli_service()
    return service.request(method, endpoint, **kwargs)


# -------------------------------------------------------------------
# Helper para usuarios
# -------------------------------------------------------------------
class FetchUser:
    """Helper class to fetch user data from MercadoLibre."""

    @staticmethod
    def fetch_user(user_id: str, meli_client: Optional[MeliService] = None):
        meli = get_meli_service()
        try:
            response = meli.get(f"/users/{user_id}")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.exception(f"Error fetching user {user_id}: {e}")
            return None
