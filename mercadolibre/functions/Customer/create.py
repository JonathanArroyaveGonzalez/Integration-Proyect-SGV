"""
Cliente HTTP para comunicación con MercadoLibre API
"""

import logging
import os
from urllib import request
import requests
from mercadolibre.functions.Customer import mapper_customer
from mercadolibre.utils.api_client import (
    get_meli_api_base_url,
    make_authenticated_request,
)
from wmsAdapterV2.functions.Customer.create import create_clt

logger = logging.getLogger(__name__)


def fetch_ml_user(user_id):
    """
    Obtiene datos de usuario desde MercadoLibre API

    Args:
        user_id (str): ID del usuario en MercadoLibre

    Returns:
        dict: Datos del usuario o None si error
    """
    try:
        logger.info(f"Obteniendo datos ML para usuario {user_id}")

        # Construir URL
        base_url = get_meli_api_base_url()
        url = f"{base_url}users/{user_id}"

        # Hacer petición (tu función maneja auth automáticamente)
        response = make_authenticated_request("GET", url, timeout=30)

        if response.status_code == 200:
            logger.info(f"Datos ML obtenidos exitosamente para el cliente {user_id}")
            return response.json()
        else:
            logger.error(
                f"Error ML {response.status_code} para usuario {user_id}: {response.text}"
            )
            return None

    except Exception as e:
        logger.error(f"Error obteniendo usuario {user_id} de ML: {str(e)}")
        return None


def create_customer_from_ml(ml_customer_id, db_name="default"):
    """
    Crea cliente en WMS usando datos de MercadoLibre

    Args:
        ml_customer_id (str): ID del cliente en MercadoLibre
        db_name (str): alias de la base de datos WMS (default: "default")

    Returns:
        tuple: (mapped_data, result)
            mapped_data: datos mapeados listos para WMS
            result: mensaje de creación ('created successfully' o error)
    """
    try:
        logger.info(f"Iniciando creación cliente desde ML: {ml_customer_id}")

        ml_data = fetch_ml_user(ml_customer_id)
        if not ml_data:
            return None, "Usuario no encontrado en MercadoLibre"

        mapped_data = mapper_customer.ml_customer_to_wms_format(ml_data)
        if not mapped_data:
            return None, "Error transformando datos de MercadoLibre"

        # result = create_clt(request=None, db_name=db_name, request_data=mapped_data)
        # endpoint
        wms_base_url = wms_base_url = os.getenv("WMS_BASE_URL")
        wms_url = f"{wms_base_url}/wms/adapter/v2/clt"
        result = request
        logger.info(
            f"Cliente ML {ml_customer_id} procesado con item {mapped_data['item']}, resultado: {result}"
        )
        return (result,)

    except Exception as e:
        logger.error(f"Error creando cliente ML {ml_customer_id}: {str(e)}")
        return None, f"Error: {str(e)}"


def send_customer_to_wms(wms_products, auth_headers=None):
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
        wms_base_url = os.getenv("WMS_BASE_URL")
        wms_url = f"{wms_base_url}/wms/adapter/v2/art"

        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        # Agregar headers de autorización si están disponibles
        if auth_headers and "Authorization" in auth_headers:
            headers["Authorization"] = auth_headers["Authorization"]

        # Enviar productos como lista (formato esperado por el WMS)
        payload = wms_products

        response = requests.post(wms_url, json=payload, headers=headers)

        if response.status_code in [200, 201]:
            return {
                "success": True,
                "message": f"Se sincronizaron {len(wms_products)} productos exitosamente",
                "data": response.json(),
            }
        else:
            return {
                "success": False,
                "message": f"Error del WMS: {response.status_code} - {response.text}",
            }

    except Exception as e:
        return {"success": False, "message": f"Error enviando al WMS: {str(e)}"}
