"""
Servicio de consultas internas para WMS y Transprensa.
"""

from typing import Dict, Any, Optional
from wmsAdapterV2.functions.carrier.save_guide import save_guide
from wmsAdapterV2.functions.carrier.cancel_guide import cancel_guide
from wmsAdapterV2.functions.carrier.read_data_guide import read_data_guide
from settings.settings import global_settings

_internal_query_service_instance: Optional["InternalQueryService"] = None
database_name_wms = global_settings.DATABASE_NAME



class InternalQueryService:
    """Servicio para consultas internas a WMS y Transprensa."""

    def __init__(self, *, db_name: str= database_name_wms):
        """
        Inicializa el servicio de consultas interno.

        Args:
            db_name: Nombre de la base de datos para wmsAdapterV2
            transprensa_client: Cliente para consumir WS de Transprensa
        """
        self.db_name = db_name

    def guardar_pdf_guia(
        self, delivery_number: str, picking: str, pdf_base64: str
    ) -> Dict[str, Any]:
        """
        Guarda el PDF de una guía usando wmsAdapterV2.

        Args:
            delivery_number: Número de entrega
            picking: Código de picking
            pdf_base64: PDF en base64

        Returns:
            Dict con resultado de la operación
        """
        try:
            return save_guide(self.db_name, delivery_number, picking, pdf_base64)
        except Exception as e:
            return {
                "success": False,
                "message": f"Error al guardar guía: {str(e)}",
                "data": None,
            }

    def anular_guia(self, delivery_number: str, picking: str) -> Dict[str, Any]:
        """
        Anula una guía usando wmsAdapterV2.

        Args:
            delivery_number: Número de entrega
            picking: Código de picking

        Returns:
            Dict con resultado de la operación
        """
        try:
            return cancel_guide(self.db_name, delivery_number, picking)
        except Exception as e:
            return {
                "success": False,
                "message": f"Error al anular guía: {str(e)}",
                "data": None,
            }

    def getGuiaData(self, picking: str, bigpedido: str) -> Dict[str, Any]:
        """
        Obtiene datos completos de una guía combinando información básica y detallada.
        Ejecuta las consultas de forma secuencial.

        Args:
            picking: Código de picking
            bigpedido: Número de pedido

        Returns:
            Dict con estructura unificada que contiene:
            - Datos básicos (is_detail_0)
            - Datos detallados (is_detail_1)
        """
        try:
            # Obtener datos sin detalle
            data_sin_detalle = read_data_guide(
                database=self.db_name, picking=picking, bigpedido=bigpedido, is_detail=0
            )

            # Obtener datos con detalle
            data_con_detalle = read_data_guide(
                database=self.db_name, picking=picking, bigpedido=bigpedido, is_detail=1
            )

            # Construir respuesta
            result = {
                "picking": picking,
                "bigpedido": bigpedido,
                "is_detail_0": {
                    "success": True,
                    "message": "Guía obtenida exitosamente",
                    "data": data_sin_detalle if data_sin_detalle else [],
                },
                "is_detail_1": {
                    "success": True,
                    "message": "Guía obtenida exitosamente",
                    "data": data_con_detalle if data_con_detalle else [],
                },
            }

            return result

        except Exception as e:
            return {
                "picking": picking,
                "bigpedido": bigpedido,
                "error": str(e),
                "is_detail_0": {"success": False, "data": []},
                "is_detail_1": {"success": False, "data": []},
            }


def get_internal_query_service() -> InternalQueryService:
    """
    Obtiene la instancia singleton del servicio de consultas internas.

    Returns:
        InternalQueryService: Instancia singleton del servicio
    """
    global _internal_query_service_instance
    if _internal_query_service_instance is None:
        _internal_query_service_instance = InternalQueryService()
    return _internal_query_service_instance
