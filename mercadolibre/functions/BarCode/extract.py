import logging
from mercadolibre.utils.mapper.data_mapper import BarCodeMapper

logger = logging.getLogger(__name__)

def extract_barcodes_from_meli_items(meli_items):
    """
    Extrae códigos de barras válidos de una lista de items de MercadoLibre
    
    Args:
        meli_items (list): Lista de items de MercadoLibre
        
    Returns:
        tuple: (lista_barcodes_validos, lista_items_omitidos)
    """
    valid_barcodes = []
    skipped_items = []
    
    for item in meli_items:
        try:
            # Obtener el producto real del wrapper si es necesario
            product_data = item.get("body", item)
            
            # Crear BarCodeMapper desde el item
            barcode_mapper = BarCodeMapper.from_meli_item(product_data)
            
            if barcode_mapper:
                valid_barcodes.append({
                    'meli_item': product_data,
                    'barcode_mapper': barcode_mapper,
                    'barcode_data': barcode_mapper.to_dict()
                })
                logger.info(f"Código de barras extraído para item {product_data.get('id', 'N/A')}: {barcode_mapper.idinternoean}")
            else:
                skipped_items.append(product_data.get('id', 'N/A'))
                logger.warning(f"Item {product_data.get('id', 'N/A')} omitido - no tiene EAN válido")
                
        except Exception as e:
            logger.error(f"Error extrayendo código de barras del item {item.get('id', 'N/A')}: {e}")
            skipped_items.append(item.get('id', 'N/A'))
            continue
    
    logger.info(f"Extracción completada: {len(valid_barcodes)} códigos válidos, {len(skipped_items)} items omitidos")
    return valid_barcodes, skipped_items

def extract_barcode_from_meli_item(meli_item):
    """
    Extrae el código de barras de un único item de MercadoLibre
    
    Args:
        meli_item (dict): Item de MercadoLibre
        
    Returns:
        dict: Información del código de barras extraído o None si no es válido
    """
    try:
        # Obtener el producto real del wrapper si es necesario
        product_data = meli_item.get("body", meli_item)
        
        # Crear BarCodeMapper desde el item
        barcode_mapper = BarCodeMapper.from_meli_item(product_data)
        
        if barcode_mapper:
            logger.info(f"Código de barras extraído para item {product_data.get('id', 'N/A')}: {barcode_mapper.idinternoean}")
            return {
                'meli_item': product_data,
                'barcode_mapper': barcode_mapper,
                'barcode_data': barcode_mapper.to_dict()
            }
        else:
            logger.warning(f"Item {product_data.get('id', 'N/A')} no tiene EAN válido")
            return None
            
    except Exception as e:
        logger.error(f"Error extrayendo código de barras del item {meli_item.get('id', 'N/A')}: {e}")
        return None

def get_ean_from_meli_item(meli_item):
    """
    Extrae únicamente el EAN de un item de MercadoLibre
    
    Args:
        meli_item (dict): Item de MercadoLibre
        
    Returns:
        str: EAN del producto o None si no existe
    """
    try:
        # Obtener el producto real del wrapper si es necesario
        product_data = meli_item.get("body", meli_item)
        
        # Extraer atributos en un dict por ID
        attributes = {attr["id"]: attr.get("value_name") for attr in product_data.get("attributes", [])}
        
        # EAN / SKU
        ean = attributes.get("GTIN") or attributes.get("SELLER_SKU")
        
        if ean:
            logger.debug(f"EAN extraído para item {product_data.get('id', 'N/A')}: {ean}")
            return ean
        else:
            logger.warning(f"No se encontró EAN para item {product_data.get('id', 'N/A')}")
            return None
            
    except Exception as e:
        logger.error(f"Error extrayendo EAN del item {meli_item.get('id', 'N/A')}: {e}")
        return None

def filter_items_with_valid_ean(meli_items):
    """
    Filtra items de MercadoLibre que tengan EAN válido
    
    Args:
        meli_items (list): Lista de items de MercadoLibre
        
    Returns:
        tuple: (items_con_ean, items_sin_ean)
    """
    items_with_ean = []
    items_without_ean = []
    
    for item in meli_items:
        try:
            # Obtener el producto real del wrapper si es necesario
            product_data = item.get("body", item)
            
            ean = get_ean_from_meli_item(product_data)
            
            if ean:
                items_with_ean.append(item)
            else:
                items_without_ean.append(item)
                
        except Exception as e:
            logger.error(f"Error filtrando item {item.get('id', 'N/A')}: {e}")
            items_without_ean.append(item)
            continue
    
    logger.info(f"Filtrado completado: {len(items_with_ean)} items con EAN, {len(items_without_ean)} items sin EAN")
    return items_with_ean, items_without_ean

def validate_barcode_data(barcode_data):
    """
    Valida que los datos del código de barras estén completos
    
    Args:
        barcode_data (dict): Datos del código de barras
        
    Returns:
        tuple: (es_valido, lista_errores)
    """
    errors = []
    required_fields = ['idinternoean', 'codbarrasasignado']
    
    for field in required_fields:
        if not barcode_data.get(field):
            errors.append(f"Campo requerido '{field}' está vacío o no existe")
    
    # Validaciones adicionales
    if barcode_data.get('cantidad') is not None and barcode_data['cantidad'] < 0:
        errors.append("La cantidad no puede ser negativa")
    
    is_valid = len(errors) == 0
    
    if is_valid:
        logger.debug(f"Datos de código de barras válidos para EAN: {barcode_data.get('idinternoean')}")
    else:
        logger.warning(f"Datos de código de barras inválidos: {errors}")
    
    return is_valid, errors
