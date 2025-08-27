from settings.settings import global_settings
from threading import Lock
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

try:
    apidbmongo = os.getenv("APIDBMONGO")
except KeyError as e:
    raise RuntimeError("Could not find a APIDBMONGO in environment") from e


class Config:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(Config, cls).__new__(cls)
                    cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.CONNECTION_STRING = global_settings.CONNECTION_STRING
        self.client = MongoClient(self.CONNECTION_STRING)
        self.db = self.client[apidbmongo]
        self.collections = self.db.list_collection_names()
        self.config_data = None

    def _load_config(self, database: str, platform: str):
        collection = self.db[database]
        json_query = {platform: {"$exists": True}}
        item_details = collection.find(json_query)
        config = []
        for item in item_details:
            item.pop("_id", None)
            config.append(item)
        return config[0] if config else {}

    def get_collections(self):
        return self.collections

    def get_config(self, database: str, platform: str):
        self.config_data = self._load_config(database, platform)
        return self.config_data

    def reload_config(self, database: str, platform: str):
        self.config_data = self._load_config(database, platform)
        return self.config_data
