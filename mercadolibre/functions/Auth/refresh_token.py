"""Dependencies"""

import requests
import logging

from mercadolibre.functions.Auth.mongo_config import get_meli_config, update_meli_tokens

logger = logging.getLogger(__name__)


def refresh_meli_tokens():
    """
    This function refreshes the MercadoLibre access_token and refresh_token
    using the current refresh_token from the database
    """
    try:
        # Get current configuration from MongoDB
        config = get_meli_config()
        
        if not config:
            raise Exception("MercadoLibre configuration not found in database")

        # Validate required fields
        required_fields = ['client_id', 'client_secret', 'refresh_token']
        missing_fields = []
        
        for field in required_fields:
            if not config.get(field):
                missing_fields.append(field)
        
        if missing_fields:
            raise Exception(f"Missing required configuration fields: {', '.join(missing_fields)}")

        # Prepare the data for the token refresh request
        data = {
            "grant_type": "refresh_token",  # Fixed: always use "refresh_token" for token refresh
            "client_id": config["client_id"],
            "client_secret": config["client_secret"],
            "refresh_token": config["refresh_token"],
        }

        # Headers for the request
        headers = {
            "accept": "application/json",
            "content-type": "application/x-www-form-urlencoded",
        }

        logger.info("Attempting to refresh MercadoLibre tokens...")

        # Make the POST request to MercadoLibre OAuth endpoint
        response = requests.post(
            "https://api.mercadolibre.com/oauth/token",
            data=data,
            headers=headers,
            timeout=30,
        )

        logger.info(f"MercadoLibre API response status: {response.status_code}")

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the response
            token_data = response.json()
            logger.info("Successfully received new tokens from MercadoLibre")

            # Extract the new tokens
            new_access_token = token_data.get("access_token")
            new_refresh_token = token_data.get("refresh_token")

            if new_access_token and new_refresh_token:
                # Update the tokens in MongoDB
                logger.info("Updating tokens in database...")
                update_success = update_meli_tokens(new_access_token, new_refresh_token)

                if update_success:
                    logger.info("Tokens successfully updated in database")
                    return {
                        "success": True,
                        "message": "Tokens refreshed successfully",
                        "access_token": new_access_token,
                        "refresh_token": new_refresh_token,
                        "expires_in": token_data.get("expires_in"),
                        "token_type": token_data.get("token_type", "Bearer"),
                    }
                else:
                    raise Exception("Failed to update tokens in database")
            else:
                missing = []
                if not new_access_token:
                    missing.append("access_token")
                if not new_refresh_token:
                    missing.append("refresh_token")
                raise Exception(f"Invalid response from MercadoLibre: missing {', '.join(missing)}")
        else:
            # Handle error responses
            logger.error(f"MercadoLibre API error: {response.status_code}")
            try:
                error_data = response.json()
                error_message = error_data.get("message", error_data.get("error_description", f"HTTP {response.status_code}"))
                logger.error(f"Error details: {error_data}")
            except Exception:
                error_message = f"HTTP {response.status_code}: {response.text}"

            raise Exception(f"MercadoLibre API error: {error_message}")

    except requests.exceptions.Timeout:
        raise Exception("Request timeout while refreshing tokens")
    except requests.exceptions.ConnectionError:
        raise Exception("Connection error while refreshing tokens")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Request error: {str(e)}")
    except Exception as e:
        raise Exception(f"Error refreshing MercadoLibre tokens: {str(e)}")
