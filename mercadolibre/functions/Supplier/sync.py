from mercadolibre.services.internal_api_service import get_internal_api_service
from mercadolibre.services.meli_service import get_meli_service
from project.config_db.repository import MeliConfigRepository


class MeliSupplierService:

    ENDPOINT_SUPPLIER = "wms/adapter/v2/supplier"
    # La logica por la cual pienso es consumir el servicio de sincronizacion de
    # clientes y actualizacion de clientes, como tal para los datos
