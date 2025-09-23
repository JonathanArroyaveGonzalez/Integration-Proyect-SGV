import logging
import requests
from django.conf import settings
from mercadolibre.utils.api_client import make_authenticated_request, get_meli_api_base_url
from mercadolibre.utils.mapper.data_mapper import ProductMapper
from .extract_id import extract_product_ids

logger = logging.getLogger(__name__)
BASE_URL = get_meli_api_base_url()
BASE_URL_WMS = getattr(settings, 'WMS_BASE_URL', "http://localhost:8000").rstrip('/')

def get_wms_base_url():
    """
    Obtiene la URL base del WMS desde configuración de Django o usa una por defecto
    """
    return getattr(settings, 'WMS_BASE_URL', "http://localhost:8000").rstrip('/')

def get_product_details(product_ids):
    """
    Obtiene los detalles de los productos desde MercadoLibre
    """
    if not product_ids:
        return []
    
    url = f"{BASE_URL}items?ids={','.join(product_ids[:20])}"
    try:
        response = make_authenticated_request("GET", url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error obteniendo productos de MercadoLibre: {e}")
        return []

def map_products_to_wms_format(meli_items):
    """
    Mapea productos de MercadoLibre al formato del WMS usando ProductMapper
    """
    wms_products = []
    required_fields = {"productoean", "descripcion", "referencia", "nuevoean"}
    
    for item in meli_items:
        try:
            product_data = item.get("body", item)
            product_mapper = ProductMapper.from_meli_item(product_data)
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

            if required_fields <= wms_product.keys():
                wms_products.append(wms_product)
            else:
                logger.warning(f"Producto omitido por campos faltantes: {product_data.get('id', 'N/A')}")
        except Exception as e:
            logger.error(f"Error mapeando producto {item.get('id', 'N/A')}: {e}")
            continue
    
    return wms_products

def send_products_to_wms(wms_products, auth_headers=None):
    """
    Envía productos al WMS usando el endpoint de artículos
    """
    if not wms_products:
        return {"success": False, "message": "No hay productos para enviar"}
    
    try:
        wms_url = f"{get_wms_base_url()}/wms/adapter/v2/art"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            **({ 'Authorization': auth_headers['Authorization']} if auth_headers and 'Authorization' in auth_headers else {})
        }

        response = requests.post(wms_url, json=wms_products, headers=headers)
        if response.status_code in (200, 201):
            return {
                "success": True,
                "message": f"Se sincronizaron {len(wms_products)} productos exitosamente",
                "data": response.json()
            }
        return {"success": False, "message": f"Error del WMS: {response.status_code} - {response.text}"}

    except requests.exceptions.RequestException as e:
        return {"success": False, "message": f"Error enviando al WMS: {e}"}

def sync_products_to_wms(auth_headers=None):
    """
    Sincroniza productos de MercadoLibre con el WMS
    """
    try:
        logger.info("Extrayendo IDs de productos...")
        product_ids = extract_product_ids()
        if not product_ids:
            return {"success": False, "message": "No se encontraron productos"}
        
        logger.info(f"Encontrados {len(product_ids)} productos")
        logger.info("Obteniendo detalles de productos...")
        meli_items = get_product_details(product_ids)
        if not meli_items:
            return {"success": False, "message": "No se pudieron obtener detalles de productos"}
        
        logger.info("Mapeando productos...")
        wms_products = map_products_to_wms_format(meli_items)
        
        logger.info("Enviando productos al WMS...")
        products_result = send_products_to_wms(wms_products, auth_headers)
        
        # Sincronizar códigos de barras después de sincronizar productos
        if products_result["success"]:
            logger.info("Sincronizando códigos de barras...")
            try:
                from ..BarCode.update import sync_or_update_barcode_from_meli_item
                
                barcodes_results = []
                barcodes_errors = []
                
                # Procesar cada item individualmente para manejar creación/actualización
                for item in meli_items:
                    try:
                        product_data = item.get("body", item)
                        barcode_result = sync_or_update_barcode_from_meli_item(product_data, auth_headers)
                        
                        if barcode_result["success"]:
                            barcodes_results.append({
                                "item_id": product_data.get("id", "N/A"),
                                "result": barcode_result
                            })
                        else:
                            barcodes_errors.append({
                                "item_id": product_data.get("id", "N/A"),
                                "error": barcode_result["message"]
                            })
                    except Exception as e:
                        logger.error(f"Error procesando código de barras para item {item.get('id', 'N/A')}: {e}")
                        barcodes_errors.append({
                            "item_id": item.get("id", "N/A"),
                            "error": str(e)
                        })
                
                # Crear resultado combinado
                barcodes_success = len(barcodes_results) > 0
                barcodes_message = f"Códigos de barras: {len(barcodes_results)} procesados exitosamente"
                
                if barcodes_errors:
                    barcodes_message += f", {len(barcodes_errors)} con errores"
                
                combined_result = {
                    "success": True,
                    "message": f"Productos: {products_result['message']}",
                    "products_data": products_result.get("data"),
                    "barcodes_success": barcodes_success,
                    "barcodes_message": barcodes_message,
                    "barcodes_processed": len(barcodes_results),
                    "barcodes_errors_count": len(barcodes_errors)
                }
                
                if barcodes_results:
                    combined_result["barcodes_data"] = barcodes_results
                
                if barcodes_errors:
                    combined_result["barcodes_errors"] = barcodes_errors
                
                combined_result["message"] += f" | {barcodes_message}"
                
                return combined_result
                
            except Exception as e:
                logger.error(f"Error sincronizando códigos de barras: {e}")
                # Si falla los códigos de barras, al menos devolver el éxito de productos
                products_result["barcodes_error"] = f"Error en códigos de barras: {e}"
                return products_result
        
        return products_result
    except Exception as e:
        logger.exception("Error en sincronización")
        return {"success": False, "message": f"Error en sincronización: {e}"}

# Funciones legacy mantenidas para compatibilidad
def sync_products():
    try:
        return get_product_details(extract_product_ids())
    except Exception as e:
        logger.error(f"Error sync_products legacy: {e}")
        return []

def map_products(meli_items):
    mapped_products = []
    for item in meli_items:
        try:
            product_data = item.get("body", item)
            mapped_products.append(ProductMapper.from_meli_item(product_data).to_dict())
        except Exception as e:
            logger.error(f"Error mapeando producto legacy: {e}")
            continue
    return mapped_products
