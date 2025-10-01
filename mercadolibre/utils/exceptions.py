"""Excepciones personalizadas para el servicio de MercadoLibre."""

from typing import Optional, Dict, Any


class MeliError(Exception):
    """Excepción base para errores de la API de MercadoLibre."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
    ):
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(message)


class MeliAuthError(MeliError):
    """Errores de autenticación (401) o autorización (403)."""

    pass


class MeliNotFoundError(MeliError):
    """Errores de recurso no encontrado (404)."""

    pass


class MeliBadRequestError(MeliError):
    """Errores de solicitud inválida (400)."""

    pass


class MeliRateLimitError(MeliError):
    """Errores de límite de tasa excedido (429)."""

    pass


# ------------------------------
# Excepciones personalizadas
# ------------------------------


class MeliServerError(MeliError):
    """Errores del servidor de MercadoLibre (500, 502, 503, 504)."""

    pass


class UserMappingError(Exception):
    """Error al mapear un cliente desde MercadoLibre a WMS."""

    def __init__(self, user_id: str, message: str, type_user: str):
        self.user_id = user_id
        self.message = message
        super().__init__(f"[{type_user} {user_id}] {message}")


class WMSRequestError(Exception):
    """Error en la comunicación o lógica con el WMS."""

    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"[WMS {status_code}] {message}")
