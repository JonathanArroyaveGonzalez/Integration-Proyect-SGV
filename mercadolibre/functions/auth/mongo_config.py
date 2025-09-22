"""Dependencies"""

import os
from pymongo import MongoClient
from dotenv import load_dotenv
from settings.settings import global_settings

load_dotenv()


def get_meli_config():
    """
    This function returns the MercadoLibre configuration from MongoDB
    """
    try:
        apidbmongo = os.getenv("APIDBMONGO")
    except KeyError as e:
        raise RuntimeError("Could not find a APIDBMONGO in environment") from e

    try:
        # Connect to the mongo client
        client = MongoClient(global_settings.CONNECTION_STRING)

        # Select the database
        db = client[apidbmongo]

        # Get the collection
        collection = db["meli_test"]

        # Find the configuration document
        config_doc = collection.find_one()

        # Close the connection
        client.close()

        if config_doc and "meli_config" in config_doc:
            return config_doc["meli_config"]
        else:
            raise Exception("MercadoLibre configuration not found")

    except Exception as e:
        raise Exception(f"Error getting MercadoLibre configuration: {str(e)}")


def update_meli_tokens(access_token, refresh_token):
    """
    This function updates the access_token and refresh_token in MongoDB
    """
    try:
        apidbmongo = os.getenv("APIDBMONGO")
    except KeyError as e:
        raise RuntimeError("Could not find a APIDBMONGO in environment") from e

    try:
        # Connect to the mongo client
        client = MongoClient(global_settings.CONNECTION_STRING)

        # Select the database
        db = client[apidbmongo]

        # Get the collection
        collection = db["meli_test"]

        # Update the tokens in the meli_config
        result = collection.update_one(
            {},  # Filter - update the first document found
            {
                "$set": {
                    "meli_config.access_token": access_token,
                    "meli_config.refresh_token": refresh_token,
                }
            },
        )

        # Close the connection
        client.close()

        if result.modified_count > 0:
            return True
        else:
            raise Exception("No document was updated")

    except Exception as e:
        raise Exception(f"Error updating MercadoLibre tokens: {str(e)}")
