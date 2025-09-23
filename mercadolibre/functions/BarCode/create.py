import logging
import requests
from django.conf import settings
from mercadolibre.utils.mapper.data_mapper import BarCodeMapper

logger = logging.getLogger(__name__)

def get_wms_base_url():
    """
    Obtiene la URL base del WMS desde configuración de Django o usa una por defecto
    """
    return getattr(settings, 'WMS_BASE_URL', "http://localhost:8000").rstrip('/')

def send_barcode_to_wms(barcode_data, auth_headers=None):
    """
    Envía un código de barras al WMS con optimizaciones de velocidad
    
    Args:
        barcode_data (dict): Datos del código de barras en formato BarCodeMapper
        auth_headers (dict): Headers de autenticación
        
    Returns:
        dict: Resultado de la operación
    """
    if not barcode_data:
        return {"success": False, "message": "No hay datos del código de barras para enviar"}
    
    try:
        wms_url = f"{get_wms_base_url()}/wms/base/v2/tRelacionCodbarras"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Connection': 'keep-alive'  # Optimización de conexión
        }
        
        # Agregar headers de autenticación si están disponibles
        if auth_headers and 'Authorization' in auth_headers:
            headers['Authorization'] = auth_headers['Authorization']

        # Usar timeout optimizado
        response = requests.post(wms_url, json=barcode_data, headers=headers, timeout=(3, 5))
        
        if response.status_code in (200, 201):
            return {
                "success": True,
                "message": "Código de barras creado exitosamente en el WMS",
                "data": response.json()
            }
        else:
            return {
                "success": False, 
                "message": f"Error del WMS: {response.status_code} - {response.text}"
            }

    except requests.exceptions.RequestException as e:
        return {"success": False, "message": f"Error enviando código de barras al WMS: {e}"}

def send_barcodes_to_wms(barcodes_data, auth_headers=None):
    """
    Envía múltiples códigos de barras al WMS usando el endpoint de tRelacionCodbarras
    
    Args:
        barcodes_data (list): Lista de datos de códigos de barras en formato BarCodeMapper
        auth_headers (dict): Headers de autenticación
        
    Returns:
        dict: Resultado de la operación
    """
    if not barcodes_data:
        return {"success": False, "message": "No hay códigos de barras para enviar"}
    
    try:
        wms_url = f"{get_wms_base_url()}/wms/base/v2/tRelacionCodbarras"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # Agregar headers de autenticación si están disponibles
        if auth_headers and 'Authorization' in auth_headers:
            headers['Authorization'] = auth_headers['Authorization']

        response = requests.post(wms_url, json=barcodes_data, headers=headers)
        
        if response.status_code in (200, 201):
            return {
                "success": True,
                "message": f"Se crearon {len(barcodes_data)} códigos de barras exitosamente en el WMS",
                "data": response.json()
            }
        else:
            return {
                "success": False, 
                "message": f"Error del WMS: {response.status_code} - {response.text}"
            }

    except requests.exceptions.RequestException as e:
        return {"success": False, "message": f"Error enviando códigos de barras al WMS: {e}"}

def create_barcode_from_meli_item_direct(meli_item, auth_headers=None):
    """
    Crea un código de barras directamente sin verificaciones previas.
    Optimizado para productos nuevos donde sabemos que el código no existe.
    
    Args:
        meli_item (dict): Datos del producto de MercadoLibre
        auth_headers (dict): Headers de autenticación
        
    Returns:
        dict: Resultado de la operación
    """
    try:
        # Crear BarCodeMapper directamente
        barcode_mapper = BarCodeMapper.from_meli_item(meli_item)
        
        if not barcode_mapper:
            return {
                "success": False, 
                "message": f"No se pudo procesar el código de barras para el item {meli_item.get('id', 'N/A')} - EAN no válido"
            }
        
        ean = barcode_mapper.idinternoean
        logger.info(f"Creando código de barras directamente para EAN {ean}...")
        
        # Enviar al WMS directamente
        result = send_barcode_to_wms(barcode_mapper.to_dict(), auth_headers)
        
        if result["success"]:
            logger.info(f"Código de barras creado exitosamente para EAN {ean}")
            return {
                "success": True,
                "message": f"Código de barras {ean} creado exitosamente",
                "data": result.get("data", {}),
                "strategy": "direct_create"
            }
        else:
            logger.error(f"Error creando código de barras para EAN {ean}: {result['message']}")
            return {
                "success": False,
                "message": f"Error creando código de barras {ean}: {result['message']}",
                "strategy": "direct_create_failed"
            }
        
    except Exception as e:
        logger.exception(f"Excepción creando código de barras para item {meli_item.get('id', 'N/A')}")
        return {
            "success": False, 
            "message": f"Error en creación directa: {e}",
            "strategy": "direct_create_exception"
        }


def create_barcode_from_meli_item(meli_item, auth_headers=None):
    """
    Crea un código de barras en el WMS a partir de un item de MercadoLibre
    
    Args:
        meli_item (dict): Datos del producto de MercadoLibre
        auth_headers (dict): Headers de autenticación
        
    Returns:
        dict: Resultado de la operación
    """
    try:
        logger.info(f"Creando código de barras para item: {meli_item.get('id', 'N/A')}")
        
        # Crear BarCodeMapper desde el item de MercadoLibre
        barcode_mapper = BarCodeMapper.from_meli_item(meli_item)
        
        if not barcode_mapper:
            return {
                "success": False, 
                "message": f"No se pudo crear el código de barras para el item {meli_item.get('id', 'N/A')} - EAN no válido"
            }
        
        # Convertir a diccionario
        barcode_data = barcode_mapper.to_dict()
        
        logger.info(f"Datos del código de barras mapeados: {barcode_data}")
        
        # Enviar al WMS
        result = send_barcode_to_wms(barcode_data, auth_headers)
        
        if result["success"]:
            logger.info(f"Código de barras creado exitosamente para item {meli_item.get('id', 'N/A')}")
        else:
            logger.error(f"Error creando código de barras para item {meli_item.get('id', 'N/A')}: {result['message']}")
        
        return result
        
    except Exception as e:
        logger.exception(f"Error en creación de código de barras para item {meli_item.get('id', 'N/A')}")
        return {"success": False, "message": f"Error en creación de código de barras: {e}"}

def create_barcodes_from_meli_items(meli_items, auth_headers=None):
    """
    Crea códigos de barras en el WMS a partir de múltiples items de MercadoLibre
    
    Args:
        meli_items (list): Lista de datos de productos de MercadoLibre
        auth_headers (dict): Headers de autenticación
        
    Returns:
        dict: Resultado de la operación
    """
    try:
        logger.info(f"Creando códigos de barras para {len(meli_items)} items")
        
        # Mapear todos los items a BarCodeMapper
        barcodes_data = []
        skipped_items = []
        
        for item in meli_items:
            try:
                # Obtener el producto real del wrapper si es necesario
                product_data = item.get("body", item)
                barcode_mapper = BarCodeMapper.from_meli_item(product_data)
                
                if barcode_mapper:
                    barcodes_data.append(barcode_mapper.to_dict())
                else:
                    skipped_items.append(product_data.get('id', 'N/A'))
                    
            except Exception as e:
                logger.error(f"Error mapeando item {item.get('id', 'N/A')}: {e}")
                skipped_items.append(item.get('id', 'N/A'))
                continue
        
        if not barcodes_data:
            return {
                "success": False, 
                "message": "No se pudieron crear códigos de barras válidos de los items proporcionados"
            }
        
        logger.info(f"Se mapearon {len(barcodes_data)} códigos de barras válidos")
        
        # Enviar todos los códigos de barras al WMS
        result = send_barcodes_to_wms(barcodes_data, auth_headers)
        
        # Agregar información sobre items omitidos
        if skipped_items:
            result["skipped_items"] = skipped_items
            result["message"] += f" (Se omitieron {len(skipped_items)} items sin EAN válido)"
        
        if result["success"]:
            logger.info(f"Códigos de barras creados exitosamente: {len(barcodes_data)} creados")
        else:
            logger.error(f"Error creando códigos de barras: {result['message']}")
        
        return result
        
    except Exception as e:
        logger.exception("Error en creación masiva de códigos de barras")
        return {"success": False, "message": f"Error en creación de códigos de barras: {e}"}