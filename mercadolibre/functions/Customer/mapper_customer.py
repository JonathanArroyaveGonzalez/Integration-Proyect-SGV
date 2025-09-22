import requests
import logging

logger = logging.getLogger(__name__)


def ml_customer_to_wms_format(ml_customer_data: dict):
    """
    Convierte datos de cliente ML al formato que espera wmsAdapterV2

    Args:
        ml_customer_data (dict): Datos crudos de MercadoLibre API

    Returns:
        dict: Formato compatible con TdaWmsClt
    """

    try:
        nit = ml_customer_data.get("identification", {}).get("number")
        nombrecliente = f"{ml_customer_data.get('first_name', '')} {ml_customer_data.get('last_name', '')}".strip()
        nickname = ml_customer_data.get("nickname", nombrecliente)
        direccion = ml_customer_data.get("address", {}).get("address")
        ciudad = ml_customer_data.get("address", {}).get("city")
        codigopais = ml_customer_data.get("country_id")
        zip_code = ml_customer_data.get("address", {}).get("zip_code")
        telefono = None
        phone_obj = ml_customer_data.get("phone")
        if phone_obj and phone_obj.get("area_code") and phone_obj.get("number"):
            telefono = f"{phone_obj.get('area_code')}{phone_obj.get('number')}"
        email = ml_customer_data.get("email")
        fecharegistro = ml_customer_data.get("registration_date")
        item = str(ml_customer_data.get("id"))

        mapper_customer = {
            "nit": nit,
            "nombrecliente": nickname,
            "direccion": direccion,
            "fecharegistro": fecharegistro,
            "codigopais": codigopais,
            "telefono": telefono,
            "ciudad": ciudad,
            "notas": None,
            "contacto": nombrecliente,
            "email": email,
            "zipcode": zip_code,
            "item": item,
            "isactivocliente": 1,
        }

        mapper_customer = {k: v for k, v in mapper_customer.items() if v is not None}

        return mapper_customer

    except Exception as e:
        logger.error(f"Error mapeando customer {e}")
        return None
