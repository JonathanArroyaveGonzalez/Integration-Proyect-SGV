#!/usr/bin/env python3
"""
Script para verificar y crear API Keys en MongoDB
"""

import os
import uuid
from pymongo import MongoClient
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def connect_to_mongo():
    """Conectar a MongoDB usando las credenciales del .env"""
    try:
        connection_string = os.getenv("DATABASE_URL")
        if not connection_string:
            raise ValueError("DATABASE_URL no encontrada en .env")
        
        client = MongoClient(connection_string)
        # Test de conexión
        client.admin.command('ping')
        print("✅ Conexión a MongoDB exitosa")
        return client
    except Exception as e:
        print(f"❌ Error conectando a MongoDB: {e}")
        return None

def get_existing_apikeys():
    """Verificar API Keys existentes"""
    client = connect_to_mongo()
    if not client:
        return {}
    
    try:
        apidbmongo = os.getenv("APIDBMONGO", "apiconfig")
        print(f"📋 Buscando en la base de datos: {apidbmongo}")
        
        db = client[apidbmongo]
        collections = db.list_collection_names()
        print(f"📂 Colecciones encontradas: {collections}")
        
        apikeys = {}
        
        for collection_name in collections:
            collection = db[collection_name]
            # Buscar documentos con campo 'apikey'
            docs_with_apikey = list(collection.find({"apikey": {"$exists": True}}))
            
            for doc in docs_with_apikey:
                apikeys[doc["apikey"]] = collection_name
                print(f"🔑 API Key encontrada: {doc['apikey'][:20]}... -> {collection_name}")
        
        client.close()
        return apikeys
    except Exception as e:
        print(f"❌ Error obteniendo API Keys: {e}")
        client.close()
        return {}

def create_sample_apikey():
    """Crear una API Key de ejemplo"""
    client = connect_to_mongo()
    if not client:
        return None
    
    try:
        apidbmongo = os.getenv("APIDBMONGO", "apiconfig")
        db = client[apidbmongo]
        
        # Nombre de la colección para el cliente de prueba
        collection_name = "test_client"
        collection = db[collection_name]
        
        # Generar una API Key única
        api_key = f"test-{uuid.uuid4().hex[:16]}"
        
        # Documento con la estructura esperada
        document = {
            "apikey": api_key,
            "wms": {
                "db": {
                    "ENGINE": "django.db.backends.sqlite3",
                    "NAME": f"{collection_name}.db",
                    "USER": "",
                    "PASSWORD": "",
                    "HOST": "",
                    "PORT": ""
                },
                "db_base": {
                    "ENGINE": "django.db.backends.sqlite3",
                    "NAME": f"{collection_name}_base.db",
                    "USER": "",
                    "PASSWORD": "",
                    "HOST": "",
                    "PORT": ""
                }
            },
            "time_zone": "UTC",
            "created_at": "2025-01-18T03:15:00Z",
            "description": "API Key de prueba creada automáticamente"
        }
        
        # Insertar el documento
        result = collection.insert_one(document)
        
        print(f"✅ API Key creada exitosamente!")
        print(f"🔑 API Key: {api_key}")
        print(f"📂 Colección: {collection_name}")
        print(f"🆔 Document ID: {result.inserted_id}")
        
        client.close()
        return api_key
        
    except Exception as e:
        print(f"❌ Error creando API Key: {e}")
        client.close()
        return None

def main():
    print("🚀 Verificando API Keys en MongoDB...\n")
    
    # Verificar API Keys existentes
    existing_keys = get_existing_apikeys()
    
    if existing_keys:
        print(f"\n✅ Se encontraron {len(existing_keys)} API Key(s) existente(s):")
        for api_key, collection in existing_keys.items():
            print(f"   🔑 {api_key[:20]}... -> {collection}")
        
        print(f"\n💡 Puedes usar cualquiera de estas API Keys en Postman:")
        for api_key in existing_keys.keys():
            print(f"   Authorization: {api_key}")
            break  # Solo mostrar la primera para el ejemplo
    else:
        print("❌ No se encontraron API Keys existentes.")
        print("\n🔧 Creando una API Key de prueba...")
        
        new_api_key = create_sample_apikey()
        
        if new_api_key:
            print(f"\n🎉 ¡Listo! Usa esta API Key en Postman:")
            print(f"   Header: Authorization")
            print(f"   Value: {new_api_key}")
        else:
            print("❌ No se pudo crear la API Key")

if __name__ == "__main__":
    main()
