import logging
import os
import requests
from mercadolibre.utils.api_client import (
    get_meli_api_base_url,
    make_authenticated_request,
)
from mercadolibre.utils.mappers import customer, data_mapper
import settings

logger = logging.getLogger(__name__)


def fetch_ml_user(user_id: str) -> dict | None:
    """
    Obtiene datos de usuario desde MercadoLibre API.
    Args:
        user_id (str): ID del usuario en MercadoLibre
    Returns:
        dict | None: Datos del usuario o None si ocurre error
    """
    try:
        logger.info(f"Obteniendo datos ML para usuario {user_id}")
        base_url = get_meli_api_base_url()
        url = f"{base_url}users/{user_id}"
        response = make_authenticated_request("GET", url, timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Error ML {response.status_code}: {response.text}")
            return None
    except Exception as e:
        logger.error(f"Error obteniendo usuario {user_id} de ML: {str(e)}")
        return None


def get_wms_base_url():
    """
    Obtiene la URL base del WMS desde configuración de Django o usa una por defecto
    """
    return getattr(settings, "WMS_BASE_URL", "http://localhost:8000").rstrip("/")


def create_customer_in_wms(ml_customer_id: str, auth_headers=None) -> dict:
    """
    Crea un cliente en WMS usando datos de MercadoLibre.
    Args:
        ml_customer_id (str): ID del cliente en MercadoLibre
        auth_headers (dict): Headers de autorización para el WMS
    Returns:
        dict: Respuesta en formato WMS {"created": [...], "errors": [...]}
    """
    try:
        # Validar entrada
        if not ml_customer_id or not ml_customer_id.strip():
            return {"created": [], "errors": ["ID de cliente requerido"]}

        # Obtener datos de MercadoLibre
        ml_data = fetch_ml_user(ml_customer_id)
        if not ml_data:
            return {"created": [], "errors": ["Cliente no encontrado en MercadoLibre"]}

        # Mapear datos
        mapped_data = data_mapper.CustomerMapper.from_meli_customer(ml_data)
        if not mapped_data:
            return {
                "created": [],
                "errors": ["Error transformando datos de MercadoLibre"],
            }

        # Configurar headers del request al WMS
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        # Usar auth_headers si se proporcionan, sino usar la variable de entorno
        if auth_headers and "Authorization" in auth_headers:
            headers["Authorization"] = auth_headers["Authorization"]
        # else:
        #     # Fallback a variable de entorno si no se pasan auth_headers
        #     wms_token = os.getenv("WMS_API_TOKEN")
        #     if wms_token:
        #         headers["Authorization"] = wms_token

        wms_base_url = get_wms_base_url()
        wms_url = f"{wms_base_url}/wms/adapter/v2/clt"

        # Hacer request al WMS
        print(f"Headers {headers}")
        response = requests.post(
            wms_url, json=[mapped_data.to_dict()], headers=headers, timeout=30
        )
        response.raise_for_status()
        wms_response = response.json()
        logger.info(f"Cliente ML {ml_customer_id} procesado: {wms_response}")
        return wms_response

    except requests.HTTPError as e:
        logger.error(f"Error HTTP WMS: {e}")
        return {
            "created": [],
            "errors": [f"Error WMS HTTP {e.response.status_code}: {e.response.text}"],
        }
    except requests.RequestException as e:
        logger.error(f"Error de conexión WMS: {e}")
        return {"created": [], "errors": [f"Error de conexión con WMS: {str(e)}"]}
    except Exception as e:
        logger.error(f"Error inesperado creando cliente: {e}")
        return {"created": [], "errors": [f"Error interno: {str(e)}"]}


def update_customer_in_wms(ml_customer_id: str, auth_headers=None) -> dict:
    """
    Actualiza un cliente en WMS usando datos de MercadoLibre.
    Args:
        ml_customer_id (str): ID del cliente en MercadoLibre
        auth_headers (dict): Headers de autorización para el WMS
    Returns:
        dict: Respuesta en formato WMS {"created": [...], "errors": [...]}
    """
    try:
        # Validar entrada
        if not ml_customer_id or not ml_customer_id.strip():
            return {"updated": [], "errors": ["ID de cliente requerido"]}

        # Obtener datos de MercadoLibre
        ml_data = fetch_ml_user(ml_customer_id)
        if not ml_data:
            return {"updated": [], "errors": ["Cliente no encontrado en MercadoLibre"]}

        # Mapear datos
        mapped_data = data_mapper.CustomerMapper.from_meli_customer(ml_data)
        print(mapped_data)
        if not mapped_data:
            print("ERROR")
            return {
                "updated": [],
                "errors": ["Error transformando datos de MercadoLibre"],
            }

        # Configurar headers del request al WMS
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        # Usar auth_headers si se proporcionan, sino usar la variable de entorno
        if auth_headers and "Authorization" in auth_headers:
            headers["Authorization"] = auth_headers["Authorization"]

        wms_base_url = get_wms_base_url()
        # Nota: Para update podrías usar PUT/PATCH si el WMS lo soporta
        # Por ahora uso el mismo endpoint que create
        wms_url = f"{wms_base_url}/wms/adapter/v2/clt"

        # Hacer request al WMS
        response = requests.put(
            wms_url,
            json=[mapped_data.to_dict()],
            headers=headers,
        )
        print(f"{response}")
        response.raise_for_status()
        wms_response = response.json()
        logger.info(f"Cliente ML {ml_customer_id} actualizado: {wms_response}")
        return wms_response

    except requests.HTTPError as e:
        logger.error(f"Error HTTP WMS: {e}")
        return {
            "updated": [],
            "errors": [f"Error WMS HTTP {e.response.status_code}: {e.response.text}"],
        }
    except requests.RequestException as e:
        logger.error(f"Error de conexión WMS: {e}")
        return {"created": [], "errors": [f"Error de conexión con WMS: {str(e)}"]}
    except Exception as e:
        logger.error(f"Error inesperado actualizando cliente: {e}")
        return {"created": [], "errors": [f"Error interno: {str(e)}"]}
