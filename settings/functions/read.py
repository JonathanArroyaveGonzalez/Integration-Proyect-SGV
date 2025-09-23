"""Dependencies"""

from dotenv import load_dotenv
from project.mongodb_service import mongodb_service

load_dotenv()


def get_collections() -> list:
    """
    This function returns a list with the names of the collections in the database
    """
    try:
        return mongodb_service.list_collections()
    except Exception:
        return []


def get_apikeys() -> dict:
    """
    This function returns a dictionary with the apikeys for each collection
    """
    try:
        return mongodb_service.get_api_keys()
    except Exception:
        return {}


def get_db_connection() -> dict:
    """
    This function returns a dictionary with the database connection for each collection
    """
    try:
        return mongodb_service.get_db_connections()
    except Exception:
        return {}


def get_time_zones() -> dict:
    """
    This function returns a dictionary with the time zones for each collection
    """
    try:
        return mongodb_service.get_time_zones()
    except Exception:
        return {}
