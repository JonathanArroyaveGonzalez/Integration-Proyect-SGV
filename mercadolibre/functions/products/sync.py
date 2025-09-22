from mercadolibre.utils.api_client import make_authenticated_request, get_meli_api_base_url
from .extract_id import extract_product_ids
import requests
import json
import os
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
    Mapea productos de MercadoLibre al formato del WMS (TdaWmsArt)
    """
    wms_products = []
    
    for item in meli_items:
        try:
            # Extraer datos del producto
            if "body" in item:
                product_data = item["body"]
            else:
                product_data = item
            
            # Mapear a formato WMS según el modelo TdaWmsArt
            wms_product = {
                "productoean": str(product_data.get("id", "")),  # Campo obligatorio
                "descripcion": product_data.get("title", "")[:250],  # Máximo 250 caracteres
                "referencia": str(product_data.get("id", "")),  # Campo obligatorio
                "inventariable": 1,  # Por defecto inventariable
                "um1": "UND",  # Unidad de medida por defecto
                "presentacion": product_data.get("condition", "new"),
                "costo": float(product_data.get("price", 0)),
                "preciounitario": float(product_data.get("price", 0)),
                "descripcioningles": product_data.get("title", "")[:250],
                "item": str(product_data.get("id", "")),
                "grupo": product_data.get("category_id", ""),
                "subgrupo": product_data.get("listing_type_id", ""),
                "nuevoean": str(product_data.get("id", "")),  # Campo obligatorio
                "tipo": "MERCADOLIBRE",
                "factor": 1.0,
                "bodega": "PRINCIPAL",
                "procedencia": "MERCADOLIBRE",
                "estadotransferencia": 0,
                "proveedor": "MERCADOLIBRE",
                "observacion": f"Sincronizado desde MercadoLibre - {product_data.get('permalink', '')}",
                "estado": 1 if product_data.get("status") == "active" else 0,
                "controla_status_calidad": 0,
            }
            
            # Solo agregar si tiene datos mínimos necesarios (campos obligatorios)
            if (wms_product["productoean"] and 
                wms_product["descripcion"] and 
                wms_product["referencia"] and 
                wms_product["nuevoean"]):
                wms_products.append(wms_product)
                
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
    Método legacy que mapea la información de los productos de MercadoLibre
    Params: meli_items: lista de items de MercadoLibre
    return: lista mapeada de productos
    """
    mapped_products = []
    for item in meli_items:
        if "body" in item:
            mapped_products.append(item["body"])
    return mapped_products

