"""
Utilidades para estandarizar respuestas HTTP en la aplicación MercadoLibre
"""

from django.http import JsonResponse
from typing import Optional, Dict, Any, Union, List
import logging

logger = logging.getLogger(__name__)


def create_success_response(
    data: Optional[Union[Dict, List]] = None,
    message: str = "Operación exitosa",
    status: int = 200,
    extra_fields: Optional[Dict[str, Any]] = None
) -> JsonResponse:
    """
    Crea una respuesta HTTP exitosa estandarizada
    
    Args:
        data: Datos a incluir en la respuesta
        message: Mensaje de éxito
        status: Código de estado HTTP (200, 201, etc.)
        extra_fields: Campos adicionales para incluir en la respuesta
        
    Returns:
        JsonResponse: Respuesta HTTP estandarizada
    """
    response_data = {
        "status": "success",
        "message": message
    }
    
    if data is not None:
        response_data["data"] = data
    
    # Agregar campos adicionales si se proporcionan
    if extra_fields:
        response_data.update(extra_fields)
    
    return JsonResponse(response_data, status=status, safe=False)


def create_error_response(
    message: str,
    errors: Optional[Union[str, List, Dict]] = None,
    status: int = 400,
    error_code: Optional[str] = None
) -> JsonResponse:
    """
    Crea una respuesta HTTP de error estandarizada
    
    Args:
        message: Mensaje principal del error
        errors: Detalles específicos del error
        status: Código de estado HTTP (400, 500, etc.)
        error_code: Código específico del error para debugging
        
    Returns:
        JsonResponse: Respuesta HTTP de error estandarizada
    """
    response_data = {
        "status": "error",
        "message": message
    }
    
    if errors is not None:
        response_data["errors"] = errors
    
    if error_code:
        response_data["error_code"] = error_code
    
    # Log del error para debugging
    logger.error(f"Error response: {message} | Status: {status} | Details: {errors}")
    
    return JsonResponse(response_data, status=status, safe=False)


def create_partial_success_response(
    created: List,
    errors: List,
    operation: str = "operación"
) -> JsonResponse:
    """
    Crea una respuesta para operaciones con éxitos parciales
    
    Args:
        created: Lista de elementos creados/actualizados exitosamente
        errors: Lista de errores ocurridos
        operation: Tipo de operación realizada
        
    Returns:
        JsonResponse: Respuesta HTTP con código apropiado
    """
    # Determinar código de estado
    if created and not errors:
        status = 200  # Solo éxitos
        message = f"{operation.capitalize()} completada exitosamente"
    elif created and errors:
        status = 207  # Éxitos parciales (Multi-Status)
        message = f"{operation.capitalize()} completada parcialmente"
    else:
        status = 400  # Solo errores
        message = f"Error en {operation}"
    
    response_data = {
        "status": "partial_success" if status == 207 else ("success" if status == 200 else "error"),
        "message": message,
        "summary": {
            "total_processed": len(created) + len(errors),
            "successful": len(created),
            "failed": len(errors)
        }
    }
    
    if created:
        response_data["created"] = created
    
    if errors:
        response_data["errors"] = errors
    
    return JsonResponse(response_data, status=status, safe=False)


def handle_request_validation(request, allowed_methods: List[str]) -> Optional[JsonResponse]:
    """
    Valida que el método HTTP sea permitido
    
    Args:
        request: Objeto request de Django
        allowed_methods: Lista de métodos HTTP permitidos
        
    Returns:
        JsonResponse con error si el método no es válido, None si es válido
    """
    if request.method not in allowed_methods:
        return create_error_response(
            message=f"Método {request.method} no permitido",
            errors=f"Métodos permitidos: {', '.join(allowed_methods)}",
            status=405
        )
    return None


def handle_json_decode_error() -> JsonResponse:
    """
    Maneja errores de decodificación JSON de manera estandarizada
    
    Returns:
        JsonResponse: Respuesta de error estandarizada para JSON inválido
    """
    return create_error_response(
        message="JSON inválido en el cuerpo de la solicitud",
        errors="Por favor, proporcione datos JSON válidos",
        status=400,
        error_code="INVALID_JSON"
    )


def handle_internal_server_error(error: Exception, context: str = "") -> JsonResponse:
    """
    Maneja errores internos del servidor de manera estandarizada
    
    Args:
        error: Excepción capturada
        context: Contexto adicional del error
        
    Returns:
        JsonResponse: Respuesta de error interno estandarizada
    """
    error_message = "Error interno del servidor"
    if context:
        error_message += f" en {context}"
    
    return create_error_response(
        message=error_message,
        errors=str(error),
        status=500,
        error_code="INTERNAL_SERVER_ERROR"
    )