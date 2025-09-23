import logging
import requests
from django.conf import settings
from mercadolibre.utils.api_client import (
    make_authenticated_request,
    get_meli_api_base_url,
)
from mercadolibre.utils.mapper.data_mapper import ProductMapper
from .extract_id import extract_product_ids

logger = logging.getLogger(__name__)
BASE_URL = get_meli_api_base_url()
BASE_URL_WMS = getattr(settings, "WMS_BASE_URL", "http://localhost:8000").rstrip("/")

# Session global optimizada para reutilizar conexiones
_http_session = None

def get_optimized_session():
    """
    Obtiene una session HTTP optimizada con pool de conexiones y timeouts
    """
    global _http_session
    if _http_session is None:
        _http_session = requests.Session()
        # Configurar adaptador con pool de conexiones
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=10,
            pool_maxsize=20,
            max_retries=1
        )
        _http_session.mount('http://', adapter)
        _http_session.mount('https://', adapter)
        
        # Timeouts por defecto optimizados
        _http_session.timeout = (3, 5)  # (connect, read) timeout
    
    return _http_session


def build_optimized_headers(auth_headers=None):
    """
    Construye headers optimizados reutilizables
    """
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Connection": "keep-alive"  # Reutilizar conexiones
    }
    
    if auth_headers and "Authorization" in auth_headers:
        headers["Authorization"] = auth_headers["Authorization"]
    
    return headers


def get_wms_base_url():
    """
    Obtiene la URL base del WMS desde configuración de Django o usa una por defecto
    """
    return getattr(settings, "WMS_BASE_URL", "http://localhost:8000").rstrip("/")


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
                logger.warning(
                    f"Producto omitido por campos faltantes: {product_data.get('id', 'N/A')}"
                )
        except Exception as e:
            logger.error(f"Error mapeando producto {item.get('id', 'N/A')}: {e}")
            continue

    return wms_products


def send_products_to_wms(wms_products, auth_headers=None):
    """
    Envía productos al WMS usando el endpoint de artículos con optimizaciones
    """
    if not wms_products:
        return {"success": False, "message": "No hay productos para enviar"}

    try:
        wms_url = f"{get_wms_base_url()}/wms/adapter/v2/art"
        headers = build_optimized_headers(auth_headers)

        # Usar session optimizada con timeout
        session = get_optimized_session()
        response = session.post(wms_url, json=wms_products, headers=headers, timeout=(3, 5))
        
        if response.status_code in (200, 201):
            return {
                "success": True,
                "message": f"Se sincronizaron {len(wms_products)} productos exitosamente",
                "data": response.json(),
            }
        return {
            "success": False,
            "message": f"Error del WMS: {response.status_code} - {response.text}",
        }

    except requests.exceptions.RequestException as e:
        return {"success": False, "message": f"Error enviando al WMS: {e}"}


def process_barcodes_for_items(meli_items, auth_headers=None, assume_new=True):
    """
    Procesa códigos de barras para una lista de items de MercadoLibre
    Ahora usa optimizaciones por defecto para mejorar rendimiento
    
    Args:
        meli_items (list): Lista de items de MercadoLibre
        auth_headers (dict): Headers de autenticación
        assume_new (bool): Si True, asume productos nuevos (optimización por defecto)
        
    Returns:
        dict: Resultado del procesamiento de códigos de barras
    """
    logger.info(f"Sincronizando códigos de barras para {len(meli_items)} items (assume_new={assume_new})...")
    
    try:
        from ..BarCode.update import sync_or_update_barcode_from_meli_item

        barcodes_results = []
        barcodes_errors = []

        # Procesar cada item con optimización por defecto
        for item in meli_items:
            try:
                product_data = item.get("body", item)
                barcode_result = sync_or_update_barcode_from_meli_item(
                    product_data, auth_headers, assume_new=assume_new
                )

                if barcode_result["success"]:
                    barcodes_results.append(
                        {
                            "item_id": product_data.get("id", "N/A"),
                            "result": barcode_result,
                            "strategy": barcode_result.get("strategy", "unknown")
                        }
                    )
                else:
                    barcodes_errors.append(
                        {
                            "item_id": product_data.get("id", "N/A"),
                            "error": barcode_result["message"],
                            "strategy": barcode_result.get("strategy", "unknown")
                        }
                    )
            except Exception as e:
                logger.error(
                    f"Error procesando código de barras para item {item.get('id', 'N/A')}: {e}"
                )
                barcodes_errors.append(
                    {
                        "item_id": item.get("id", "N/A"), 
                        "error": str(e),
                        "strategy": "processing_error"
                    }
                )

        # Crear resultado del procesamiento de códigos de barras
        barcodes_success = len(barcodes_results) > 0
        barcodes_message = f"Códigos de barras: {len(barcodes_results)} procesados exitosamente"

        if barcodes_errors:
            barcodes_message += f", {len(barcodes_errors)} con errores"

        result = {
            "success": barcodes_success or len(barcodes_errors) == 0,
            "message": barcodes_message,
            "processed": len(barcodes_results),
            "errors": len(barcodes_errors),
            "results": barcodes_results,
            "error_details": barcodes_errors
        }

        # Agregar información de estrategias usadas
        strategies_used = {}
        for item in barcodes_results + barcodes_errors:
            strategy = item.get("strategy", "unknown")
            strategies_used[strategy] = strategies_used.get(strategy, 0) + 1
        
        result["strategies_used"] = strategies_used

        if barcodes_results:
            result["barcodes_data"] = barcodes_results

        if barcodes_errors:
            result["barcodes_errors"] = barcodes_errors

        return result

    except Exception as e:
        logger.error(f"Error sincronizando códigos de barras: {e}")
        return {
            "success": False,
            "message": f"Error en procesamiento de códigos de barras: {e}",
            "processed": 0,
            "errors": 1,
            "strategies_used": {"processing_error": 1}
        }


def sync_specific_products_to_wms_parallel(product_ids, auth_headers=None, assume_new=True):
    """
    Sincroniza productos específicos con paralelización para máxima velocidad
    
    Args:
        product_ids (list): Lista de IDs de productos específicos
        auth_headers (dict): Headers de autenticación
        assume_new (bool): Si True, asume que son productos nuevos (optimización)
        
    Returns:
        dict: Resultado de la sincronización
    """
    try:
        logger.info(f"Sincronización paralela de {len(product_ids)} productos específicos...")
        
        # Obtener detalles de productos específicos
        logger.info("Obteniendo detalles de productos específicos...")
        meli_items = get_product_details(product_ids)
        if not meli_items:
            return {
                "success": False,
                "message": "No se pudieron obtener detalles de productos específicos",
            }

        # Mapear productos una sola vez
        logger.info("Mapeando productos específicos...")
        wms_products = map_products_to_wms_format(meli_items)

        # PARALELIZACIÓN: Ejecutar productos y códigos de barras simultáneamente
        def send_products_task():
            """Tarea para enviar productos"""
            return send_products_to_wms(wms_products, auth_headers)
        
        def send_barcodes_task():
            """Tarea para procesar códigos de barras"""
            return process_barcodes_for_items_optimized(meli_items, auth_headers, assume_new)

        # Ejecutar ambas tareas en paralelo
        logger.info("Ejecutando productos y códigos de barras en paralelo...")
        from concurrent.futures import ThreadPoolExecutor
        
        with ThreadPoolExecutor(max_workers=2) as executor:
            # Enviar ambas tareas
            products_future = executor.submit(send_products_task)
            barcodes_future = executor.submit(send_barcodes_task)
            
            # Esperar resultados
            products_result = products_future.result(timeout=10)
            barcodes_result = barcodes_future.result(timeout=10)

        # Verificar éxito de productos
        if products_result["success"]:
            # Crear resultado combinado optimizado
            combined_result = {
                "success": True,
                "message": f"Productos específicos: {products_result['message']}",
                "products_data": products_result.get("data"),
                "barcodes_success": barcodes_result["success"],
                "barcodes_message": barcodes_result["message"],
                "barcodes_processed": barcodes_result["processed"],
                "barcodes_errors_count": barcodes_result["errors"],
                "assume_new": assume_new,
                "optimization_used": True,
                "parallel_execution": True
            }

            # Agregar datos de códigos de barras si existen
            if "barcodes_data" in barcodes_result:
                combined_result["barcodes_data"] = barcodes_result["barcodes_data"]

            if "barcodes_errors" in barcodes_result:
                combined_result["barcodes_errors"] = barcodes_result["barcodes_errors"]

            # Agregar información de estrategias
            if "strategies_used" in barcodes_result:
                combined_result["strategies_used"] = barcodes_result["strategies_used"]

            # Combinar mensajes
            combined_result["message"] += f" | {barcodes_result['message']}"

            return combined_result

        return products_result
        
    except Exception:
        logger.exception("Error en sincronización paralela de productos específicos")
        # Fallback a versión secuencial si falla la paralela
        logger.info("Fallback a sincronización secuencial...")
        return sync_specific_products_to_wms(product_ids, auth_headers, assume_new)


def sync_specific_products_to_wms(product_ids, auth_headers=None, assume_new=True):
    """
    Sincroniza productos específicos de MercadoLibre con el WMS
    Optimizado para productos nuevos sin verificaciones innecesarias
    
    Args:
        product_ids (list): Lista de IDs de productos específicos
        auth_headers (dict): Headers de autenticación
        assume_new (bool): Si True, asume que son productos nuevos (optimización)
        
    Returns:
        dict: Resultado de la sincronización
    """
    try:
        logger.info(f"Sincronizando {len(product_ids)} productos específicos...")
        
        # Obtener detalles de productos específicos
        logger.info("Obteniendo detalles de productos específicos...")
        meli_items = get_product_details(product_ids)
        if not meli_items:
            return {
                "success": False,
                "message": "No se pudieron obtener detalles de productos específicos",
            }

        # Mapear productos
        logger.info("Mapeando productos específicos...")
        wms_products = map_products_to_wms_format(meli_items)

        # Enviar productos al WMS
        logger.info("Enviando productos específicos al WMS...")
        products_result = send_products_to_wms(wms_products, auth_headers)

        # Sincronizar códigos de barras con optimización para productos nuevos
        if products_result["success"]:
            logger.info(f"Procesando códigos de barras para productos específicos (assume_new={assume_new})...")
            barcodes_result = process_barcodes_for_items_optimized(meli_items, auth_headers, assume_new)
            
            # Crear resultado combinado
            combined_result = {
                "success": True,
                "message": f"Productos específicos: {products_result['message']}",
                "products_data": products_result.get("data"),
                "barcodes_success": barcodes_result["success"],
                "barcodes_message": barcodes_result["message"],
                "barcodes_processed": barcodes_result["processed"],
                "barcodes_errors_count": barcodes_result["errors"],
                "assume_new": assume_new,
                "optimization_used": True
            }

            # Agregar datos de códigos de barras si existen
            if "barcodes_data" in barcodes_result:
                combined_result["barcodes_data"] = barcodes_result["barcodes_data"]

            if "barcodes_errors" in barcodes_result:
                combined_result["barcodes_errors"] = barcodes_result["barcodes_errors"]

            # Agregar información de estrategias
            if "strategies_used" in barcodes_result:
                combined_result["strategies_used"] = barcodes_result["strategies_used"]

            # Combinar mensajes
            combined_result["message"] += f" | {barcodes_result['message']}"

            return combined_result

        return products_result
    except Exception as e:
        logger.exception("Error en sincronización de productos específicos")
        return {"success": False, "message": f"Error en sincronización específica: {e}"}


def process_barcodes_for_items_optimized(meli_items, auth_headers=None, assume_new=False):
    """
    Procesa códigos de barras para una lista de items con optimización
    
    Args:
        meli_items (list): Lista de items de MercadoLibre
        auth_headers (dict): Headers de autenticación
        assume_new (bool): Si True, asume que son productos nuevos para crear directamente
        
    Returns:
        dict: Resultado del procesamiento de códigos de barras
    """
    logger.info(f"Sincronizando códigos de barras para {len(meli_items)} items (optimización: assume_new={assume_new})...")
    
    try:
        from ..BarCode.update import sync_or_update_barcode_from_meli_item

        barcodes_results = []
        barcodes_errors = []

        # Procesar cada item con la estrategia optimizada
        for item in meli_items:
            try:
                product_data = item.get("body", item)
                barcode_result = sync_or_update_barcode_from_meli_item(
                    product_data, auth_headers, assume_new=assume_new
                )

                if barcode_result["success"]:
                    barcodes_results.append(
                        {
                            "item_id": product_data.get("id", "N/A"),
                            "result": barcode_result,
                            "strategy": barcode_result.get("strategy", "unknown")
                        }
                    )
                else:
                    barcodes_errors.append(
                        {
                            "item_id": product_data.get("id", "N/A"),
                            "error": barcode_result["message"],
                            "strategy": barcode_result.get("strategy", "unknown")
                        }
                    )
            except Exception as e:
                logger.error(
                    f"Error procesando código de barras para item {item.get('id', 'N/A')}: {e}"
                )
                barcodes_errors.append(
                    {
                        "item_id": item.get("id", "N/A"), 
                        "error": str(e),
                        "strategy": "processing_error"
                    }
                )

        # Crear resultado del procesamiento de códigos de barras
        barcodes_success = len(barcodes_results) > 0
        barcodes_message = f"Códigos de barras: {len(barcodes_results)} procesados exitosamente"

        if barcodes_errors:
            barcodes_message += f", {len(barcodes_errors)} con errores"

        result = {
            "success": barcodes_success or len(barcodes_errors) == 0,
            "message": barcodes_message,
            "processed": len(barcodes_results),
            "errors": len(barcodes_errors),
            "results": barcodes_results,
            "error_details": barcodes_errors,
            "assume_new": assume_new
        }

        # Agregar información de estrategias usadas
        strategies_used = {}
        for item in barcodes_results + barcodes_errors:
            strategy = item.get("strategy", "unknown")
            strategies_used[strategy] = strategies_used.get(strategy, 0) + 1
        
        result["strategies_used"] = strategies_used

        if barcodes_results:
            result["barcodes_data"] = barcodes_results

        if barcodes_errors:
            result["barcodes_errors"] = barcodes_errors

        return result

    except Exception as e:
        logger.error(f"Error sincronizando códigos de barras optimizados: {e}")
        return {
            "success": False,
            "message": f"Error en procesamiento optimizado de códigos de barras: {e}",
            "processed": 0,
            "errors": 1,
            "strategies_used": {"processing_error": 1},
            "assume_new": assume_new
        }


def sync_products_to_wms_parallel(auth_headers=None, assume_new=True):
    """
    Sincroniza productos de MercadoLibre con el WMS usando paralelización optimizada
    
    Args:
        auth_headers (dict): Headers de autenticación
        assume_new (bool): Si True, asume productos nuevos para optimizar
        
    Returns:
        dict: Resultado de la sincronización
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
            return {
                "success": False,
                "message": "No se pudieron obtener detalles de productos",
            }

        logger.info("Mapeando productos...")
        wms_products = map_products_to_wms_format(meli_items)

        # PARALELIZACIÓN: Ejecutar productos y códigos de barras simultáneamente
        def send_products_task():
            """Tarea para enviar productos"""
            return send_products_to_wms(wms_products, auth_headers)
        
        def send_barcodes_task():
            """Tarea para procesar códigos de barras optimizados"""
            return process_barcodes_for_items_optimized(meli_items, auth_headers, assume_new)

        # Ejecutar ambas tareas en paralelo
        logger.info("Ejecutando productos y códigos de barras en paralelo (masivo optimizado)...")
        from concurrent.futures import ThreadPoolExecutor
        
        with ThreadPoolExecutor(max_workers=2) as executor:
            # Enviar ambas tareas
            products_future = executor.submit(send_products_task)
            barcodes_future = executor.submit(send_barcodes_task)
            
            # Esperar resultados
            products_result = products_future.result(timeout=15)
            barcodes_result = barcodes_future.result(timeout=15)

        # Verificar éxito de productos
        if products_result["success"]:
            # Crear resultado combinado optimizado
            combined_result = {
                "success": True,
                "message": f"Productos masivos: {products_result['message']}",
                "products_data": products_result.get("data"),
                "barcodes_success": barcodes_result["success"],
                "barcodes_message": barcodes_result["message"],
                "barcodes_processed": barcodes_result["processed"],
                "barcodes_errors_count": barcodes_result["errors"],
                "assume_new": assume_new,
                "optimization_used": True,
                "parallel_execution": True,
                "sync_type": "massive_parallel"
            }

            # Agregar datos de códigos de barras si existen
            if "barcodes_data" in barcodes_result:
                combined_result["barcodes_data"] = barcodes_result["barcodes_data"]

            if "barcodes_errors" in barcodes_result:
                combined_result["barcodes_errors"] = barcodes_result["barcodes_errors"]

            # Agregar información de estrategias
            if "strategies_used" in barcodes_result:
                combined_result["strategies_used"] = barcodes_result["strategies_used"]

            # Combinar mensajes
            combined_result["message"] += f" | {barcodes_result['message']}"

            return combined_result

        return products_result
        
    except Exception:
        logger.exception("Error en sincronización paralela masiva")
        # Fallback a versión secuencial si falla la paralela
        logger.info("Fallback a sincronización masiva secuencial...")
        return sync_products_to_wms(auth_headers)


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
            return {
                "success": False,
                "message": "No se pudieron obtener detalles de productos",
            }

        logger.info("Mapeando productos...")
        wms_products = map_products_to_wms_format(meli_items)

        logger.info("Enviando productos al WMS...")
        products_result = send_products_to_wms(wms_products, auth_headers)

        # Sincronizar códigos de barras después de sincronizar productos con optimización
        if products_result["success"]:
            # Procesar códigos de barras usando optimización por defecto (assume_new=True)
            barcodes_result = process_barcodes_for_items(meli_items, auth_headers, assume_new=True)
            
            # Crear resultado combinado
            combined_result = {
                "success": True,
                "message": f"Productos: {products_result['message']}",
                "products_data": products_result.get("data"),
                "barcodes_success": barcodes_result["success"],
                "barcodes_message": barcodes_result["message"],
                "barcodes_processed": barcodes_result["processed"],
                "barcodes_errors_count": barcodes_result["errors"],
            }

            # Agregar datos de códigos de barras si existen
            if "barcodes_data" in barcodes_result:
                combined_result["barcodes_data"] = barcodes_result["barcodes_data"]

            if "barcodes_errors" in barcodes_result:
                combined_result["barcodes_errors"] = barcodes_result["barcodes_errors"]

            # Combinar mensajes
            combined_result["message"] += f" | {barcodes_result['message']}"

            return combined_result

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
