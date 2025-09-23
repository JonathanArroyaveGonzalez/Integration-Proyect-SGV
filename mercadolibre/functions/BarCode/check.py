"""
Funciones para verificar existencia de códigos de barras en el WMS
Optimizado para reducir latencia mediante verificación previa con validación inteligente
"""

import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def get_wms_base_url():
    """
    Obtiene la URL base del WMS desde configuración de Django o usa una por defecto
    """
    return getattr(settings, "WMS_BASE_URL", "http://localhost:8000").rstrip("/")


def check_barcode_exists(ean, auth_headers=None):
    """
    Verifica si un código de barras ya existe en el WMS usando el endpoint GET
    Incluye validación inteligente para detectar inconsistencias del WMS
    
    Args:
        ean (str): EAN/ID interno del código de barras
        auth_headers (dict): Headers de autenticación
        
    Returns:
        dict: {
            "exists": bool,
            "success": bool, 
            "message": str,
            "data": dict (si existe),
            "validation_status": str  # 'valid', 'empty_data', 'invalid_structure', 'network_error'
        }
    """
    if not ean:
        return {
            "exists": False,
            "success": False,
            "message": "EAN no proporcionado",
            "data": None,
            "validation_status": "invalid_input"
        }
    
    try:
        wms_url = f"{get_wms_base_url()}/wms/base/v2/tRelacionCodbarras"
        headers = {
            "Accept": "application/json",
            **(
                {"Authorization": auth_headers["Authorization"]}
                if auth_headers and "Authorization" in auth_headers
                else {}
            ),
        }
        
        params = {"idinternoean": str(ean)}
        
        logger.info(f"Verificando existencia de código de barras para EAN: {ean}")
        response = requests.get(wms_url, headers=headers, params=params)
        
        if response.status_code == 200:
            try:
                data = response.json()
                
                # Validación inteligente de datos
                if not data or (isinstance(data, dict) and not data) or (isinstance(data, list) and len(data) == 0):
                    logger.warning(f"WMS retornó 200 pero datos vacíos para EAN {ean}")
                    return {
                        "exists": False,
                        "success": True,
                        "message": f"WMS retornó datos vacíos para EAN {ean} (inconsistencia detectada)",
                        "data": None,
                        "validation_status": "empty_data"
                    }
                
                # Verificar estructura de datos esperada
                if isinstance(data, list) and len(data) > 0:
                    item = data[0]
                    if not isinstance(item, dict) or ('idinternoean' not in item and 'ean' not in item):
                        logger.warning(f"WMS retornó datos con estructura inválida para EAN {ean}")
                        return {
                            "exists": False,
                            "success": True,
                            "message": f"WMS retornó estructura de datos inválida para EAN {ean}",
                            "data": None,
                            "validation_status": "invalid_structure"
                        }
                elif isinstance(data, dict):
                    if ('idinternoean' not in data and 'ean' not in data) and 'error' in data:
                        logger.warning(f"WMS retornó error en datos para EAN {ean}: {data.get('error')}")
                        return {
                            "exists": False,
                            "success": True,
                            "message": f"WMS retornó error: {data.get('error')}",
                            "data": None,
                            "validation_status": "empty_data"
                        }
                
                logger.info(f"Código de barras encontrado y validado para EAN {ean}")
                return {
                    "exists": True,
                    "success": True,
                    "message": f"Código de barras existe y está validado para EAN {ean}",
                    "data": data,
                    "validation_status": "valid"
                }
                
            except Exception as json_error:
                logger.error(f"Error parseando respuesta JSON para EAN {ean}: {str(json_error)}")
                return {
                    "exists": False,
                    "success": False,
                    "message": f"Error parseando respuesta del WMS: {str(json_error)}",
                    "data": None,
                    "validation_status": "invalid_structure"
                }
                
        elif response.status_code == 404:
            # Código de barras no existe (comportamiento normal)
            logger.info(f"Código de barras no encontrado para EAN {ean}")
            return {
                "exists": False,
                "success": True,
                "message": f"Código de barras no existe para EAN {ean}",
                "data": None,
                "validation_status": "valid"
            }
        else:
            # Error en la consulta
            logger.warning(f"Error consultando código de barras para EAN {ean}: {response.status_code}")
            return {
                "exists": False,
                "success": False,
                "message": f"Error consultando código de barras: {response.status_code} - {response.text}",
                "data": None,
                "validation_status": "network_error"
            }
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error de conexión verificando código de barras para EAN {ean}: {e}")
        return {
            "exists": False,
            "success": False,
            "message": f"Error de conexión: {e}",
            "data": None,
            "validation_status": "network_error"
        }
    except Exception as e:
        logger.error(f"Error inesperado verificando código de barras para EAN {ean}: {e}")
        return {
            "exists": False,
            "success": False,
            "message": f"Error inesperado: {e}",
            "data": None,
            "validation_status": "network_error"
        }


def check_multiple_barcodes_exist(eans, auth_headers=None):
    """
    Verifica existencia de múltiples códigos de barras de manera eficiente
    Incluye análisis de patrones de inconsistencias del WMS
    
    Args:
        eans (list): Lista de EANs a verificar
        auth_headers (dict): Headers de autenticación
        
    Returns:
        dict: {
            "existing": list,           # EANs que existen y están validados
            "non_existing": list,       # EANs que no existen  
            "errors": list,             # EANs con errores
            "inconsistent": list,       # EANs con datos inconsistentes
            "success": bool,
            "message": str,
            "validation_summary": dict  # Resumen de tipos de validación
        }
    """
    if not eans:
        return {
            "existing": [],
            "non_existing": [],
            "errors": [],
            "inconsistent": [],
            "success": True,
            "message": "No se proporcionaron EANs para verificar",
            "validation_summary": {}
        }
    
    existing = []
    non_existing = []
    errors = []
    inconsistent = []
    validation_counts = {
        "valid": 0,
        "empty_data": 0,
        "invalid_structure": 0,
        "network_error": 0,
        "invalid_input": 0
    }
    
    logger.info(f"Verificando existencia de {len(eans)} códigos de barras con validación inteligente")
    
    for ean in eans:
        try:
            result = check_barcode_exists(ean, auth_headers)
            
            # Contar tipos de validación
            validation_status = result.get("validation_status", "unknown")
            if validation_status in validation_counts:
                validation_counts[validation_status] += 1
            
            if result["success"]:
                if result["exists"] and result["validation_status"] == "valid":
                    existing.append(ean)
                elif not result["exists"] and result["validation_status"] == "valid":
                    non_existing.append(ean)
                else:
                    # Datos inconsistentes (200 con datos vacíos/inválidos)
                    inconsistent.append({
                        "ean": ean, 
                        "reason": result["message"],
                        "validation_status": result["validation_status"]
                    })
            else:
                errors.append({
                    "ean": ean, 
                    "error": result["message"],
                    "validation_status": result["validation_status"]
                })
                
        except Exception as e:
            logger.error(f"Error verificando EAN {ean}: {e}")
            errors.append({
                "ean": ean, 
                "error": str(e),
                "validation_status": "exception"
            })
    
    # Análisis de patrones de inconsistencia
    inconsistency_rate = len(inconsistent) / len(eans) if eans else 0
    if inconsistency_rate > 0.1:  # Más del 10% inconsistente
        logger.warning(f"Alto índice de inconsistencias WMS detectado: {inconsistency_rate:.2%}")
    
    return {
        "existing": existing,
        "non_existing": non_existing,
        "errors": errors,
        "inconsistent": inconsistent,
        "success": True,
        "message": f"Verificación completada: {len(existing)} válidos, {len(non_existing)} nuevos, {len(errors)} errores, {len(inconsistent)} inconsistentes",
        "validation_summary": {
            **validation_counts,
            "inconsistency_rate": inconsistency_rate,
            "total_processed": len(eans)
        }
    }