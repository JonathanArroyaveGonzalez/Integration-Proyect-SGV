"""Repository for MercadoLibre configuration operations."""

from typing import Optional, Dict, Any
from .connection import mongo_connection
from .models import MeliConfig


class MeliConfigRepository:
    """Repository for MercadoLibre configuration CRUD operations."""
    
    COLLECTION_NAME = "meli_config"
    CONFIG_FIELD = "meli_config"
    
    def __init__(self):
        """Initialize repository with database connection."""
        self.db = mongo_connection.get_database()
        self.collection = self.db[self.COLLECTION_NAME]
    
    def get_config(self) -> Optional[MeliConfig]:
        """
        Get MercadoLibre configuration.
        
        Returns:
            MeliConfig or None if not found
        """
        try:
            document = self.collection.find_one({})
            if document and self.CONFIG_FIELD in document:
                return MeliConfig.from_dict(document[self.CONFIG_FIELD])
            return None
        except Exception as e:
            raise RuntimeError(f"Failed to get MercadoLibre configuration: {str(e)}")
    
    def get_user_account_id(self) -> Optional[str]:
        """
        Get MercadoLibre user account ID.
        
        Returns:
            str or None if not found
        """
        config = self.get_config()
        return config.user_account_id if config else None
    
    def get_tokens(self) -> Optional[Dict[str, str]]:
        """
        Get MercadoLibre access and refresh tokens.
        
        Returns:
            dict with 'access_token' and 'refresh_token' or None
        """
        config = self.get_config()
        if config:
            return {
                'access_token': config.access_token,
                'refresh_token': config.refresh_token
            }
        return None
    
    def update_tokens(self, access_token: str, refresh_token: str) -> bool:
        """
        Update MercadoLibre tokens.
        
        Args:
            access_token: New access token
            refresh_token: New refresh token
            
        Returns:
            True if updated successfully, False otherwise
        """
        try:
            result = self.collection.update_one(
                {},
                {
                    "$set": {
                        f"{self.CONFIG_FIELD}.access_token": access_token,
                        f"{self.CONFIG_FIELD}.refresh_token": refresh_token
                    }
                },
                upsert=True
            )
            return result.modified_count > 0 or result.upserted_id is not None
        except Exception as e:
            raise RuntimeError(f"Failed to update tokens: {str(e)}")
    
    def update_config(self, config_data: Dict[str, Any]) -> bool:
        """
        Update partial MercadoLibre configuration.
        
        Args:
            config_data: Dictionary with fields to update
            
        Returns:
            True if updated successfully, False otherwise
        """
        try:
            update_dict = {
                f"{self.CONFIG_FIELD}.{key}": value 
                for key, value in config_data.items()
            }
            
            result = self.collection.update_one(
                {},
                {"$set": update_dict},
                upsert=True
            )
            return result.modified_count > 0 or result.upserted_id is not None
        except Exception as e:
            raise RuntimeError(f"Failed to update configuration: {str(e)}")
    
    def upsert_full_config(self, config: MeliConfig) -> bool:
        """
        Insert or update complete MercadoLibre configuration.
        
        Args:
            config: MeliConfig instance
            
        Returns:
            True if operation was successful
        """
        try:
            result = self.collection.update_one(
                {},
                {"$set": {self.CONFIG_FIELD: config.to_dict()}},
                upsert=True
            )
            return result.modified_count > 0 or result.upserted_id is not None
        except Exception as e:
            raise RuntimeError(f"Failed to upsert configuration: {str(e)}")
