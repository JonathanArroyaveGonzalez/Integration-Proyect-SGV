"""
Utilidades para manejo de autenticación en requests HTTP
"""

from typing import Dict, Optional
from django.http import HttpRequest
import logging

logger = logging.getLogger(__name__)


def extract_auth_headers(request: HttpRequest) -> Dict[str, str]:
    """
    Extrae los headers de autorización del request de Django de manera estandarizada
    
    Args:
        request: Objeto HttpRequest de Django
        
    Returns:
        Dict con headers de autorización si están presentes
    """
    auth_headers = {}
    
    # Buscar en META (estándar Django)
    if "HTTP_AUTHORIZATION" in request.META:
        auth_headers["Authorization"] = request.META["HTTP_AUTHORIZATION"]
    # Buscar en headers directamente (algunas configuraciones)
    elif hasattr(request, 'headers') and "Authorization" in request.headers:
        auth_headers["Authorization"] = request.headers["Authorization"]
    
    return auth_headers


def validate_auth_headers(auth_headers: Dict[str, str]) -> bool:
    """
    Valida que los headers de autorización estén presentes y tengan formato correcto
    
    Args:
        auth_headers: Diccionario con headers de autorización
        
    Returns:
        bool: True si los headers son válidos
    """
    if not auth_headers or "Authorization" not in auth_headers:
        logger.warning("Headers de autorización faltantes")
        return False
    
    auth_value = auth_headers["Authorization"]
    if not auth_value or not auth_value.strip():
        logger.warning("Header de autorización vacío")
        return False
    
    # Validar formato básico Bearer token
    if not auth_value.startswith(("Bearer ", "Token ")):
        logger.warning(f"Formato de autorización no reconocido: {auth_value[:20]}...")
        return False
    
    return True


def get_validated_auth_headers(request: HttpRequest) -> Optional[Dict[str, str]]:
    """
    Obtiene y valida headers de autorización en una sola operación
    
    Args:
        request: Objeto HttpRequest de Django
        
    Returns:
        Dict con headers válidos o None si no son válidos
    """
    auth_headers = extract_auth_headers(request)
    
    if validate_auth_headers(auth_headers):
        return auth_headers
    
    return None