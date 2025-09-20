"""Dependencies"""

from settings.settings import global_settings
import os
from pymongo import MongoClient
from dotenv import load_dotenv

""" Local Dependencies """

load_dotenv()


def get_collections() -> list:
    """
    This function returns a list with the names of the collections in the database
    """

    try:
        apidbmongo = os.getenv("APIDBMONGO")
    except KeyError as e:
        raise RuntimeError("Could not find a APIDBMONGO in environment") from e

    try:
        # connect to the mongo client
        client = MongoClient(global_settings.CONNECTION_STRING)

        # select the database
        db = client[apidbmongo]  # type: ignore

        # get the collections
        collections = db.list_collection_names()

        # close the connection
        client.close()

        # return the collections
        return collections

    # if the connection fails, return an empty list
    except Exception:
        return []


def get_apikeys() -> dict:
    """
    This function returns a dictionary with the apikeys for each collection
    """
    try:
        apidbmongo = os.getenv("APIDBMONGO")
    except KeyError as e:
        raise RuntimeError("Could not find a APIDBMONGO in environment") from e

    try:
        # connect to the mongo client
        client = MongoClient(global_settings.CONNECTION_STRING)

        # select the database
        db = client[apidbmongo]  # type: ignore

        # initialize the dictionary
        apikeys = {}

        # for each collection, get the apikey
        for collection in db.list_collection_names():

            # select the collection
            collection = db[collection]

            # get the apikey
            item_details = collection.find({"apikey": {"$exists": True}})

            # add the apikey to the dictionary
            for item in item_details:
                apikeys[item["apikey"]] = collection.name

        # close the connection
        client.close()

        # return the dictionary
        return apikeys

    # if the connection fails, return an empty dictionary
    except Exception:
        return {}


def get_db_connection() -> dict:
    """
    This function returns a dictionary with the database connection for each collection
    """
    try:
        apidbmongo = os.getenv("APIDBMONGO")
    except KeyError as e:
        raise RuntimeError("Could not find a APIDBMONGO in environment") from e

    try:
        try:
            # connect to the mongo client
            client = MongoClient(global_settings.CONNECTION_STRING)
        except Exception:
            # if the connection fails, return an empty dictionary
            raise ValueError("Could not connect to the database")

        # select the database
        db = client[apidbmongo]  # type: ignore

        # initialize the dictionary
        db_connection = {}

        # for each collection, get the database connection
        for collection in db.list_collection_names():

            # select the collection
            collection = db[collection]

            # get the database connection
            item_details = collection.find({"wms": {"$exists": True}})

            # add the databases connections to the dictionary (adapter and base)
            for item in item_details:
                db_connection[collection.name] = item["wms"]["db"]  # adapter
                db_connection[str(collection.name) + "_base"] = item["wms"][
                    "db_base"
                ]  # base

        # close the connection
        client.close()

        # return the dictionary
        return db_connection

    # if the connection fails, return an empty dictionary
    except Exception:
        return {}


def get_time_zones() -> dict:
    """
    This function returns a dictionary with the time zones for each collection
    """
    try:
        apidbmongo = os.getenv("APIDBMONGO")
    except KeyError as e:
        raise RuntimeError("Could not find a APIDBMONGO in environment") from e

    try:
        # connect to the mongo client
        client = MongoClient(global_settings.CONNECTION_STRING)

        # select the database
        db = client[apidbmongo]  # type: ignore

        # initialize the dictionary
        time_zones = {}

        # for each collection, get the time zone
        for collection in db.list_collection_names():

            # select the collection
            collection = db[collection]

            # get the time zone
            item_details = list(collection.find({"time_zone": {"$exists": True}}))
            # add a default time zone to the dictionary
            if len(item_details) == 0:
                time_zones[collection.name] = "UTC"
            else:
                # add the time zone to the dictionary
                for item in item_details:
                    time_zones[collection.name] = item["time_zone"]

        # close the connection
        client.close()

        # return the dictionary
        return time_zones

    # if the connection fails, return an empty dictionary
    except Exception:
        return {}
