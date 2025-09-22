import logging
import requests
from django.conf import settings
from mercadolibre.utils.api_client import make_authenticated_request, get_meli_api_base_url
from mercadolibre.utils.data_mapper import ProductMapper

logger = logging.getLogger(__name__)
BASE_URL = get_meli_api_base_url()

def get_wms_base_url():
    """
    Obtiene la URL base del WMS desde configuración de Django o usa una por defecto
    """
    return getattr(settings, 'WMS_BASE_URL', "http://localhost:8000").rstrip('/')

def get_product_by_id(product_id):
    """
    Obtiene los detalles de un producto específico desde MercadoLibre
    
    Args:
        product_id (str): ID del producto en MercadoLibre
        
    Returns:
        dict: Datos del producto o None si hay error
    """
    if not product_id:
        return None
    
    url = f"{BASE_URL}items?ids={product_id}"
    try:
        response = make_authenticated_request("GET", url)
        response.raise_for_status()
        result = response.json()
        
        # La API devuelve una lista, tomamos el primer elemento
        if result and len(result) > 0:
            # Si hay error en la respuesta
            if result[0].get("code") == 200:
                return result[0].get("body")
            else:
                logger.error(f"Error en respuesta de MercadoLibre para producto {product_id}: {result[0]}")
                return None
        
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error obteniendo producto {product_id} de MercadoLibre: {e}")
        return None

def map_product_to_wms_format(meli_item):
    """
    Mapea un producto de MercadoLibre al formato del WMS usando ProductMapper
    
    Args:
        meli_item (dict): Datos del producto de MercadoLibre
        
    Returns:
        dict: Producto mapeado al formato WMS
    """
    try:
        product_mapper = ProductMapper.from_meli_item(meli_item)
        wms_product = product_mapper.to_dict()

        # Valores por defecto para campos del WMS
        wms_product.setdefault("bodega", "PRINCIPAL")
        wms_product.setdefault("inventariable", 1)
        wms_product.setdefault("um1", "UND")
        wms_product.setdefault("factor", 1.0)
        wms_product.setdefault("estado", 1)
        wms_product.setdefault("estadotransferencia", 0)
        wms_product.setdefault("controla_status_calidad", 0)
        wms_product.setdefault("tipo", "MERCADOLIBRE")

        return wms_product
    except Exception as e:
        logger.error(f"Error mapeando producto {meli_item.get('id', 'N/A')}: {e}")
        return None

def update_product_in_wms(wms_product, auth_headers=None):
    """
    Actualiza un producto en el WMS usando el endpoint de artículos con método PUT
    
    Args:
        wms_product (dict): Datos del producto en formato WMS
        auth_headers (dict): Headers de autenticación
        
    Returns:
        dict: Resultado de la operación
    """
    if not wms_product:
        return {"success": False, "message": "No hay datos del producto para actualizar"}
    
    try:
        wms_url = f"{get_wms_base_url()}/wms/adapter/v2/art"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # Agregar headers de autenticación si están disponibles
        if auth_headers and 'Authorization' in auth_headers:
            headers['Authorization'] = auth_headers['Authorization']

        response = requests.put(wms_url, json=wms_product, headers=headers)
        
        if response.status_code in (200, 201):
            return {
                "success": True,
                "message": "Producto actualizado exitosamente en el WMS",
                "data": response.json()
            }
        else:
            return {
                "success": False, 
                "message": f"Error del WMS: {response.status_code} - {response.text}"
            }

    except requests.exceptions.RequestException as e:
        return {"success": False, "message": f"Error actualizando en el WMS: {e}"}

def update_product_from_meli_to_wms(product_id, auth_headers=None):
    """
    Función principal que orquesta la actualización de un producto:
    1. Obtiene el producto de MercadoLibre por ID
    2. Lo mapea al formato del WMS
    3. Lo actualiza en el WMS usando PUT
    
    Args:
        product_id (str): ID del producto en MercadoLibre
        auth_headers (dict): Headers de autenticación
        
    Returns:
        dict: Resultado de la operación
    """
    try:
        logger.info(f"Iniciando actualización del producto {product_id}")
        
        # 1. Obtener producto de MercadoLibre
        meli_item = get_product_by_id(product_id)
        if not meli_item:
            return {"success": False, "message": f"No se pudo obtener el producto {product_id} de MercadoLibre"}
        
        logger.info(f"Producto obtenido de MercadoLibre: {meli_item.get('title', 'Sin título')}")
        
        # 2. Mapear al formato WMS
        wms_product = map_product_to_wms_format(meli_item)
        if not wms_product:
            return {"success": False, "message": "Error mapeando el producto al formato WMS"}
        
        logger.info("Producto mapeado exitosamente al formato WMS")
        
        # 3. Actualizar en WMS
        result = update_product_in_wms(wms_product, auth_headers)
        
        if result["success"]:
            logger.info(f"Producto {product_id} actualizado exitosamente")
        else:
            logger.error(f"Error actualizando producto {product_id}: {result['message']}")
        
        return result
        
    except Exception as e:
        logger.exception(f"Error en actualización del producto {product_id}")
        return {"success": False, "message": f"Error en actualización: {e}"}
