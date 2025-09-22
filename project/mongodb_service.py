"""
Centralized MongoDB Service for the project.

This module provides a singleton service for MongoDB operations,
centralizing connection management and common database operations.
"""

import os
from threading import Lock
from typing import Dict, List, Any, Optional
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from dotenv import load_dotenv

load_dotenv()


class MongoDBService:
    """
    Singleton MongoDB service for centralized database operations.
    
    This service handles:
    - Connection management
    - Database and collection access
    - Common CRUD operations
    - Configuration management
    """
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(MongoDBService, cls).__new__(cls)
                    cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the MongoDB service with connection and database setup."""
        try:
            self.apidbmongo = os.getenv("APIDBMONGO")
            if not self.apidbmongo:
                raise RuntimeError("Could not find APIDBMONGO in environment")
            
            # Get CONNECTION_STRING directly from environment to avoid circular import
            self.connection_string = os.getenv("DATABASE_URL")
            if not self.connection_string:
                raise RuntimeError("Could not find DATABASE_URL in environment")
                
            self.client: Optional[MongoClient] = None
            self.db: Optional[Database] = None
            self._connect()
            
        except Exception as e:
            raise RuntimeError(f"Failed to initialize MongoDB service: {str(e)}")
    
    def _connect(self):
        """Establish connection to MongoDB."""
        try:
            self.client = MongoClient(self.connection_string)
            self.db = self.client[self.apidbmongo]
        except Exception as e:
            raise RuntimeError(f"Failed to connect to MongoDB: {str(e)}")
    
    def get_client(self) -> MongoClient:
        """Get the MongoDB client."""
        if self.client is None:
            self._connect()
        return self.client
    
    def get_database(self) -> Database:
        """Get the current database."""
        if self.db is None:
            self._connect()
        return self.db
    
    def get_collection(self, collection_name: str) -> Collection:
        """Get a specific collection."""
        return self.get_database()[collection_name]
    
    def list_collections(self) -> List[str]:
        """Get list of all collection names in the database."""
        try:
            return self.get_database().list_collection_names()
        except Exception as e:
            raise RuntimeError(f"Failed to list collections: {str(e)}")
    
    def find_one(self, collection_name: str, filter_query: Dict = None, projection: Dict = None) -> Optional[Dict]:
        """
        Find a single document in a collection.
        
        Args:
            collection_name (str): Name of the collection
            filter_query (dict): MongoDB filter query
            projection (dict): Fields to include/exclude
            
        Returns:
            dict or None: Found document or None if not found
        """
        try:
            collection = self.get_collection(collection_name)
            return collection.find_one(filter_query or {}, projection)
        except Exception as e:
            raise RuntimeError(f"Failed to find document in {collection_name}: {str(e)}")
    
    def find(self, collection_name: str, filter_query: Dict = None, projection: Dict = None, limit: int = None) -> List[Dict]:
        """
        Find multiple documents in a collection.
        
        Args:
            collection_name (str): Name of the collection
            filter_query (dict): MongoDB filter query
            projection (dict): Fields to include/exclude
            limit (int): Maximum number of documents to return
            
        Returns:
            list: List of found documents
        """
        try:
            collection = self.get_collection(collection_name)
            cursor = collection.find(filter_query or {}, projection)
            if limit:
                cursor = cursor.limit(limit)
            return list(cursor)
        except Exception as e:
            raise RuntimeError(f"Failed to find documents in {collection_name}: {str(e)}")
    
    def insert_one(self, collection_name: str, document: Dict) -> str:
        """
        Insert a single document into a collection.
        
        Args:
            collection_name (str): Name of the collection
            document (dict): Document to insert
            
        Returns:
            str: Inserted document ID
        """
        try:
            collection = self.get_collection(collection_name)
            result = collection.insert_one(document)
            return str(result.inserted_id)
        except Exception as e:
            raise RuntimeError(f"Failed to insert document in {collection_name}: {str(e)}")
    
    def update_one(self, collection_name: str, filter_query: Dict, update_query: Dict, upsert: bool = False) -> bool:
        """
        Update a single document in a collection.
        
        Args:
            collection_name (str): Name of the collection
            filter_query (dict): MongoDB filter query
            update_query (dict): Update operations
            upsert (bool): Create document if not found
            
        Returns:
            bool: True if document was modified, False otherwise
        """
        try:
            collection = self.get_collection(collection_name)
            result = collection.update_one(filter_query, update_query, upsert=upsert)
            return result.modified_count > 0 or (upsert and result.upserted_id is not None)
        except Exception as e:
            raise RuntimeError(f"Failed to update document in {collection_name}: {str(e)}")
    
    def update_many(self, collection_name: str, filter_query: Dict, update_query: Dict) -> int:
        """
        Update multiple documents in a collection.
        
        Args:
            collection_name (str): Name of the collection
            filter_query (dict): MongoDB filter query
            update_query (dict): Update operations
            
        Returns:
            int: Number of documents modified
        """
        try:
            collection = self.get_collection(collection_name)
            result = collection.update_many(filter_query, update_query)
            return result.modified_count
        except Exception as e:
            raise RuntimeError(f"Failed to update documents in {collection_name}: {str(e)}")
    
    def delete_one(self, collection_name: str, filter_query: Dict) -> bool:
        """
        Delete a single document from a collection.
        
        Args:
            collection_name (str): Name of the collection
            filter_query (dict): MongoDB filter query
            
        Returns:
            bool: True if document was deleted, False otherwise
        """
        try:
            collection = self.get_collection(collection_name)
            result = collection.delete_one(filter_query)
            return result.deleted_count > 0
        except Exception as e:
            raise RuntimeError(f"Failed to delete document in {collection_name}: {str(e)}")
    
    def get_api_keys(self) -> Dict[str, str]:
        """
        Get all API keys from all collections.
        
        Returns:
            dict: Dictionary mapping API keys to collection names
        """
        try:
            apikeys = {}
            for collection_name in self.list_collections():
                documents = self.find(collection_name, {"apikey": {"$exists": True}})
                for doc in documents:
                    if "apikey" in doc:
                        apikeys[doc["apikey"]] = collection_name
            return apikeys
        except Exception as e:
            raise RuntimeError(f"Failed to get API keys: {str(e)}")
    
    def get_db_connections(self) -> Dict[str, Any]:
        """
        Get database connections configuration from all collections.
        
        Returns:
            dict: Dictionary with database connections
        """
        try:
            db_connections = {}
            for collection_name in self.list_collections():
                documents = self.find(collection_name, {"wms": {"$exists": True}})
                for doc in documents:
                    if "wms" in doc and "db" in doc["wms"]:
                        db_connections[collection_name] = doc["wms"]["db"]
                        if "db_base" in doc["wms"]:
                            db_connections[f"{collection_name}_base"] = doc["wms"]["db_base"]
            return db_connections
        except Exception as e:
            raise RuntimeError(f"Failed to get database connections: {str(e)}")
    
    def get_time_zones(self) -> Dict[str, str]:
        """
        Get time zones from all collections.
        
        Returns:
            dict: Dictionary mapping collection names to time zones
        """
        try:
            time_zones = {}
            for collection_name in self.list_collections():
                documents = self.find(collection_name, {"time_zone": {"$exists": True}})
                if documents:
                    time_zones[collection_name] = documents[0]["time_zone"]
                else:
                    time_zones[collection_name] = "UTC"  # Default timezone
            return time_zones
        except Exception as e:
            raise RuntimeError(f"Failed to get time zones: {str(e)}")
    
    def get_meli_config(self) -> Dict[str, Any]:
        """
        Get MercadoLibre configuration from the meli_test collection.
        
        Returns:
            dict: MercadoLibre configuration
        """
        try:
            doc = self.find_one("meli_test")
            if doc and "meli_config" in doc:
                return doc["meli_config"]
            else:
                raise Exception("MercadoLibre configuration not found")
        except Exception as e:
            raise RuntimeError(f"Failed to get MercadoLibre configuration: {str(e)}")
    
    def update_meli_tokens(self, access_token: str, refresh_token: str) -> bool:
        """
        Update MercadoLibre access and refresh tokens.
        
        Args:
            access_token (str): New access token
            refresh_token (str): New refresh token
            
        Returns:
            bool: True if tokens were updated successfully
        """
        try:
            update_query = {
                "$set": {
                    "meli_config.access_token": access_token,
                    "meli_config.refresh_token": refresh_token
                }
            }
            return self.update_one("meli_test", {}, update_query)
        except Exception as e:
            raise RuntimeError(f"Failed to update MercadoLibre tokens: {str(e)}")
    
    def get_config(self, database: str, platform: str) -> Dict[str, Any]:
        """
        Get configuration for a specific database and platform.
        
        Args:
            database (str): Database/collection name
            platform (str): Platform identifier
            
        Returns:
            dict: Configuration data
        """
        try:
            filter_query = {platform: {"$exists": True}}
            doc = self.find_one(database, filter_query)
            if doc:
                doc.pop("_id", None)  # Remove MongoDB ObjectId
                return doc
            return {}
        except Exception as e:
            raise RuntimeError(f"Failed to get config for {database}/{platform}: {str(e)}")
    
    def close_connection(self):
        """Close the MongoDB connection."""
        if self.client is not None:
            self.client.close()
            self.client = None
            self.db = None


# Global instance
mongodb_service = MongoDBService()