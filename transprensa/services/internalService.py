from typing import Dict, Any, Optional

from wmsAdapterV2.functions.SaleOrder.read import read_sale_orders
from wmsAdapterV2.functions.carrier.save_guide import save_guide
from wmsAdapterV2.functions.carrier.cancel_guide import cancel_guide
from wmsAdapterV2.functions.carrier.read_data_guide import read_data_guide
from transprensa.services.transprensaService import get_transprensa_service

# Singleton global para InternalQueryService
_internal_query_service_instance: Optional["InternalQueryService"] = None

# Cache persistente de ciudades para evitar consultas repetidas
_CIUDAD_CACHE: Dict[str, str] = {}


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
                    self.GET[key] = [str(value)]  

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

    def get_ciudad_codigo_by_nombre(self, nombre_ciudad: str) -> str:
        """
        Consulta el código DANE de ciudad por nombre usando el servicio de Transprensa.
        Utiliza cache para evitar consultas repetidas.

        Args:
            nombre_ciudad: Nombre de la ciudad a consultar

        Returns:
            str: Código DANE de la ciudad o cadena vacía si no se encuentra
        """
        if not nombre_ciudad:
            return ""

        # Normalizar nombre para búsqueda en cache
        nombre_normalizado = nombre_ciudad.upper().strip()

        # Verificar cache primero 
        if nombre_normalizado in _CIUDAD_CACHE:
            return _CIUDAD_CACHE[nombre_normalizado]

        payload = {
            "ciudad_codigo": "",
            "departamento_codigo": "",
            "departamento_codigodane": "",
            "nombre_ciudad": nombre_normalizado,
        }

        try:
            # Llamar a Transprensa con timeout de 5 segundos
            resp = self.tp.request(
                method="POST",
                endpoint="servicio.Consultas.ciudad",
                data=payload,
                timeout=5,  # Timeout para evitar bloqueos indefinidos
            )

            if not resp or not resp.get("success") or not resp.get("data"):
                _CIUDAD_CACHE[nombre_normalizado] = ""
                return ""

            ciudades = resp.get("data", [])
            if not ciudades or not isinstance(ciudades[0], dict):
                _CIUDAD_CACHE[nombre_normalizado] = ""
                return ""

            codigo_dane = ciudades[0].get("ciudad_codigodane", "")

            # Guardar en cache para futuras consultas
            _CIUDAD_CACHE[nombre_normalizado] = codigo_dane

            return codigo_dane

        except Exception:
            # Guardar error en cache para no reintentar inmediatamente
            _CIUDAD_CACHE[nombre_normalizado] = ""
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
            include_fields = "order_detail:qtypedido,preciounitario"

            # Crear MockRequest con parámetros de filtro e include
            params = {"numpedido": orden_id, "include": include_fields}
            mock_request = MockRequest(params)

            print(f"[DEBUG] Buscando orden con numpedido: {orden_id}")
            print(f"[DEBUG] Incluye campos de detalle: {include_fields}")

            # Llamar a la función de wmsAdapterV2 con el orden correcto de parámetros
            result, query, query_detail = read_sale_orders(mock_request, self.db_name)

            return result

        except Exception as e:
            return {
                "success": False,
                "message": f"Error al consultar orden: {str(e)}",
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
        tp_client = get_transprensa_service()
        _internal_query_service_instance = InternalQueryService(
            db_name="couca01_test", transprensa_client=tp_client
        )
    return _internal_query_service_instance
