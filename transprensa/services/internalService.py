"""
Servicio de consultas internas para WMS y Transprensa.
"""

from typing import Dict, Any, Optional, List
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
from wmsAdapterV2.functions.carrier.save_guide import save_guide
from wmsAdapterV2.functions.carrier.cancel_guide import cancel_guide
from wmsAdapterV2.functions.carrier.read_data_guide import read_data_guide
from transprensa.services.transprensaService import get_transprensa_service
from settings.settings import global_settings

_internal_query_service_instance: Optional["InternalQueryService"] = None
_GUIA_COMPARATIVA_CACHE: Dict[str, tuple] = {}
_GUIA_CACHE_TTL_SECONDS = 900
_QUERY_EXECUTOR = ThreadPoolExecutor(max_workers=10, thread_name_prefix="query_")
database_name_wms = global_settings.DATABASE_NAME


class MockRequest:
    """Simula un objeto request de Django para wmsAdapterV2."""

    def __init__(self, get_params=None, body_params=None):
        self.GET = {}
        if get_params:
            for key, value in get_params.items():
                self.GET[key] = value if isinstance(value, list) else [str(value)]

        self.body = body_params or b""
        self.method = "GET"


class InternalQueryService:
    """Servicio para consultas internas a WMS y Transprensa."""

    def __init__(self, *, db_name: str, transprensa_client):
        """
        Inicializa el servicio de consultas interno.

        Args:
            db_name: Nombre de la base de datos para wmsAdapterV2
            transprensa_client: Cliente para consumir WS de Transprensa
        """
        self.db_name = db_name
        self.tp = transprensa_client

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

    async def getGuiaData(self, picking: str, bigpedido: str) -> Dict[str, Any]:
        """
        Obtiene datos completos de una guía combinando información básica y detallada.
        Ejecuta ambas consultas en paralelo y maneja caché para optimizar rendimiento.

        Args:
            picking: Código de picking
            bigpedido: Número de pedido

        Returns:
            Dict con estructura unificada que contiene:
            - Datos básicos (is_detail_0)
            - Datos detallados (is_detail_1)
        """
        cache_key = f"{picking}#{bigpedido}"

        # Verificar caché primero
        if cache_key in _GUIA_COMPARATIVA_CACHE:
            cached_data, timestamp = _GUIA_COMPARATIVA_CACHE[cache_key]
            if time.time() - timestamp < _GUIA_CACHE_TTL_SECONDS:
                return cached_data

        try:
            # Función auxiliar para ejecutar read_data_guide de forma asíncrona
            async def execute_query(is_detail: bool) -> Dict[str, Any]:
                try:
                    data = await asyncio.get_event_loop().run_in_executor(
                        _QUERY_EXECUTOR,
                        read_data_guide,
                        self.db_name,
                        picking,
                        bigpedido,
                        1 if is_detail else 0,
                    )
                    return {
                        "success": True,
                        "message": "Guía obtenida exitosamente",
                        "data": data if data else [],
                    }
                except Exception as e:
                    return {
                        "success": False,
                        "message": f"Error al leer datos de guía: {str(e)}",
                        "data": [],
                    }

            # Ejecutar ambas consultas en paralelo
            data_sin_detalle, data_con_detalle = await asyncio.gather(
                execute_query(False), execute_query(True), return_exceptions=False
            )

            result = {
                "picking": picking,
                "bigpedido": bigpedido,
                "is_detail_0": {
                    "success": data_sin_detalle.get("success"),
                    "message": data_sin_detalle.get("message"),
                    "data": data_sin_detalle.get("data", []),
                },
                "is_detail_1": {
                    "success": data_con_detalle.get("success"),
                    "message": data_con_detalle.get("message"),
                    "data": data_con_detalle.get("data", []),
                },
            }

            # Guardar en caché
            _GUIA_COMPARATIVA_CACHE[cache_key] = (result, time.time())
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
        tp_client = get_transprensa_service()
        _internal_query_service_instance = InternalQueryService(
            db_name=database_name_wms, transprensa_client=tp_client
        )
    return _internal_query_service_instance
