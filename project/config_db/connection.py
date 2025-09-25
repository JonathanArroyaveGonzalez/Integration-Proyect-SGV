"""MongoDB connection management."""

import os
from threading import Lock
from typing import Optional
from pymongo import MongoClient
from pymongo.database import Database
from dotenv import load_dotenv

load_dotenv()


class MongoConnection:
    """Singleton MongoDB connection manager."""
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(MongoConnection, cls).__new__(cls)
                    cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize MongoDB connection."""
        self.database_url = os.getenv("DATABASE_URL")
        self.database_name = os.getenv("APIDBMONGO")
        
        if not self.database_url or not self.database_name:
            raise RuntimeError("Missing DATABASE_URL or APIDBMONGO in environment")
        
        self.client: Optional[MongoClient] = None
        self.db: Optional[Database] = None
        self._connect()
    
    def _connect(self):
        """Establish connection to MongoDB."""
        try:
            self.client = MongoClient(self.database_url)
            self.db = self.client[self.database_name]
            # Test connection
            self.client.server_info()
        except Exception as e:
            raise RuntimeError(f"Failed to connect to MongoDB: {str(e)}")
    
    def get_database(self) -> Database:
        """Get the database instance."""
        if self.db is None:
            self._connect()
        return self.db
    
    def close(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            self.client = None
            self.db = None


# Global connection instance
mongo_connection = MongoConnection()
