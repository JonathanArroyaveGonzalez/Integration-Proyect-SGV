from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional
import re
from transprensa.services.clientService import  get_ciudad_codigo_by_nombre
from dotenv import load_dotenv
import os

load_dotenv()


#  Constantes OSAKA
CLIENTE_CODIGO = os.getenv("CLIENTE_CODIGO")
REMITENTE_CODIGO = os.getenv("REMITENTE_CODIGO")
FORMA_PAGO_CREDITO = "5"
PRODUCTO_CAJAS = "3559"
TIPO_SERVICIO_PAQUETEO = "2"
CENTRO_COSTO_MEDELLIN = "10"
DANE_MEDELLIN = "05001000"
TIPODOC_CEDULA = "1"
TIPODOC_NIT = "2"


#  Utilidades
def obtener_codigo_dane(ciudad: str) -> str:
    """Obtiene código DANE de ciudad o retorna el de Medellín por defecto."""
    if not ciudad:
        return "05001000"
    return get_ciudad_codigo_by_nombre(ciudad.upper().strip()) or "05001000"



def limpiar_espacios(valor: Any) -> Any:
    """
    Elimina espacios en blanco al inicio y final de cadenas de texto.
    Si el valor es None o no es string, lo retorna sin cambios.
    """
    if isinstance(valor, str):
        return valor.strip()
    return valor


def create_guia_number(picking, bigpedido):
    # Extrae solo los dígitos usando expresión regular
    solo_numeros_picking = re.sub(r"\D", "", picking or "")
    solo_numeros_bigpedido = re.sub(r"\D", "", bigpedido or "")

    # Une los dos valores
    pedido_unido = solo_numeros_picking + solo_numeros_bigpedido
    return pedido_unido


# Definición de dataclasses
@dataclass
class Cliente:
    cliente_codigo: Optional[str] = CLIENTE_CODIGO
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
    remitente_codigo: Optional[str] = REMITENTE_CODIGO
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


# Funciones de mapeo
def get_data_from_guia(guia_data: Dict[str, Any]):
    """Extrae datos de guía según su estructura. (Con y sin detalle)"""
    # validar estructura de datos
    if "is_detail_0" in guia_data:
        sin_detalle = guia_data.get("is_detail_0", {}).get("data", [{}])[0]
        con_detalle = guia_data.get("is_detail_1", {}).get("data", [{}])[0]
    else:
        return None

    return sin_detalle, con_detalle


def mapear_guia_a_remesa(guia_data: Dict[str, Any]) -> Optional[Remesa]:
    """Mapea datos de guía consultada a Remesa."""
    try:
        dataguide, detalle = get_data_from_guia(guia_data)
        #guide_number = "1089"  # Valor temporal fijo para pruebas
        guide_number = create_guia_number(guia_data.get("picking", ""), guia_data.get("bigpedido", ""))
        print("Numero de guia Generado:", guide_number)
        # Extraer datos del destinatario
        destinatario = Destinatario(
            destinatario_codigo="",
            tipo_documentodestinatario_codigo=TIPODOC_NIT,
            destinatario_documento=limpiar_espacios(dataguide.get("nit_destinatario"))
            .replace("-", "")
            .strip(),
            destinatario_nombre=limpiar_espacios(dataguide.get("nombre_destinatario")),
            destinatario_direccion=limpiar_espacios(
                dataguide.get("direccion_destinatario")
            ),
            destinatario_telefono=limpiar_espacios(
                dataguide.get("telefono_destinatario", "")
            )
            or "0000000000",
            
            destinatario_ciudad_codigo=obtener_codigo_dane(limpiar_espacios(dataguide.get("ciudad_destinatario"))),
        )
        print("Codigo DANE Destinatario:", obtener_codigo_dane(limpiar_espacios(dataguide.get("ciudad_destinatario"))))
        # Detalle
        detalle = Detalle(
            detalle_peso=detalle.get("peso_real", "0"),
            detalle_volumen=detalle.get("volumen", "0"),
            detalle_valordeclarado=dataguide.get("valor_declarado", "0"),
            detalle_producto_codigo=PRODUCTO_CAJAS,
            detalle_cantidad=detalle.get("unidades", ""),
            detalle_descripcion=limpiar_espacios(detalle.get("descripcion", "")),
        )

        # Crear remesa completa
        remesa = Remesa(
            ciudad_codigo_origen=DANE_MEDELLIN,
            ciudad_codigo_destino=destinatario.destinatario_ciudad_codigo,
            tipo_servicio=TIPO_SERVICIO_PAQUETEO,
            cliente=Cliente(),  # Usar valores por defecto
            remitente=Remitente(),  # Usar valores por defecto
            destinatario=destinatario,
            detalle=detalle,
            remesa_total="",
            remesa_manejo="",
            remesa_tarifa="",
            centro_costo=CENTRO_COSTO_MEDELLIN,
            orden_carga="",
            forma_pago=FORMA_PAGO_CREDITO,
            documento_cliente=limpiar_espacios(dataguide.get("referencia", "")),
            orden_compra="",
            remesa_observacion=limpiar_espacios(dataguide.get("observaciones", ""))
            or "SIN VERIFICAR PESO NI CONTENIDO",
            remesa_codigo=guide_number,
        )
        return remesa

    except Exception as e:
        print(f"Error mapeando guía: {e}")
        return None


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
        "detalle": [asdict(d) for d in remesa.detalle]
        if isinstance(remesa.detalle, list)
        else [asdict(remesa.detalle)],
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
        remesas: Lista de objetos Remesa ya mapeados

    Returns:
        Diccionario con el formato esperado por el API
    """
    return {"remesas": [remesa_a_dict(r) for r in remesas if r]}
