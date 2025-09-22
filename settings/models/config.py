from threading import Lock
from dotenv import load_dotenv
from project.mongodb_service import mongodb_service

load_dotenv()


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
        self.mongodb_service = mongodb_service
        self.config_data = None

    def get_collections(self):
        return self.mongodb_service.list_collections()

    def get_config(self, database: str, platform: str):
        self.config_data = self.mongodb_service.get_config(database, platform)
        return self.config_data

    def reload_config(self, database: str, platform: str):
        self.config_data = self._load_config(database, platform)
        return self.config_data
