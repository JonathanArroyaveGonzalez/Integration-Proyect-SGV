"""Dependencies"""

from dotenv import load_dotenv
from project.mongodb_service import mongodb_service

load_dotenv()


def get_meli_config():
    """
    This function returns the MercadoLibre configuration from MongoDB
    """
    try:
        return mongodb_service.get_meli_config()
    except Exception as e:
        raise Exception(f"Error getting MercadoLibre configuration: {str(e)}")


def update_meli_tokens(access_token, refresh_token):
    """
    This function updates the access_token and refresh_token in MongoDB
    """
    try:
        result = mongodb_service.update_meli_tokens(access_token, refresh_token)
        if result:
            return True
        else:
            raise Exception("No document was updated")
    except Exception as e:
        raise Exception(f"Error updating MercadoLibre tokens: {str(e)}")