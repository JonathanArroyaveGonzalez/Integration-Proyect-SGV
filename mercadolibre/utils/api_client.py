"""
Utility functions for MercadoLibre API authentication
"""

import logging
<<<<<<< HEAD
from mercadolibre.functions.auth.mongo_config import get_meli_config
from mercadolibre.functions.auth.refresh_token import refresh_meli_tokens

logger = logging.getLogger(__name__)
=======
from mercadolibre.functions.Auth.mongo_config import get_meli_config
from mercadolibre.functions.Auth.refresh_token import refresh_meli_tokens
>>>>>>> d8a9700292ac06f9dc5397dd451ec27b8963ffbe

logger = logging.getLogger(__name__)


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
        access_token = config.get("access_token")

        if not access_token:
            # Try to refresh tokens if no access token is found
            logger.info("No access token found, attempting to refresh...")
            refresh_result = refresh_meli_tokens()
<<<<<<< HEAD

            if refresh_result.get("success"):
                return refresh_result.get("access_token")
            else:
                raise Exception("No access token found and refresh failed")

=======
            
            if refresh_result.get('success'):
                return refresh_result.get('access_token')
            else:
                raise Exception("No access token found and refresh failed")
            
>>>>>>> d8a9700292ac06f9dc5397dd451ec27b8963ffbe
        return access_token

    except Exception as e:
        # Add more detailed error logging
        error_msg = f"Error getting valid access token: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)


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
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    except Exception as e:
        raise Exception(f"Error getting auth headers: {str(e)}")


def make_authenticated_request(method, url, max_retries=1, **kwargs):
    """
    Make an authenticated request to MercadoLibre API with automatic token refresh
<<<<<<< HEAD

=======
    
>>>>>>> d8a9700292ac06f9dc5397dd451ec27b8963ffbe
    Args:
        method (str): HTTP method (GET, POST, PUT, DELETE)
        url (str): API endpoint URL
        max_retries (int): Maximum number of retry attempts for token refresh
        **kwargs: Additional arguments for requests

    Returns:
        requests.Response: Response object

    Raises:
        Exception: If request fails after all retries
    """
    import requests
<<<<<<< HEAD

    last_exception = None

=======
    
    last_exception = None
    
>>>>>>> d8a9700292ac06f9dc5397dd451ec27b8963ffbe
    for attempt in range(max_retries + 1):
        try:
            # Get authentication headers
            headers = get_auth_headers()
<<<<<<< HEAD

            # Merge with any additional headers
            if "headers" in kwargs:
                headers.update(kwargs["headers"])

            kwargs["headers"] = headers

            # Make the request
            response = requests.request(method, url, **kwargs)

            # Check if token might be expired (401 Unauthorized)
            if response.status_code == 401 and attempt < max_retries:
                logger.warning(
                    f"Received 401 Unauthorized, attempting token refresh (attempt {attempt + 1}/{max_retries})"
                )

                # Try to refresh the token
                try:
                    refresh_result = refresh_meli_tokens()

                    if refresh_result.get("success"):
=======
            
            # Merge with any additional headers
            if 'headers' in kwargs:
                headers.update(kwargs['headers'])
            
            kwargs['headers'] = headers
            
            # Make the request
            response = requests.request(method, url, **kwargs)
            
            # Check if token might be expired (401 Unauthorized)
            if response.status_code == 401 and attempt < max_retries:
                logger.warning(f"Received 401 Unauthorized, attempting token refresh (attempt {attempt + 1}/{max_retries})")
                
                # Try to refresh the token
                try:
                    refresh_result = refresh_meli_tokens()
                    
                    if refresh_result.get('success'):
>>>>>>> d8a9700292ac06f9dc5397dd451ec27b8963ffbe
                        logger.info("Token refreshed successfully, retrying request...")
                        continue  # Retry the loop with new token
                    else:
                        raise Exception(f"Token refresh unsuccessful: {refresh_result}")
<<<<<<< HEAD

=======
                        
>>>>>>> d8a9700292ac06f9dc5397dd451ec27b8963ffbe
                except Exception as refresh_error:
                    logger.error(f"Token refresh failed: {str(refresh_error)}")
                    if attempt == max_retries - 1:  # Last attempt
                        raise Exception(f"Token refresh failed: {str(refresh_error)}")
                    continue
<<<<<<< HEAD

            # If we get here, the request was made (successfully or not)
            return response

        except Exception as e:
            last_exception = e
            logger.error(f"Request attempt {attempt + 1} failed: {str(e)}")

            # If this is the last attempt, raise the exception
            if attempt == max_retries:
                break

    # If we get here, all attempts failed
    raise Exception(
        f"Error making authenticated request after {max_retries + 1} attempts: {str(last_exception)}"
    )
=======
            
            # If we get here, the request was made (successfully or not)
            return response
            
        except Exception as e:
            last_exception = e
            logger.error(f"Request attempt {attempt + 1} failed: {str(e)}")
            
            # If this is the last attempt, raise the exception
            if attempt == max_retries:
                break
    
    # If we get here, all attempts failed
    raise Exception(f"Error making authenticated request after {max_retries + 1} attempts: {str(last_exception)}")
>>>>>>> d8a9700292ac06f9dc5397dd451ec27b8963ffbe


def get_meli_api_base_url():
    """
    Get the base URL for MercadoLibre API

    Returns:
        str: Base URL
    """
    try:
        config = get_meli_config()
<<<<<<< HEAD
        return config.get("api_base_url", "https://api.mercadolibre.com/")
    except Exception as e:
        logger.warning(
            f"Could not get API base URL from config, using default: {str(e)}"
        )
        return "https://api.mercadolibre.com/"
=======
        return config.get('api_base_url', 'https://api.mercadolibre.com/')
    except Exception as e:
        logger.warning(f"Could not get API base URL from config, using default: {str(e)}")
        return 'https://api.mercadolibre.com/'
>>>>>>> d8a9700292ac06f9dc5397dd451ec27b8963ffbe
