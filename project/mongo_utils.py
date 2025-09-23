"""
MongoDB utilities and helper functions.

This module provides convenient access to the centralized MongoDB service
and commonly used database operations.
"""

from project.mongodb_service import mongodb_service

# Export the service for easy importing
__all__ = ['mongodb_service', 'get_mongo_service']


def get_mongo_service():
    """
    Get the singleton MongoDB service instance.
    
    Returns:
        MongoDBService: The MongoDB service instance
    """
    return mongodb_service