# -*- coding: utf-8 -*-
"""
Servicio interno que integra las funcionalidades de wmsAdapterV2 con el servicio de Transprensa.
Este servicio actúa como intermediario, utilizando las funciones ya implementadas en wmsAdapterV2
y añadiendo la funcionalidad específica de consulta de ciudades de Transprensa.
"""

from typing import Dict, Any, Optional
from functools import lru_cache

# Importaciones de wmsAdapterV2
from wmsAdapterV2.functions.SaleOrder.read import read_sale_orders
from wmsAdapterV2.functions.Customer.read import read_clt
from wmsAdapterV2.functions.Product.read import read_articles
from wmsAdapterV2.functions.carrier.save_guide import save_guide
from wmsAdapterV2.functions.carrier.cancel_guide import cancel_guide
from wmsAdapterV2.functions.carrier.read_data_guide import read_data_guide


# Singleton global para InternalQueryService
_internal_query_service_instance: Optional["InternalQueryService"] = None


class MockRequest:
    """
    Simula un objeto request de Django para usar con las funciones de wmsAdapterV2.
    Django request.GET devuelve un QueryDict donde los valores son listas.
    """

    def __init__(self, get_params=None, body_params=None):
        # Convertir strings a listas para simular request.GET correctamente
        self.GET = {}
        if get_params:
            for key, value in get_params.items():
                if isinstance(value, list):
                    self.GET[key] = value
                else:
                    self.GET[key] = [str(value)]  # Django siempre devuelve listas

        self.body = body_params or b""
        self.method = "GET"


class InternalQueryService:
    def __init__(self, *, db_name: str, transprensa_client):
        """
        Inicializa el servicio de consultas interno.

        Args:
            db_name: Nombre de la base de datos para wmsAdapterV2
            transprensa_client: Cliente para consumir WS de Transprensa.
                Debe exponer:
                - consultas_ciudad(filtros: dict) -> dict
        """
        self.db_name = db_name
        self.tp = transprensa_client

    @lru_cache(maxsize=512)
    def get_ciudad_codigo_by_nombre(self, nombre_ciudad: str) -> str:
        """
        Consulta el código de ciudad por nombre usando el servicio de Transprensa.
        Esta es la única función que interactúa con el servicio externo.

        Args:
            nombre_ciudad: Nombre de la ciudad a consultar

        Returns:
            str: Código de la ciudad o cadena vacía si no se encuentra
        """
        if not nombre_ciudad:
            return ""

        # Preparar el cuerpo de la petición igual que el curl que funciona
        payload = {
            "ciudad_codigo": "",
            "departamento_codigo": "",
            "departamento_codigodane": "",
            "nombre_ciudad": nombre_ciudad.upper().strip(),
        }

        try:
            # Usar el método request de TransprensaService
            resp = self.tp.request(
                method="POST", endpoint="servicio.Consultas.ciudad", data=payload
            )

            if not resp or not resp.get("success") or not resp.get("data"):
                return None

            # Obtener el primer resultado si existe
            ciudades = resp.get("data", [])
            if not ciudades:
                return None

            # Devolver toda la información de la ciudad
            return ciudades[0]

        except Exception as e:
            print(f"Error al consultar ciudad: {str(e)}")
            return ""

    def get_orden_por_id(self, orden_id: str) -> Dict[str, Any]:
        """
        Obtiene una orden usando wmsAdapterV2 con detalles de línea incluidos.

        Args:
            orden_id: ID de la orden a consultar (se busca por numpedido)

        Returns:
            Dict con la respuesta estructurada que incluye:
                - data: Lista con la orden y sus detalles (productoean, referencia, item, qtyreservado)
                - success: Booleano indicando éxito de la consulta
                - message: Mensaje descriptivo del resultado
        """
        try:
            # Campos de detalle predefinidos a incluir en la consulta
            include_fields = "order_detail:productoean,referencia,item,qtyreservado"

            # Crear MockRequest con parámetros de filtro e include
            params = {"numpedido": orden_id, "include": include_fields}
            mock_request = MockRequest(params)

            print(f"[DEBUG] Buscando orden con numpedido: {orden_id}")
            print(f"[DEBUG] Incluye campos de detalle: {include_fields}")
            print(f"[DEBUG] MockRequest.GET: {mock_request.GET}")

            # Llamar a la función de wmsAdapterV2 con el orden correcto de parámetros
            result, query, query_detail = read_sale_orders(mock_request, self.db_name)

            print(f"[DEBUG] Resultado de read_sale_orders: {result}")

            return result

        except Exception as e:
            print(f"[ERROR] Error en get_orden_por_id: {str(e)}")
            return {
                "success": False,
                "message": f"Error al consultar orden: {str(e)}",
                "data": [],
            }

    def get_cliente_por_nit_o_sucursal(
        self, nit: str, idsucursal: Optional[str]
    ) -> Dict[str, Any]:
        """
        Obtiene un cliente usando wmsAdapterV2.

        Args:
            nit: NIT del cliente (campo principal de búsqueda)
            idsucursal: ID de sucursal (opcional)

        Returns:
            Dict con la respuesta estructurada
        """
        try:
            # Preparar filtros
            filters = {}
            if nit:
                filters["nit"] = nit
            if idsucursal:
                filters["idsucursal"] = idsucursal

            print(f"[DEBUG] Buscando cliente - Filtros: {filters}")

            # Crear MockRequest con los parámetros de filtro
            mock_request = MockRequest(filters)

            print(f"[DEBUG] MockRequest.GET: {mock_request.GET}")

            # Llamar a la función de wmsAdapterV2 con el orden correcto de parámetros
            result, query = read_clt(mock_request, self.db_name)

            print(f"[DEBUG] Resultado de read_clt: {result}")

            return result

        except Exception as e:
            print(f"[ERROR] Error en get_cliente_por_nit_o_sucursal: {str(e)}")
            return {
                "success": False,
                "message": f"Error al consultar cliente: {str(e)}",
                "data": [],
            }

    def get_articulo_por_referencia(self, referencia: str) -> Dict[str, Any]:
        """
        Obtiene información de un artículo usando wmsAdapterV2.

        Args:
            referencia: Código EAN del artículo (se busca por productoean)

        Returns:
            Dict con la respuesta estructurada
        """
        try:
            # Crear MockRequest con los parámetros de filtro
            # Usar productoean según especificación
            mock_request = MockRequest({"productoean": referencia})

            print(f"[DEBUG] Buscando artículo con productoean: {referencia}")
            print(f"[DEBUG] MockRequest.GET: {mock_request.GET}")

            # Llamar a la función de wmsAdapterV2 con el orden correcto de parámetros
            result, query = read_articles(mock_request, self.db_name)

            print(f"[DEBUG] Resultado de read_articles: {result}")

            return result

        except Exception as e:
            print(f"[ERROR] Error en get_articulo_por_referencia: {str(e)}")
            return {
                "success": False,
                "message": f"Error al consultar artículo: {str(e)}",
                "data": [],
            }

    def guardar_pdf_guia(
        self, delivery_number: str, picking: str, pdf_base64: str
    ) -> Dict[str, Any]:
        """
        Guarda el PDF de una guía usando wmsAdapterV2.
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
        """
        try:
            return cancel_guide(self.db_name, delivery_number, picking)
        except Exception as e:
            return {
                "success": False,
                "message": f"Error al anular guía: {str(e)}",
                "data": None,
            }

    def leer_datos_guia(
        self, picking: str, bigpedido: str, is_detail: bool
    ) -> Dict[str, Any]:
        """
        Lee datos de una guía usando wmsAdapterV2.
        """
        try:
            return read_data_guide(
                self.db_name, picking, bigpedido, 1 if is_detail else 0
            )
        except Exception as e:
            return {
                "success": False,
                "message": f"Error al leer datos de guía: {str(e)}",
                "data": [],
            }


def get_internal_query_service() -> InternalQueryService:
    """
    Obtiene la instancia singleton del servicio de consultas internas.

    La instancia se crea una única vez en la primera llamada y se reutiliza
    en todas las peticiones posteriores, evitando overhead de inicialización.

    Returns:
        InternalQueryService: Instancia singleton del servicio
    """
    global _internal_query_service_instance
    if _internal_query_service_instance is None:
        from transprensa.services.transprensaService import get_transprensa_service

        tp_client = get_transprensa_service()
        _internal_query_service_instance = InternalQueryService(
            db_name="couca01_test", transprensa_client=tp_client
        )
    return _internal_query_service_instance
