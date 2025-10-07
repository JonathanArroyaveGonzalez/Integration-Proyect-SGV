"""Internal API service for centralized project endpoint requests."""

import logging
from typing import Dict, Any, Optional, Union
from urllib.parse import urljoin
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from django.conf import settings

logger = logging.getLogger(__name__)


class InternalAPIService:
    """Service for internal API requests with session management and auth forwarding."""

    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize internal API service.

        Args:
            base_url: Override base URL, defaults to settings.WMS_BASE_URL
        """
        self.base_url = self._get_base_url(base_url)
        self._session = None
        self._setup_session()

    def _get_base_url(self, override_url: Optional[str] = None) -> str:
        """
        Get base URL for internal API.

        Args:
            override_url: Optional URL to override settings

        Returns:
            Base URL string
        """
        if override_url:
            return override_url.rstrip("/")

        return getattr(settings, "WMS_BASE_URL", "http://localhost:8000").rstrip("/")

    def _setup_session(self):
        """Configure requests session with connection pooling and retry strategy."""
        self._session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.3,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=[
                "HEAD",
                "GET",
                "PUT",
                "DELETE",
                "OPTIONS",
                "TRACE",
                "POST",
            ],
        )

        # Configure adapter with connection pooling
        adapter = HTTPAdapter(
            pool_connections=10, pool_maxsize=20, max_retries=retry_strategy
        )

        self._session.mount("http://", adapter)
        self._session.mount("https://", adapter)

        # Set default timeout
        self._session.timeout = (3, 10)  # (connect, read) timeout

        # Keep-alive headers
        self._session.headers.update(
            {
                "Connection": "keep-alive",
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )

    @property
    def session(self) -> requests.Session:
        """Get or create session instance."""
        if self._session is None:
            self._setup_session()
        return self._session

    def extract_authorization(
        self, request_or_headers: Union[Dict, Any]
    ) -> Optional[str]:
        """
        Extract authorization token from request or headers.

        Args:
            request_or_headers: Django request object or headers dict

        Returns:
            Authorization header value or None
        """
        # If it's a dictionary (headers)
        if isinstance(request_or_headers, dict):
            return request_or_headers.get("Authorization") or request_or_headers.get(
                "authorization"
            )

        # If it's a Django request object
        if hasattr(request_or_headers, "headers"):
            return request_or_headers.headers.get("Authorization")

        # Try META for Django request
        if hasattr(request_or_headers, "META"):
            auth = request_or_headers.META.get("HTTP_AUTHORIZATION")
            if auth:
                return auth

        return None

    def build_url(self, endpoint: str) -> str:
        """
        Build complete URL from endpoint.

        Args:
            endpoint: API endpoint path

        Returns:
            Complete URL
        """
        # Remove leading slash if present
        endpoint = endpoint.lstrip("/")
        return urljoin(self.base_url + "/", endpoint)

    def forward_request(
        self,
        method: str,
        endpoint: str,
        original_request: Any = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> requests.Response:
        """
        Forward a request to internal API with authentication.

        Args:
            method: HTTP method
            endpoint: API endpoint
            original_request: Original Django request to extract auth from
            headers: Additional headers to include
            **kwargs: Additional arguments for requests

        Returns:
            Response object
        """
        # Build complete URL
        url = self.build_url(endpoint)

        # Prepare headers
        request_headers = {}

        # Extract authorization from original request if provided
        if original_request:
            auth = self.extract_authorization(original_request)
            if auth:
                request_headers["Authorization"] = auth

        # Merge with additional headers
        if headers:
            request_headers.update(headers)

        # Set headers in kwargs
        if request_headers:
            kwargs["headers"] = request_headers

        # Set timeout if not specified
        if "timeout" not in kwargs:
            kwargs["timeout"] = self.session.timeout

        # Log the request
        logger.debug(f"Internal API {method} request to: {url}")

        try:
            response = self.session.request(method, url, **kwargs)

            # Log response status
            logger.debug(f"Internal API response: {response.status_code}")

            return response

        except requests.exceptions.Timeout:
            logger.error(f"Timeout calling internal API: {method} {url}")
            raise
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error calling internal API: {method} {url}")
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error calling internal API: {method} {url} - {str(e)}"
            )
            raise

    def get(
        self, endpoint: str, original_request: Any = None, **kwargs
    ) -> requests.Response:
        """Make GET request to internal API."""
        return self.forward_request("GET", endpoint, original_request, **kwargs)

    def post(
        self, endpoint: str, original_request: Any = None, **kwargs
    ) -> requests.Response:
        """Make POST request to internal API."""
        return self.forward_request("POST", endpoint, original_request, **kwargs)

    def put(
        self, endpoint: str, original_request: Any = None, **kwargs
    ) -> requests.Response:
        """Make PUT request to internal API."""
        return self.forward_request("PUT", endpoint, original_request, **kwargs)

    def patch(
        self, endpoint: str, original_request: Any = None, **kwargs
    ) -> requests.Response:
        """Make PATCH request to internal API."""
        return self.forward_request("PATCH", endpoint, original_request, **kwargs)

    def delete(
        self, endpoint: str, original_request: Any = None, **kwargs
    ) -> requests.Response:
        """Make DELETE request to internal API."""
        return self.forward_request("DELETE", endpoint, original_request, **kwargs)

    def close(self):
        """Close the session and free resources."""
        if self._session:
            self._session.close()
            self._session = None


# Singleton instance
_internal_api_service: Optional[InternalAPIService] = None


def get_internal_api_service(base_url: Optional[str] = None) -> InternalAPIService:
    """
    Get or create internal API service singleton.

    Args:
        base_url: Optional base URL override

    Returns:
        InternalAPIService instance
    """
    global _internal_api_service

    if _internal_api_service is None or (
        base_url and base_url != _internal_api_service.base_url
    ):
        _internal_api_service = InternalAPIService(base_url)

    return _internal_api_service


# Convenience function for backward compatibility
def forward_authenticated_request(
    method: str, endpoint: str, original_request: Any = None, **kwargs
) -> requests.Response:
    """
    Forward authenticated request to internal API.

    Args:
        method: HTTP method
        endpoint: API endpoint
        original_request: Original Django request
        **kwargs: Additional request arguments

    Returns:
        Response object
    """
    service = get_internal_api_service()
    return service.forward_request(method, endpoint, original_request, **kwargs)
