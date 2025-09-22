<<<<<<< HEAD
import requests

ML_BASE_URL = "https://api.mercadolibre.com"

# ⚡ Configuración con los tokens actuales
ACCESS_TOKEN = "APP_USR-4013894436730927-091810-80594d566859ef30bc6a29edc7ce6a06-2679650708"
ML_USER_ID = "2679650708"   # nuevo user_id que te devolvió Mercado Libre


def get_items_from_user() -> list[str]:
    """Obtiene todos los IDs de publicaciones del usuario"""
    url = f"{ML_BASE_URL}/users/{ML_USER_ID}/items/search"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json().get("results", [])


def get_item_detail(item_id: str) -> dict:
    """Obtiene los detalles completos de un ítem"""
    url = f"{ML_BASE_URL}/items/{item_id}"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()


def get_item_description(item_id: str) -> str:
    """Obtiene la descripción en texto plano del ítem"""
    url = f"{ML_BASE_URL}/items/{item_id}/description"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        return resp.json().get("plain_text", "")
    return ""


def extract_attribute(attributes: list[dict], attr_id: str) -> str:
    """Busca un atributo específico por su ID (ej: SELLER_SKU, GTIN)"""
    for attr in attributes:
        if attr.get("id") == attr_id:
            return attr.get("value_name", "")
    return ""


def extract_all_items() -> list[dict]:
    """Extrae todos los ítems publicados del usuario"""
    item_ids = get_items_from_user()
    extracted = []

    for item_id in item_ids:
        try:
            item = get_item_detail(item_id)
            description = get_item_description(item_id)

            attributes = item.get("attributes", [])
            sku = item.get("seller_custom_field") or extract_attribute(attributes, "SELLER_SKU")
            ean = extract_attribute(attributes, "GTIN")

            extracted.append({
                "id": item["id"],
                "sku": sku,
                "ean": ean,
                "title": item.get("title"),
                "description": description,
                "category_id": item.get("category_id"),
                "price": item.get("price"),
                "currency": item.get("currency_id"),
                "stock": item.get("available_quantity")
            })
        except Exception as e:
            print(f"Error procesando item {item_id}: {e}")

    return extracted


if __name__ == "__main__":
    items = extract_all_items()
    for it in items:
        print(it)
=======
from mercadolibre.utils.api_client import make_authenticated_request, get_meli_api_base_url
from mercadolibre.utils.data_mapper import ProductMapper
from .extract_id import extract_product_ids
import requests
from django.conf import settings

base_url = get_meli_api_base_url()

def get_wms_base_url():
    """
    Obtiene la URL base del WMS desde configuración
    """
    
    # Buscar en settings de Django
    try:
        wms_url = getattr(settings, 'WMS_BASE_URL', None)
        if wms_url:
            return wms_url.rstrip('/')
    except Exception:
        pass
    
    # URL por defecto para desarrollo
    return "http://localhost:8000"

def get_product_details(product_ids):
    """
    Obtiene los detalles de los productos desde MercadoLibre
    """
    if not product_ids:
        return []
    
    # MercadoLibre API permite hasta 20 IDs por request
    url = f"{base_url}items?ids={','.join(product_ids[:20])}"
    
    try:
        response = make_authenticated_request("GET", url)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error obteniendo productos: {response.status_code}: {response.text}")
            return []
    except Exception as e:
        print(f"Error en get_product_details: {str(e)}")
        return []

def sync_products_to_wms(auth_headers=None):
    """
    Sincroniza productos de MercadoLibre con el WMS
    
    Args:
        auth_headers (dict): Headers de autorización para el WMS
    """
    try:
        # 1. Extraer IDs de productos
        print("Extrayendo IDs de productos...")
        product_ids = extract_product_ids()
        
        if not product_ids:
            return {"success": False, "message": "No se encontraron productos"}
        
        print(f"Encontrados {len(product_ids)} productos")
        
        # 2. Obtener detalles de productos
        print("Obteniendo detalles de productos...")
        meli_items = get_product_details(product_ids)
        
        if not meli_items:
            return {"success": False, "message": "No se pudieron obtener detalles de productos"}
        
        # 3. Mapear productos a formato WMS
        print("Mapeando productos...")
        wms_products = map_products_to_wms_format(meli_items)
        
        # 4. Enviar al WMS con headers de autorización
        print("Enviando productos al WMS...")
        result = send_products_to_wms(wms_products, auth_headers=auth_headers)
        
        return result
        
    except Exception as e:
        return {"success": False, "message": f"Error en sincronización: {str(e)}"}

def map_products_to_wms_format(meli_items):
    """
    Mapea productos de MercadoLibre al formato del WMS usando ProductMapper
    """
    wms_products = []
    
    for item in meli_items:
        try:
            # Extraer datos del producto
            if "body" in item:
                product_data = item["body"]
            else:
                product_data = item
            
            # Usar ProductMapper para mapear el producto
            product_mapper = ProductMapper.from_meli_item(product_data)
            
            # Convertir a diccionario y agregar campos específicos del WMS
            wms_product = product_mapper.to_dict()
            
            # Asegurar campos obligatorios y valores por defecto para WMS
            wms_product.update({
                "bodega": wms_product.get("bodega", "PRINCIPAL"),
                "inventariable": wms_product.get("inventariable", 1),
                "um1": wms_product.get("um1", "UND"),
                "factor": wms_product.get("factor", 1.0),
                "estado": wms_product.get("estado", 1),
                "estadotransferencia": wms_product.get("estadotransferencia", 0),
                "controla_status_calidad": wms_product.get("controla_status_calidad", 0),
                "tipo": wms_product.get("tipo", "MERCADOLIBRE"),
            })
            
            # Validar campos obligatorios
            required_fields = ["productoean", "descripcion", "referencia", "nuevoean"]
            if all(wms_product.get(field) for field in required_fields):
                wms_products.append(wms_product)
            else:
                print(f"Producto omitido por campos obligatorios faltantes: {product_data.get('id', 'N/A')}")
                
        except Exception as e:
            print(f"Error mapeando producto: {str(e)}")
            continue
    
    return wms_products

def send_products_to_wms(wms_products, auth_headers=None):
    """
    Envía productos al WMS usando el endpoint de artículos
    
    Args:
        wms_products (list): Lista de productos en formato WMS
        auth_headers (dict): Headers de autorización para el WMS
    """
    if not wms_products:
        return {"success": False, "message": "No hay productos para enviar"}
    
    try:
        # Obtener URL base del WMS dinámicamente
        wms_base_url = get_wms_base_url()
        wms_url = f"{wms_base_url}/wms/adapter/v2/art"
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # Agregar headers de autorización si están disponibles
        if auth_headers and 'Authorization' in auth_headers:
            headers['Authorization'] = auth_headers['Authorization']
        
        # Enviar productos como lista (formato esperado por el WMS)
        payload = wms_products
        
        response = requests.post(wms_url, json=payload, headers=headers)
        
        if response.status_code in [200, 201]:
            return {
                "success": True, 
                "message": f"Se sincronizaron {len(wms_products)} productos exitosamente",
                "data": response.json()
            }
        else:
            return {
                "success": False, 
                "message": f"Error del WMS: {response.status_code} - {response.text}"
            }
            
    except Exception as e:
        return {"success": False, "message": f"Error enviando al WMS: {str(e)}"}

# Funciones legacy mantenidas para compatibilidad
def sync_products():
    """
    Método legacy que extrae la información de los productos de MercadoLibre
    """
    try:
        product_ids = extract_product_ids()
        return get_product_details(product_ids)
    except Exception as e:
        print(f"Error {str(e)}")
        return []

def map_products(meli_items):
    """
    Método legacy que mapea la información de los productos de MercadoLibre usando ProductMapper
    Params: meli_items: lista de items de MercadoLibre
    return: lista mapeada de productos
    """
    mapped_products = []
    for item in meli_items:
        try:
            if "body" in item:
                product_data = item["body"]
            else:
                product_data = item
            
            # Usar ProductMapper para consistencia
            product_mapper = ProductMapper.from_meli_item(product_data)
            mapped_products.append(product_mapper.to_dict())
        except Exception as e:
            print(f"Error mapeando producto legacy: {str(e)}")
            continue
    
    return mapped_products

>>>>>>> 15208b5ff8cd253f2c691c80bd3fe4b5da85d1d8
