"""
Utility functions for MercadoLibre API authentication
"""


from mercadolibre.functions.auth.mongo_config import get_meli_config
from mercadolibre.functions.auth.refresh_token import refresh_meli_tokens


def get_valid_access_token():
    """
    Get a valid access token for MercadoLibre API calls.
    This function will return the current token or refresh it if needed.

    Returns:
        str: Valid access token

    Raises:
        Exception: If unable to get or refresh the token
    """
    try:
        config = get_meli_config()
        access_token = config.get('access_token')

        if not access_token:
            raise Exception("No access token found in configuration")

        return access_token

    except Exception as e:
        raise Exception(f"Error getting valid access token: {str(e)}")


def get_auth_headers():
    """
    Get authentication headers for MercadoLibre API calls

    Returns:
        dict: Headers dictionary with Authorization

    Raises:
        Exception: If unable to get valid token
    """
    try:
        access_token = get_valid_access_token()

        return {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    except Exception as e:
        raise Exception(f"Error getting auth headers: {str(e)}")


def make_authenticated_request(method, url, **kwargs):
    """
    Make an authenticated request to MercadoLibre API

    Args:
        method (str): HTTP method (GET, POST, PUT, DELETE)
        url (str): API endpoint URL
        **kwargs: Additional arguments for requests

    Returns:
        requests.Response: Response object

    Raises:
        Exception: If request fails
    """
    import requests

    try:
        # Get authentication headers
        headers = get_auth_headers()

        # Merge with any additional headers
        if 'headers' in kwargs:
            headers.update(kwargs['headers'])

        kwargs['headers'] = headers

        # Make the request
        response = requests.request(method, url, **kwargs)

        # Check if token might be expired (401 Unauthorized)
        if response.status_code == 401:
            # Try to refresh the token once
            try:
                refresh_result = refresh_meli_tokens()

                if refresh_result.get('success'):
                    # Update headers with new token
                    headers = get_auth_headers()
                    kwargs['headers'] = headers

                    # Retry the request
                    response = requests.request(method, url, **kwargs)

            except Exception as refresh_error:
                raise Exception(f"Token refresh failed: {str(refresh_error)}")

        return response

    except Exception as e:
        raise Exception(f"Error making authenticated request: {str(e)}")


def get_meli_api_base_url():
    """
    Get the base URL for MercadoLibre API

    Returns:
        str: Base URL
    """
    try:
        config = get_meli_config()
        return config.get('api_base_url', 'https://api.mercadolibre.com/')
    except Exception:
        return 'https://api.mercadolibre.com/'
