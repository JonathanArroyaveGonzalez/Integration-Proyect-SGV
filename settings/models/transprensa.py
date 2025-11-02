from .config import Config


class TransprensaModel:
    def __init__(self):
        
        self.config = Config()
        self.db = self.config.client["apiconfig"]
        self.collection = self.db["transprensa_test"]

    def get_config(self) -> dict:
        """
        Obtiene todo el documento de configuración de Transprensa.
        """
        document = self.collection.find_one({}, {"_id": 0})
        return document or {}

    def get_field(self, field_path: str):
        """
        Obtiene un campo específico dentro del documento.
        Ejemplo: field_path = "transprensa_config.usuario_login"
        """
        projection = {field_path: 1, "_id": 0}
        document = self.collection.find_one({}, projection)
        value = document
        for key in field_path.split('.'):
            if isinstance(value, dict):
                value = value.get(key)
        return value

    def update_field(self, field_path: str, new_value):
        """
        Actualiza un campo específico del documento de configuración.
        Ejemplo: field_path = "transprensa_config.token"
        """
        update_query = {"$set": {field_path: new_value}}
        result = self.collection.update_one({}, update_query)
        return result.modified_count > 0

    def update_config(self, new_data: dict):
        """
        Reemplaza completamente el documento de configuración.
        """
        result = self.collection.replace_one({}, new_data, upsert=True)
        return result.modified_count > 0 or result.upserted_id is not None
