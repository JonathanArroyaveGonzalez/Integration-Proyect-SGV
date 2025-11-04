from .config import Config


class TransprensaModel:
    def __init__(self):
        
        self.config = Config()
        self.db = self.config.client["apiconfig"]
        self.collection = self.db["transprensa_test"]

    def get_config(self) -> dict:
        """
        Obtiene el documento de configuración de Transprensa,
        reemplazando test_url y production_url por base_url.
        """
        document = self.collection.find_one({}, {"_id": 0}) or {}
        trans_conf = document.get("transprensa_config", {})

        # Extraer valores
        test_url = trans_conf.get("test_url")
        production_url = trans_conf.get("production_url")
        is_test = trans_conf.get("test", "True").lower() == "true"

        # Calcular base_url
        base_url = test_url if is_test else production_url

        # Reemplazar en el documento
        trans_conf["base_url"] = base_url
        trans_conf.pop("test_url", None)
        trans_conf.pop("production_url", None)

        document["transprensa_config"] = trans_conf
        return document

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
