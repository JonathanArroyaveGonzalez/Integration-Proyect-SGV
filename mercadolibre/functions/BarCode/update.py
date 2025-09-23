import logging
import requests
from django.conf import settings
from mercadolibre.utils.mapper.data_mapper import BarCodeMapper
from .check import check_barcode_exists

logger = logging.getLogger(__name__)

def get_wms_base_url():
    """
    Obtiene la URL base del WMS desde configuración de Django o usa una por defecto
    """
    return getattr(settings, 'WMS_BASE_URL', "http://localhost:8000").rstrip('/')

def update_barcode_in_wms(barcode_data, ean, auth_headers=None):
    """
    Actualiza un código de barras en el WMS usando el endpoint de tRelacionCodbarras
    
    Args:
        barcode_data (dict): Datos del código de barras en formato BarCodeMapper
        ean (str): EAN del código de barras a actualizar
        auth_headers (dict): Headers de autenticación
        
    Returns:
        dict: Resultado de la operación
    """
    if not barcode_data:
        return {"success": False, "message": "No hay datos del código de barras para actualizar"}
    
    try:
        wms_url = f"{get_wms_base_url()}/wms/base/v2/tRelacionCodbarras?idinternoean={ean}"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # Agregar headers de autenticación si están disponibles
        if auth_headers and 'Authorization' in auth_headers:
            headers['Authorization'] = auth_headers['Authorization']

        response = requests.put(wms_url, json=barcode_data, headers=headers)
        
        if response.status_code in (200, 201):
            return {
                "success": True,
                "message": "Código de barras actualizado exitosamente en el WMS",
                "data": response.json()
            }
        else:
            return {
                "success": False, 
                "message": f"Error del WMS: {response.status_code} - {response.text}"
            }

    except requests.exceptions.RequestException as e:
        return {"success": False, "message": f"Error actualizando código de barras en el WMS: {e}"}

def update_barcode_from_meli_item(meli_item, auth_headers=None):
    """
    Actualiza un código de barras en el WMS a partir de un item de MercadoLibre
    
    Args:
        meli_item (dict): Datos del producto de MercadoLibre
        auth_headers (dict): Headers de autenticación
        
    Returns:
        dict: Resultado de la operación
    """
    try:
        logger.info(f"Actualizando código de barras para item: {meli_item.get('id', 'N/A')}")
        
        # Crear BarCodeMapper desde el item de MercadoLibre
        barcode_mapper = BarCodeMapper.from_meli_item(meli_item)
        
        if not barcode_mapper:
            return {
                "success": False, 
                "message": f"No se pudo actualizar el código de barras para el item {meli_item.get('id', 'N/A')} - EAN no válido"
            }
        
        # Convertir a diccionario
        barcode_data = barcode_mapper.to_dict()
        ean = barcode_mapper.idinternoean
        
        logger.info(f"Datos del código de barras mapeados para actualización: {barcode_data}")
        
        # Actualizar en WMS
        result = update_barcode_in_wms(barcode_data, ean, auth_headers)
        
        if result["success"]:
            logger.info(f"Código de barras actualizado exitosamente para item {meli_item.get('id', 'N/A')}")
        else:
            logger.error(f"Error actualizando código de barras para item {meli_item.get('id', 'N/A')}: {result['message']}")
        
        return result
        
    except Exception as e:
        logger.exception(f"Error en actualización de código de barras para item {meli_item.get('id', 'N/A')}")
        return {"success": False, "message": f"Error en actualización de código de barras: {e}"}

def get_barcode_from_wms(ean, auth_headers=None):
    """
    Obtiene un código de barras del WMS por EAN
    
    Args:
        ean (str): EAN del código de barras a obtener
        auth_headers (dict): Headers de autenticación
        
    Returns:
        dict: Resultado de la operación con los datos del código de barras
    """
    if not ean:
        return {"success": False, "message": "EAN es requerido para obtener el código de barras"}
    
    try:
        wms_url = f"{get_wms_base_url()}/wms/base/v2/tRelacionCodbarras?idinternoean={ean}"
        headers = {
            'Accept': 'application/json'
        }
        
        # Agregar headers de autenticación si están disponibles
        if auth_headers and 'Authorization' in auth_headers:
            headers['Authorization'] = auth_headers['Authorization']

        response = requests.get(wms_url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "message": "Código de barras obtenido exitosamente",
                "data": data
            }
        elif response.status_code == 404:
            return {
                "success": False,
                "message": f"Código de barras con EAN {ean} no encontrado en el WMS"
            }
        else:
            return {
                "success": False, 
                "message": f"Error del WMS: {response.status_code} - {response.text}"
            }

    except requests.exceptions.RequestException as e:
        return {"success": False, "message": f"Error obteniendo código de barras del WMS: {e}"}

def sync_or_update_barcode_from_meli_item_optimized(meli_item, auth_headers=None, assume_new=False):
    """
    Sincroniza o actualiza un código de barras de manera optimizada:
    - Si assume_new=True, crea directamente sin verificaciones (productos nuevos)
    - Si assume_new=False, intenta verificar existencia primero (optimización)
    - Si la verificación falla o es inconsistente, usa directamente método legacy (rápido)
    
    Args:
        meli_item (dict): Datos del producto de MercadoLibre
        auth_headers (dict): Headers de autenticación
        assume_new (bool): Si True, asume que es un producto nuevo y crea directamente
        
    Returns:
        dict: Resultado de la operación con información de estrategia usada
    """
    try:
        # Crear BarCodeMapper para obtener el EAN
        barcode_mapper = BarCodeMapper.from_meli_item(meli_item)
        
        if not barcode_mapper:
            return {
                "success": False, 
                "message": f"No se pudo procesar el código de barras para el item {meli_item.get('id', 'N/A')} - EAN no válido",
                "strategy": "validation_failed"
            }
        
        ean = barcode_mapper.idinternoean
        
        # OPTIMIZACIÓN: Si asumimos que es nuevo, crear directamente
        if assume_new:
            logger.info(f"Producto nuevo detectado - creando código de barras directamente para EAN {ean}...")
            from .create import create_barcode_from_meli_item_direct
            result = create_barcode_from_meli_item_direct(meli_item, auth_headers)
            return result
        
        # OPTIMIZACIÓN: Un solo intento de verificación rápida
        logger.info(f"Verificando existencia de código de barras para EAN {ean}...")
        existence_check = check_barcode_exists(ean, auth_headers)
        
        # Si la verificación falla o retorna datos inconsistentes, usar legacy inmediatamente
        if not existence_check["success"] or existence_check.get("validation_status") in ["empty_data", "invalid_structure"]:
            if not existence_check["success"]:
                logger.info(f"Verificación falló para EAN {ean}, usando método legacy directamente.")
            else:
                logger.info(f"Datos inconsistentes del WMS detectados para EAN {ean}, usando método legacy directamente.")
            
            result = sync_or_update_barcode_from_meli_item_legacy(meli_item, auth_headers)
            result["strategy"] = "legacy_fallback_fast"
            return result
        
        if existence_check["exists"]:
            # EXISTE: Actualizar directamente
            logger.info(f"Código de barras existe para EAN {ean}, actualizando directamente...")
            result = update_barcode_from_meli_item(meli_item, auth_headers)
            result["strategy"] = "optimized_update"
            return result
        else:
            # NO EXISTE: Crear directamente
            logger.info(f"Código de barras no existe para EAN {ean}, creando directamente...")
            from .create import create_barcode_from_meli_item_direct
            result = create_barcode_from_meli_item_direct(meli_item, auth_headers)
            return result
        
    except Exception as e:
        logger.exception(f"Error en sincronización optimizada para item {meli_item.get('id', 'N/A')}")
        logger.info(f"Fallback a método legacy debido a excepción: {str(e)}")
        result = sync_or_update_barcode_from_meli_item_legacy(meli_item, auth_headers)
        result["strategy"] = "legacy_fallback_exception"
        return result


def sync_or_update_barcode_from_meli_item_legacy(meli_item, auth_headers=None):
    """
    Método legacy: Sincroniza o actualiza un código de barras usando el patrón anterior
    (Mantenido como fallback por compatibilidad)
    
    Args:
        meli_item (dict): Datos del producto de MercadoLibre
        auth_headers (dict): Headers de autenticación
        
    Returns:
        dict: Resultado de la operación
    """
    try:
        # Crear BarCodeMapper para obtener el EAN
        barcode_mapper = BarCodeMapper.from_meli_item(meli_item)
        
        if not barcode_mapper:
            return {
                "success": False, 
                "message": f"No se pudo procesar el código de barras para el item {meli_item.get('id', 'N/A')} - EAN no válido"
            }
        
        ean = barcode_mapper.idinternoean
        
        # Primero intentar actualizar (método anterior)
        logger.info(f"[LEGACY] Intentando actualizar código de barras para EAN {ean}...")
        update_result = update_barcode_from_meli_item(meli_item, auth_headers)
        
        if update_result["success"]:
            logger.info(f"[LEGACY] Código de barras actualizado exitosamente para EAN {ean}")
            return update_result
        
        # Si la actualización falla, intentar crear
        logger.info(f"[LEGACY] Actualización falló, intentando crear código de barras para EAN {ean}...")
        from .create import create_barcode_from_meli_item
        create_result = create_barcode_from_meli_item(meli_item, auth_headers)
        
        if create_result["success"]:
            logger.info(f"[LEGACY] Código de barras creado exitosamente para EAN {ean}")
            return create_result
        
        # Si ambos fallan, devolver el error más relevante
        if "already exists" in create_result.get("message", "").lower():
            return {
                "success": False,
                "message": f"Código de barras {ean} existe pero no se pudo actualizar. Update: {update_result['message']}, Create: {create_result['message']}"
            }
        
        return {
            "success": False,
            "message": f"No se pudo crear ni actualizar el código de barras {ean}. Update: {update_result['message']}, Create: {create_result['message']}"
        }
        
    except Exception as e:
        logger.exception(f"Error en sincronización legacy de código de barras para item {meli_item.get('id', 'N/A')}")
        return {"success": False, "message": f"Error en sincronización legacy: {e}"}


# Alias para compatibilidad - usar la versión optimizada por defecto
def sync_or_update_barcode_from_meli_item(meli_item, auth_headers=None, assume_new=False):
    """
    Punto de entrada principal - usa la versión optimizada por defecto
    """
    return sync_or_update_barcode_from_meli_item_optimized(meli_item, auth_headers, assume_new)
