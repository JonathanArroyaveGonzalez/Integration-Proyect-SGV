# -*- coding: utf-8 -*-
"""
Servicio para estructurar respuestas de manera consistente.
Convierte las respuestas directas de wmsAdapterV2 al formato esperado por las vistas.
"""

from typing import Dict, Any, List, Union
from datetime import datetime
import json


class ResponseService:
    """Servicio para formatear respuestas de manera consistente"""

    @staticmethod
    def format_wms_response(data: Any, message: str = "") -> Dict[str, Any]:
        """
        Convierte respuestas de wmsAdapterV2 al formato estándar.

        Args:
            data: Datos devueltos por funciones de wmsAdapterV2 (lista, tupla, etc.)
            message: Mensaje personalizado para la respuesta

        Returns:
            Dict con formato estándar: {"success": bool, "message": str, "data": list}
        """
        try:
            # Si data es una tupla (como read_sale_orders), tomar el primer elemento
            if isinstance(data, tuple):
                actual_data = data[0]  # Primer elemento contiene los datos
            else:
                actual_data = data

            # Si actual_data es una lista con elementos
            if isinstance(actual_data, list) and len(actual_data) > 0:
                # Serializar objetos datetime para JSON
                serialized_data = ResponseService._serialize_data(actual_data)

                return {
                    "success": True,
                    "message": message or "Datos encontrados exitosamente",
                    "data": serialized_data,
                }

            # Si actual_data es una lista vacía
            elif isinstance(actual_data, list) and len(actual_data) == 0:
                return {
                    "success": False,
                    "message": "No se encontraron registros",
                    "data": [],
                }

            # Si actual_data ya tiene formato de respuesta estructurada
            elif isinstance(actual_data, dict) and "success" in actual_data:
                return actual_data

            # Para otros casos
            else:
                return {
                    "success": True,
                    "message": message or "Operación completada",
                    "data": actual_data if actual_data is not None else [],
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error al procesar respuesta: {str(e)}",
                "data": [],
            }

    @staticmethod
    def format_error_response(error_message: str, data: Any = None) -> Dict[str, Any]:
        """
        Crea una respuesta de error estandarizada.

        Args:
            error_message: Mensaje de error
            data: Datos adicionales (opcional)

        Returns:
            Dict con formato de error estándar
        """
        return {
            "success": False,
            "message": error_message,
            "data": data if data is not None else [],
        }

    @staticmethod
    def format_success_response(
        data: Any, message: str = "Operación exitosa"
    ) -> Dict[str, Any]:
        """
        Crea una respuesta de éxito estandarizada.

        Args:
            data: Datos a incluir en la respuesta
            message: Mensaje de éxito

        Returns:
            Dict con formato de éxito estándar
        """
        return {
            "success": True,
            "message": message,
            "data": ResponseService._serialize_data(data) if data is not None else [],
        }

    @staticmethod
    def format_ciudad_response(ciudad_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Formatea la respuesta específica para consultas de ciudad.

        Args:
            ciudad_data: Datos completos de la ciudad

        Returns:
            Dict con formato específico para ciudad
        """
        if ciudad_data:
            return {
                "success": True,
                "message": "Ciudad encontrada exitosamente",
                "data": ciudad_data,
            }
        else:
            return {"success": False, "message": "Ciudad no encontrada", "data": None}

    @staticmethod
    def _serialize_data(data: Any) -> Any:
        """
        Serializa objetos datetime y otros tipos no serializables para JSON.

        Args:
            data: Datos a serializar

        Returns:
            Datos serializados
        """
        if isinstance(data, list):
            return [ResponseService._serialize_item(item) for item in data]
        else:
            return ResponseService._serialize_item(data)

    @staticmethod
    def _serialize_item(item: Any) -> Any:
        """
        Serializa un elemento individual.

        Args:
            item: Elemento a serializar

        Returns:
            Elemento serializado
        """
        if isinstance(item, dict):
            serialized = {}
            for key, value in item.items():
                if isinstance(value, datetime):
                    serialized[key] = value.isoformat()
                elif isinstance(value, str):
                    # Limpiar strings con muchos espacios
                    serialized[key] = value.strip()
                else:
                    serialized[key] = value
            return serialized
        elif isinstance(item, datetime):
            return item.isoformat()
        elif isinstance(item, str):
            return item.strip()
        else:
            return item


# Instancia singleton del servicio
response_service = ResponseService()
