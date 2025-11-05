# -*- coding: utf-8 -*-
"""
Lógica principal para construcción y gestión de remesas.
Consolidación de parsers, validadores, PDFs y construcción de payload.
"""

from __future__ import annotations
import json
import base64
import requests
from typing import Dict, Any, List, Tuple

from .remesaMapper import (
    RemesaMapper,
    DANE_MEDELLIN,
    PRODUCTO_CAJAS,
)

from transprensa.services.internalService import InternalQueryService


# =========================
#  Parsing
# =========================
def parseRequestPayload(request) -> Dict[str, Any]:
    """Parse del payload del request extrayendo components principales."""
    body = {}
    try:
        if request.body:
            decoded = request.body.decode("utf-8")
            body = json.loads(decoded) if decoded else {}
    except (json.JSONDecodeError, UnicodeDecodeError, AttributeError):
        body = {}

    orders_ids_raw = body.get("orders_ids") or []
    ids = (
        [str(x).strip() for x in orders_ids_raw if x]
        if isinstance(orders_ids_raw, list)
        else []
    )
    orders = body.get("orders") or []
    dry_run = bool(body.get("dry_run", False))

    return {
        "ids": ids,
        "orders": orders,
        "dry_run": dry_run,
        "body": body,
    }


# =========================
#  Enriquecimiento de órdenes
# =========================
def enrichOrderWithProductDetails(
    service: InternalQueryService, order: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Enriquece una orden consultando detalles de cada artículo por EAN.

    Para cada línea en order_detail:
    1. Extrae productoean
    2. Consulta service.get_articulo_por_referencia(ean)
    3. Agrega datos del artículo a la línea

    Args:
        service: InternalQueryService
        order: Orden con estructura {'order_detail': [...]}

    Returns:
        Orden enriquecida con datos de artículos
    """
    lines = order.get("order_detail", []) or []
    articleMap = {}

    for line in lines:
        ean = line.get("productoean", "").strip()
        if not ean:
            continue

        # Evitar consultas duplicadas del mismo EAN
        if ean in articleMap:
            line["articulo"] = articleMap[ean]
            continue

        try:
            result = service.get_articulo_por_referencia(ean)

            # result puede ser una lista directamente o un dict con {"success": ..., "data": [...]}
            articles = []
            if isinstance(result, list):
                articles = result
            elif isinstance(result, dict) and result.get("data"):
                articles = result.get("data", [])

            if articles:
                article = articles[0]
                articleMap[ean] = {
                    "id": article.get("id"),
                    "referencia": (article.get("referencia") or "").strip(),
                    "descripcion": (article.get("descripcion") or "").strip(),
                    "clasifart": article.get("clasifart", ""),
                    "preciounitario": article.get("preciounitario") or 0,
                    "peso": article.get("peso") or 1,
                    "volumen": article.get("volumen") or 0,
                }
                line["articulo"] = articleMap[ean]
            else:
                # Fallback a datos de línea si no se encuentra
                line["articulo"] = {
                    "id": None,
                    "referencia": (line.get("referencia") or "").strip(),
                    "descripcion": (line.get("descripcion") or "").strip(),
                    "preciounitario": line.get("preciounitario") or 0,
                    "peso": line.get("peso") or 1,
                    "volumen": line.get("volumen") or 0,
                }

        except Exception:
            # Fallback silencioso a datos de línea
            line["articulo"] = {
                "id": None,
                "referencia": (line.get("referencia") or "").strip(),
                "descripcion": (line.get("descripcion") or "").strip(),
                "preciounitario": line.get("preciounitario") or 0,
                "peso": line.get("peso") or 1,
                "volumen": line.get("volumen") or 0,
            }

    return order


# =========================
#  Construcción de índices
# =========================
def buildCityIndexFromOrders(
    service: InternalQueryService, orders: List[Dict[str, Any]]
) -> Dict[str, str]:
    """Construye índice {NOMBRE_CIUDAD -> COD_DANE} consultando Transprensa."""
    unique_names: set = set()
    for o in orders:
        nombre = (o.get("ciudad_despacho") or o.get("ciudad") or "").strip().upper()
        if nombre:
            unique_names.add(nombre)

    idx: Dict[str, str] = {}
    for nombre_norm in unique_names:
        ciudad_info = service.get_ciudad_codigo_by_nombre(nombre_norm)
        if ciudad_info and isinstance(ciudad_info, dict):
            dane = str(
                ciudad_info.get("ciudad_codigodane")
                or ciudad_info.get("ciudad_codigo")
                or ""
            ).strip()
            if dane:
                idx[nombre_norm] = dane

    return idx


# =========================
#  Resolvers
# =========================
def makeCiudadDaneResolver(ciudadesPorNombre: Dict[str, str]):
    """Crea resolver para DANE de ciudad."""

    def resolver(info: Dict[str, Any]) -> str:
        role = info.get("role")
        order = info.get("order", {})
        if role == "origen":
            return DANE_MEDELLIN
        nombre = (
            (order.get("ciudad_despacho") or order.get("ciudad") or "").strip().upper()
        )
        dane = ciudadesPorNombre.get(nombre)
        if not dane:
            raise ValueError(f"No se encontró DANE para ciudad '{nombre}'.")
        return dane

    return resolver


def makeProductoResolver():
    """Crea resolver para código de producto."""

    def resolver(_info: Dict[str, Any]) -> str:
        return PRODUCTO_CAJAS

    return resolver


# =========================
#  Construcción de payload
# =========================
def buildRemesasFromOrders(
    service: InternalQueryService,
    orders: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Construye payload de remesas desde órdenes.

    1. Enriquece órdenes con datos de artículos
    2. Construye índice de ciudades
    3. Mapea a estructura Transprensa
    4. Retorna payload y estadísticas
    """
    # Enriquecer órdenes con detalles de artículos
    for order in orders:
        enrichOrderWithProductDetails(service, order)

    # Construir índice de ciudades
    ciudades_idx = buildCityIndexFromOrders(service, orders)

    # Mapper con resolvers
    mapper = RemesaMapper(
        ciudadDaneResolver=makeCiudadDaneResolver(ciudades_idx),
        productCodigoResolver=makeProductoResolver(),
        detalleDefaults={
            "detalle_peso": "1",
            "detalle_cantidad": "1",
            "detalle_descripcion": "CAJA",
            "detalle_volumen": "1",
            "detalle_valordeclarado": "0",
            "detalle_producto_codigo": PRODUCTO_CAJAS,
        },
        defaults={"ciudades_por_nombre": ciudades_idx},
    )

    # Construir payload
    mapper.addSource({"orders": orders}, tag="ordenes-internas")
    payload = mapper.build()

    # Estadísticas
    remesas = payload.get("remesas", [])
    missing_cities = [
        (o.get("numpedido"), (o.get("ciudad_despacho") or o.get("ciudad")))
        for o in orders
        if (
            (o.get("ciudad_despacho") or o.get("ciudad") or "").strip().upper()
            not in ciudades_idx
        )
    ]

    stats = {
        "total_orders": len(orders),
        "remesas_built": len(remesas),
        "unique_cities": len(ciudades_idx),
        "missing_city_codes": len(missing_cities),
    }

    return {
        "success": True,
        "payload": payload,
        "stats": stats,
        "missing_city_codes_detail": missing_cities,
    }


# =========================
#  Manejo de PDFs
# =========================
def downloadPdfBase64(url: str, timeout: int = 20) -> str:
    """Descarga PDF y lo convierte a base64."""
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    return base64.b64encode(response.content).decode("utf-8")


def saveGuideToDatabase(
    service, remesa_num: str, picking: str, pdf_b64: str
) -> Dict[str, Any]:
    """Guarda guía (PDF en base64) en la base de datos."""
    return service.guardar_pdf_guia(
        delivery_number=remesa_num, picking=picking, pdf_base64=pdf_b64
    )


def processPdfDownloadsAndSaves(
    service,
    created_remesas: List[str],
    remesas_payload: List[Dict[str, Any]],
    pdf_urls_map: Dict[str, str],
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Procesa descarga y guardado de PDFs."""
    saved: List[Dict[str, Any]] = []
    errors: List[Dict[str, Any]] = []

    for i, remesa_num in enumerate(created_remesas):
        picking = ""

        if i < len(remesas_payload):
            remesa_item = remesas_payload[i]
            if isinstance(remesa_item, dict):
                picking = str(remesa_item.get("remesa_codigo", ""))

        pdf_url = pdf_urls_map.get(remesa_num)
        if not pdf_url:
            errors.append(
                {
                    "remesa": remesa_num,
                    "picking": picking,
                    "error": "No llegó URL de PDF desde Transprensa",
                }
            )
            continue

        try:
            pdf_b64 = downloadPdfBase64(pdf_url)
            save_result = saveGuideToDatabase(service, remesa_num, picking, pdf_b64)

            if isinstance(save_result, dict):
                if save_result.get("success"):
                    saved.append(
                        {
                            "remesa": remesa_num,
                            "picking": picking,
                            "status": "saved",
                        }
                    )
                else:
                    error_msg = save_result.get("message", "Error desconocido")
                    errors.append(
                        {
                            "remesa": remesa_num,
                            "picking": picking,
                            "error": error_msg,
                        }
                    )
            else:
                errors.append(
                    {
                        "remesa": remesa_num,
                        "picking": picking,
                        "error": f"Respuesta inesperada: {type(save_result).__name__}",
                    }
                )

        except requests.Timeout:
            errors.append(
                {
                    "remesa": remesa_num,
                    "picking": picking,
                    "error": "Timeout al descargar PDF (>20s)",
                }
            )

        except requests.RequestException as e:
            errors.append(
                {
                    "remesa": remesa_num,
                    "picking": picking,
                    "error": f"Error al descargar PDF: {str(e)}",
                }
            )

        except Exception as e:
            errors.append(
                {
                    "remesa": remesa_num,
                    "picking": picking,
                    "error": f"Excepción inesperada: {str(e)}",
                }
            )

    return saved, errors


def extractPdfUrlsFromResponse(tp_print_response: Dict[str, Any]) -> Dict[str, str]:
    """Extrae mapeo {remesa_num: pdf_url} de respuesta de impresión."""
    if not tp_print_response or not isinstance(tp_print_response, dict):
        return {}

    if not tp_print_response.get("success"):
        return {}

    data = tp_print_response.get("data")
    if isinstance(data, dict):
        return data

    return {}
