from __future__ import annotations
import os
import django
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional

# Configurar Django antes de importar modelos
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
django.setup()

from transprensa.services.internalService import get_internal_query_service


#  Constantes OSAKA
OSAKA_CLIENTE_CODIGO = "3245"
OSAKA_REMITENTE_CODIGO = "2597359"
FORMA_PAGO_CREDITO = "5"
PRODUCTO_CAJAS = "3559"
TIPO_SERVICIO_PAQUETEO = "2"
CENTRO_COSTO_MEDELLIN = "10"
DANE_MEDELLIN = "05001000"
TIPODOC_CEDULA = "1"
TIPODOC_NIT = "2"

# Instancia servicio consulta interno
internal_service = get_internal_query_service()


def limpiar_espacios(valor: Any) -> Any:
    """
    Elimina espacios en blanco al inicio y final de cadenas de texto.
    Si el valor es None o no es string, lo retorna sin cambios.
    """
    if isinstance(valor, str):
        return valor.strip()
    return valor


@dataclass
class Cliente:
    cliente_codigo: Optional[str] = OSAKA_CLIENTE_CODIGO
    tipo_documentocliente_codigo: Optional[str] = ""
    cliente_documento: Optional[str] = ""
    cliente_nombre1: Optional[str] = ""
    cliente_nombre2: Optional[str] = ""
    cliente_apellido1: Optional[str] = ""
    cliente_apellido2: Optional[str] = ""
    cliente_direccion: Optional[str] = ""
    cliente_telefono: Optional[str] = ""
    cliente_ciudad_codigo: Optional[str] = ""
    cliente_email: Optional[str] = ""
    cliente_tipopersona: Optional[bool] = False
    cliente_digitoverificacion: Optional[str] = ""


@dataclass
class Remitente:
    remitente_codigo: Optional[str] = OSAKA_REMITENTE_CODIGO
    tipo_documentoremitente_codigo: Optional[str] = ""
    remitente_documento: Optional[str] = ""
    remitente_nombre: Optional[str] = ""
    remitente_direccion: Optional[str] = ""
    remitente_telefono: Optional[str] = ""
    remitente_ciudad_codigo: Optional[str] = ""


@dataclass
class Destinatario:
    destinatario_codigo: Optional[str] = ""
    tipo_documentodestinatario_codigo: Optional[str] = TIPODOC_NIT
    destinatario_documento: Optional[str] = None
    destinatario_nombre: Optional[str] = None
    destinatario_direccion: Optional[str] = None
    destinatario_telefono: Optional[str] = None
    destinatario_ciudad_codigo: Optional[str] = None


@dataclass
class Detalle:
    detalle_peso: Optional[str] = None
    detalle_volumen: Optional[str] = None
    detalle_valordeclarado: Optional[str] = None
    detalle_producto_codigo: Optional[str] = PRODUCTO_CAJAS
    detalle_cantidad: Optional[str] = None
    detalle_descripcion: Optional[str] = "Mercancia Delicada"


@dataclass
class Remesa:
    ciudad_codigo_origen: Optional[str] = DANE_MEDELLIN
    ciudad_codigo_destino: Optional[str] = None
    tipo_servicio: Optional[str] = TIPO_SERVICIO_PAQUETEO
    cliente: Cliente = None
    remitente: Remitente = None
    destinatario: Destinatario = None
    detalle: List[Detalle] = None
    remesa_total: Optional[str] = ""
    remesa_manejo: Optional[str] = ""
    remesa_tarifa: Optional[str] = ""
    centro_costo: Optional[str] = CENTRO_COSTO_MEDELLIN
    orden_carga: Optional[str] = ""
    forma_pago: Optional[str] = FORMA_PAGO_CREDITO
    documento_cliente: Optional[str] = None
    orden_compra: Optional[str] = None
    remesa_observacion: Optional[str] = "SIN VERIFICAR PESO NI CONTENIDO"
    remesa_codigo: Optional[str] = None


def obtener_codigo_dane(ciudad: str, default: str = DANE_MEDELLIN) -> str:
    """
    Obtiene el código DANE de una ciudad.
    Si no existe en el mapa, retorna el valor por defecto.
    """
    if not ciudad:
        return default
    else:
        consultaCiudad = internal_service.get_ciudad_codigo_by_nombre(ciudad.upper().strip())
    return consultaCiudad


def mapperOrderToRemesa(orden_api: Dict[str, Any]) -> Optional[Remesa]:
    """
    Mapea un objeto de la API externa a una estructura Remesa.

    Args:
        orden_api: Diccionario con los datos de la orden desde la API externa

    Returns:
        Objeto Remesa poblado con los datos mapeados o None si faltan datos críticos
    """
    try:
        # Extraer datos del destinatario
        destinatario = Destinatario(
            destinatario_codigo="",
            tipo_documentodestinatario_codigo=TIPODOC_NIT,
            destinatario_documento=limpiar_espacios(orden_api.get("nit"))
            .replace("-", "")
            .strip(),
            destinatario_nombre=limpiar_espacios(orden_api.get("nombrecliente")),
            destinatario_direccion=limpiar_espacios(
                orden_api.get("direccion_despacho")
            ),
            destinatario_telefono=limpiar_espacios(orden_api.get("contacto", ""))
            or "0000000000",
            destinatario_ciudad_codigo=obtener_codigo_dane(
                limpiar_espacios(orden_api.get("ciudad_despacho"))
            ),
        )

        # Crear detalles a partir de order_detail
        detalles = []
        order_details = orden_api.get("order_detail", [])

        for item in order_details:
            detalle = Detalle(
                detalle_peso="0",
                detalle_volumen="0",
                # detalle_valordeclarado = str((float(item.get("preciounitario") or 0)) * int(float(item.get("qtypedido") or 0))),
                detalle_valordeclarado="0",
                detalle_producto_codigo=PRODUCTO_CAJAS,
                detalle_cantidad=str(int(float(item.get("qtypedido", 0)))),
                detalle_descripcion="Mercancia Delicada",
            )
            detalles.append(detalle)

        # Si no hay detalles, crear uno por defecto
        if not detalles:
            detalles.append(
                Detalle(
                    detalle_peso="1",
                    detalle_volumen="1",
                    detalle_valordeclarado="0",
                    detalle_producto_codigo=PRODUCTO_CAJAS,
                    detalle_cantidad="1",
                    detalle_descripcion="Mercancia Delicada",
                )
            )

        # Crear remesa completa
        remesa = Remesa(
            ciudad_codigo_origen=DANE_MEDELLIN,
            ciudad_codigo_destino=obtener_codigo_dane(
                limpiar_espacios(orden_api.get("ciudad_despacho"))
            ),
            tipo_servicio=TIPO_SERVICIO_PAQUETEO,
            cliente=Cliente(),  # Usar valores por defecto
            remitente=Remitente(),  # Usar valores por defecto
            destinatario=destinatario,
            detalle=detalles,
            remesa_total="",
            remesa_manejo="",
            remesa_tarifa="",
            centro_costo=CENTRO_COSTO_MEDELLIN,
            orden_carga="",
            forma_pago=FORMA_PAGO_CREDITO,
            documento_cliente=limpiar_espacios(orden_api.get("pedidorelacionado")),
            orden_compra=limpiar_espacios(orden_api.get("numpedido")),
            remesa_observacion=limpiar_espacios(orden_api.get("notas"))
            or "SIN VERIFICAR PESO NI CONTENIDO",
            remesa_codigo=limpiar_espacios(orden_api.get("numpedido")),
        )

        return remesa

    except Exception as e:
        print(f"Error mapeando orden: {e}")
        return None


def mapear_lista_ordenes(ordenes_api: List[Dict[str, Any]]) -> List[Remesa]:
    """
    Mapea una lista completa de órdenes de la API a objetos Remesa.

    Args:
        ordenes_api: Lista de diccionarios con datos de órdenes

    Returns:
        Lista de objetos Remesa
    """
    remesas = []
    for orden in ordenes_api:
        remesa = mapperOrderToRemesa(orden)
        if remesa:
            remesas.append(remesa)
    return remesas


def remesa_a_dict(remesa: Remesa) -> Dict[str, Any]:
    """
    Convierte un objeto Remesa a un diccionario listo para enviar al API.

    Args:
        remesa: Objeto Remesa a convertir

    Returns:
        Diccionario con la estructura esperada por el API
    """
    return {
        "ciudad_codigo_origen": remesa.ciudad_codigo_origen,
        "ciudad_codigo_destino": remesa.ciudad_codigo_destino,
        "tipo_servicio": remesa.tipo_servicio,
        "cliente": asdict(remesa.cliente),
        "remitente": asdict(remesa.remitente),
        "destinatario": asdict(remesa.destinatario),
        "detalle": [asdict(d) for d in remesa.detalle],
        "remesa_total": remesa.remesa_total,
        "remesa_manejo": remesa.remesa_manejo,
        "remesa_tarifa": remesa.remesa_tarifa,
        "centro_costo": remesa.centro_costo,
        "orden_carga": remesa.orden_carga,
        "forma_pago": remesa.forma_pago,
        "documento_cliente": remesa.documento_cliente,
        "orden_compra": remesa.orden_compra,
        "remesa_observacion": remesa.remesa_observacion,
        "remesa_codigo": remesa.remesa_codigo,
    }


def crear_payload_api(remesas: List[Remesa]) -> Dict[str, Any]:
    """
    Crea el payload completo para enviar al API de SILOGTRAN.

    Args:
        remesas: Lista de objetos Remesa

    Returns:
        Diccionario con el formato esperado por el API
    """
    return {"remesas": [remesa_a_dict(r) for r in remesas]}


# =========================
#  Ejemplo de Uso
# =========================
if __name__ == "__main__":
    # Datos de ejemplo de la API externa WMS
    respuesta_api = [
        {
            "tipodocto": "PD",
            "doctoerp": "103888",
            "picking": "7746",
            "numpedido": "103888",
            "fechaplaneacion": "2025-10-30T16:59:58.153",
            "f_pedido": "2025-10-30T16:59:58.153",
            "item": "1045047287-4   ",
            "nombrecliente": "ORTIZ BERRIO DANIEL",
            "contacto": "                                   ",
            "email": "",
            "notas": "",
            "ciudad_despacho": "itagui                                                    ",
            "pais_despacho": "",
            "departamento_despacho": "",
            "sucursal_despacho": "",
            "direccion_despacho": "CALLE 57 B #51 D 19 MEDELLIN                                                                                                                                                                                                                              ",
            "idsucursal": "0",
            "ciudad": "MEDELLIN                                                    ",
            "pedidorelacionado": "PD-103888    ",
            "cargue": "20230523",
            "nit": "1045047287-4   ",
            "estadopicking": 9,
            "fecharegistro": "2025-10-30T16:59:58.153",
            "fpedido": "2025-10-30T16:59:58.153",
            "fechtrans": None,
            "transportadora": "",
            "centrooperacion": "01",
            "estadoerp": "1",
            "picking_batch": None,
            "field_condicionpago": None,
            "field_documentoreferencia": None,
            "bodega": "01",
            "vendedor2": "18             ",
            "numguia": None,
            "id": 1,
            "f_ultima_actualizacion": "2025-10-31T17:32:32.380",
            "bodegaerp": "01",
            "tipoaduana": "AUTOADUANA",
            "order_detail": [
                {"qtypedido": "50.0000", "preciounitario": "1000.000"},
                {"qtypedido": "10.0000", "preciounitario": "1000.000"},
                {"qtypedido": "50.0000", "preciounitario": None},
                {"qtypedido": "10.0000", "preciounitario": None},
            ],
        }
    ]

    # Mapear las órdenes a remesas
    remesas = mapear_lista_ordenes(respuesta_api)

    # Crear payload para el API
    payload = crear_payload_api(remesas)

    # Mostrar resultado
    import json

    print(json.dumps(payload, indent=2, ensure_ascii=False))
