"""Dependencies"""

import requests

from mercadolibre.functions.auth.mongo_config import get_meli_config, update_meli_tokens


def refresh_meli_tokens():
    """
    This function refreshes the MercadoLibre access_token and refresh_token
    using the current refresh_token from the database
    """
    try:
        # Get current configuration from MongoDB
        config = get_meli_config()

        # Prepare the data for the token refresh request
        data = {
            "grant_type": config["grant_type"],
            "client_id": config["client_id"],
            "client_secret": config["client_secret"],
            "refresh_token": config["refresh_token"],
        }

        # Headers for the request
        headers = {
            "accept": "application/json",
            "content-type": "application/x-www-form-urlencoded",
        }

        # Make the POST request to MercadoLibre OAuth endpoint
        response = requests.post(
            "https://api.mercadolibre.com/oauth/token",
            data=data,
            headers=headers,
            timeout=30,
        )

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the response
            token_data = response.json()

            # Extract the new tokens
            new_access_token = token_data.get("access_token")
            new_refresh_token = token_data.get("refresh_token")

            if new_access_token and new_refresh_token:
                # Update the tokens in MongoDB
                update_success = update_meli_tokens(new_access_token, new_refresh_token)

                if update_success:
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
                raise Exception("Invalid response from MercadoLibre: missing tokens")
        else:
            # Handle error responses
            try:
                error_data = response.json()
                error_message = error_data.get(
                    "message", f"HTTP {response.status_code}"
                )
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
