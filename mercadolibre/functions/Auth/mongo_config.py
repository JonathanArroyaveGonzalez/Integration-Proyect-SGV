"""Dependencies"""

from dotenv import load_dotenv
from project.config_db import MeliConfigRepository

load_dotenv()

# Initialize the repository
config_repository = MeliConfigRepository()


def get_meli_config():
    """
    This function returns the MercadoLibre configuration from MongoDB
    using the new MeliConfigRepository service
    """
    try:
        config = config_repository.get_config()
        return config.to_dict() if config else None
    except Exception as e:
        raise Exception(f"Error getting MercadoLibre configuration: {str(e)}")
    

def get_meli_user_account_id():
    """
    This function returns the user account ID from MongoDB
    using the new MeliConfigRepository service
    """
    try:
        return config_repository.get_user_account_id()
    except Exception as e:
        raise Exception(f"Error getting MercadoLibre user account ID: {str(e)}")


def get_meli_tokens():
    """
    This function returns the access_token and refresh_token from MongoDB
    using the new MeliConfigRepository service
    """
    try:
        return config_repository.get_tokens()
    except Exception as e:
        raise Exception(f"Error getting MercadoLibre tokens: {str(e)}")


def update_meli_tokens(access_token, refresh_token):
    """
    This function updates the access_token and refresh_token in MongoDB
    using the new MeliConfigRepository service
    """
    try:
        result = config_repository.update_tokens(access_token, refresh_token)
        if result:
            return True
        else:
            raise Exception("No document was updated - tokens may be the same")
    except Exception as e:
        raise Exception(f"Error updating MercadoLibre tokens: {str(e)}")


def update_meli_config(config_data):
    """
    This function updates partial MercadoLibre configuration in MongoDB
    using the new MeliConfigRepository service
    
    Args:
        config_data: Dictionary with fields to update
    """
    try:
        result = config_repository.update_config(config_data)
        if result:
            return True
        else:
            raise Exception("No document was updated")
    except Exception as e:
        raise Exception(f"Error updating MercadoLibre configuration: {str(e)}")


def upsert_full_meli_config(user_account_id, access_token, refresh_token, 
                           client_id=None, client_secret=None, redirect_uri=None):
    """
    This function inserts or updates complete MercadoLibre configuration in MongoDB
    using the new MeliConfigRepository service
    """
    try:
        from project.config_db.models import MeliConfig
        
        config = MeliConfig(
            user_account_id=user_account_id,
            access_token=access_token,
            refresh_token=refresh_token,
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri
        )
        
        result = config_repository.upsert_full_config(config)
        if result:
            return True
        else:
            raise Exception("Failed to upsert configuration")
    except Exception as e:
        raise Exception(f"Error upserting MercadoLibre configuration: {str(e)}")
