# -*- coding: utf-8 -*-
"""
Mapeador de órdenes a estructura Transprensa.
Convierte datos internos de órdenes al formato requerido por la API de Transprensa.
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Callable
from copy import deepcopy
import re

# =========================
#  Constantes OSAKA
# =========================
OSAKA_CLIENTE_CODIGO = "3245"
OSAKA_REMITENTE_CODIGO = "2597359"
FORMA_PAGO_CREDITO = "5"
PRODUCTO_CAJAS = "3559"
TIPO_SERVICIO_PAQUETEO = "2"
CENTRO_COSTO_MEDELLIN = "10"
DANE_MEDELLIN = "05001000"

TIPODOC_CEDULA = "1"
TIPODOC_NIT = "2"


# =========================
#  Modelos de datos
# =========================
@dataclass
class TPCliente:
    cliente_codigo: Optional[str] = OSAKA_CLIENTE_CODIGO
    tipo_documentocliente_codigo: Optional[str] = None
    cliente_documento: Optional[str] = None
    cliente_nombre1: Optional[str] = None
    cliente_nombre2: Optional[str] = None
    cliente_apellido1: Optional[str] = None
    cliente_apellido2: Optional[str] = None
    cliente_direccion: Optional[str] = None
    cliente_telefono: Optional[str] = None
    cliente_ciudad_codigo: Optional[str] = None
    cliente_email: Optional[str] = None
    cliente_tipopersona: Optional[bool] = None
    cliente_digitoverificacion: Optional[str] = None


@dataclass
class TPRemitente:
    remitente_codigo: Optional[str] = OSAKA_REMITENTE_CODIGO
    tipo_documentoremitente_codigo: Optional[str] = None
    remitente_documento: Optional[str] = None
    remitente_nombre: Optional[str] = None
    remitente_direccion: Optional[str] = None
    remitente_telefono: Optional[str] = None
    remitente_ciudad_codigo: Optional[str] = None


@dataclass
class TPDestinatario:
    destinatario_codigo: Optional[str] = None
    tipo_documentodestinatario_codigo: Optional[str] = None
    destinatario_documento: Optional[str] = None
    destinatario_nombre: Optional[str] = None
    destinatario_direccion: Optional[str] = None
    destinatario_telefono: Optional[str] = None
    destinatario_ciudad_codigo: Optional[str] = None


@dataclass
class TPDetalle:
    detalle_peso: Optional[str] = None
    detalle_cantidad: Optional[str] = None
    detalle_descripcion: Optional[str] = None
    detalle_volumen: Optional[str] = None
    detalle_valordeclarado: Optional[str] = None
    detalle_producto_codigo: Optional[str] = None


@dataclass
class TPRemesa:
    ciudad_codigo_origen: Optional[str] = None
    ciudad_codigo_destino: Optional[str] = None
    tipo_servicio: Optional[str] = TIPO_SERVICIO_PAQUETEO
    cliente: TPCliente = field(default_factory=TPCliente)
    remitente: TPRemitente = field(default_factory=TPRemitente)
    destinatario: TPDestinatario = field(default_factory=TPDestinatario)
    detalle: List[TPDetalle] = field(default_factory=list)
    remesa_total: Optional[str] = None
    remesa_manejo: Optional[str] = None
    remesa_tarifa: Optional[str] = None
    centro_costo: Optional[str] = CENTRO_COSTO_MEDELLIN
    orden_carga: Optional[str] = None
    forma_pago: Optional[str] = FORMA_PAGO_CREDITO
    documento_cliente: Optional[str] = None
    orden_compra: Optional[str] = None
    remesa_observacion: Optional[str] = "SIN VERIFICAR PESO NI CONTENIDO"
    remesa_codigo: Optional[str] = None


# =========================
#  Mapeador principal
# =========================
class RemesaMapper:
    """Mapea órdenes internas a estructura Transprensa."""

    def __init__(
        self,
        *,
        ciudadDaneResolver: Callable[[Dict[str, Any]], str],
        productCodigoResolver: Callable[[Dict[str, Any]], str],
        detalleDefaults: Optional[Dict[str, Any]] = None,
        defaults: Optional[Dict[str, Any]] = None,
    ):
        self.sources: List[Dict[str, Any]] = []
        self.defaults = defaults or {}
        self.resolvers = {
            "ciudadDane": ciudadDaneResolver,
            "producto": productCodigoResolver,
        }
        self.detalleDefaults = {
            "detalle_peso": "1",
            "detalle_cantidad": "1",
            "detalle_descripcion": "Mercancía",
            "detalle_volumen": "1",
            "detalle_valordeclarado": "0",
            "detalle_producto_codigo": PRODUCTO_CAJAS,
            **(detalleDefaults or {}),
        }

    def addSource(
        self, data: Dict[str, Any], *, tag: Optional[str] = None
    ) -> "RemesaMapper":
        """Agrega una fuente de datos al mapeador."""
        src = deepcopy(data)
        if tag:
            src["_source_tag"] = tag
        self.sources.append(src)
        return self

    def build(self) -> Dict[str, Any]:
        """Construye el payload de remesas."""
        ctx = self.mergeSources()
        remesas: List[Dict[str, Any]] = []

        orders: list = ctx.get("orders") or []
        if not orders:
            raise ValueError("No se encontraron órdenes para construir remesas.")

        for order in orders:
            remesas.append(self.buildRemesaFromOrder(ctx, order))

        payload = {"remesas": remesas}
        payload = self.sanitizeNumericFields(payload)
        self.validatePayload(payload)
        return payload

    def mergeSources(self) -> Dict[str, Any]:
        """Fusiona todas las fuentes de datos."""
        ctx: Dict[str, Any] = deepcopy(self.defaults)
        for src in self.sources:
            ctx = self.deepMerge(ctx, src)
        return ctx

    @staticmethod
    def deepMerge(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
        """Fusiona dos diccionarios recursivamente."""
        out = deepcopy(a)
        for k, v in b.items():
            if isinstance(v, dict) and isinstance(out.get(k), dict):
                out[k] = RemesaMapper.deepMerge(out[k], v)
            else:
                out[k] = deepcopy(v)
        return out

    @staticmethod
    def normalizeText(s: Optional[str]) -> str:
        """Normaliza texto eliminando espacios múltiples."""
        if s is None:
            return ""
        return re.sub(r"\s+", " ", s).strip()

    @staticmethod
    def extractFirstDigits(
        s: Optional[str], minLen: int = 7, maxLen: int = 12
    ) -> Optional[str]:
        """Extrae primeros dígitos dentro de rango."""
        if not s:
            return None
        m = re.search(rf"\b(\d{{{minLen},{maxLen}}})\b", s)
        return m.group(1) if m else None

    @staticmethod
    def extractNitWithDv(nit: Optional[str]) -> str:
        """
        Extrae NIT extrayendo solo dígitos (sin puntos ni guiones).

        Ejemplos:
        - "1045047287-4" → "10450472874"
        - "1045047287" → "1045047287"
        - "  1045047287 - 4  " → "10450472874"
        """
        nit = RemesaMapper.normalizeText(nit)
        if not nit:
            return ""

        nit = nit.replace(" ", "")
        # Extraer solo dígitos
        return re.sub(r"\D", "", nit)

    @staticmethod
    def pickFirstAvailable(d: Dict[str, Any], keys: List[str]) -> Any:
        """Retorna el primer valor disponible de una lista de claves."""
        for k in keys:
            if k in d and d[k] not in (None, ""):
                return d[k]
        return None

    @staticmethod
    def toStr(v: Any) -> Optional[str]:
        """Convierte valor a string."""
        if v is None:
            return None
        return str(v)

    @staticmethod
    def toNumeric(v: Any) -> Optional[str]:
        """Convierte a string numérico sin puntos ni guiones."""
        if v is None:
            return None
        # Extraer solo dígitos
        return re.sub(r"\D", "", str(v))

    @staticmethod
    def pruneNoneValues(d: Any) -> Any:
        """Elimina valores None, listas vacías y diccionarios vacíos."""
        if isinstance(d, dict):
            return {
                k: RemesaMapper.pruneNoneValues(v)
                for k, v in d.items()
                if v not in (None, [], {})
            }
        if isinstance(d, list):
            return [
                RemesaMapper.pruneNoneValues(x) for x in d if x not in (None, [], {})
            ]
        return d

    @staticmethod
    def sanitizeNumericFields(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Convierte campos numéricos a tipos correctos (int/float)."""
        remesas = payload.get("remesas", [])
        for remesa in remesas:
            # Códigos DANE: MANTENER COMO STRING (8 dígitos con ceros iniciales)
            # No convertir a int porque pierde los ceros iniciales
            for key in [
                "ciudad_codigo_origen",
                "ciudad_codigo_destino",
            ]:
                if key in remesa and remesa[key]:
                    try:
                        # Asegurar que es string con 8 dígitos
                        dane_str = str(remesa[key]).replace(" ", "").strip()
                        if len(dane_str) <= 8:
                            remesa[key] = dane_str
                    except (ValueError, TypeError):
                        pass

            # Centro costo, forma pago a int
            for key in ["centro_costo", "forma_pago", "tipo_servicio"]:
                if key in remesa and remesa[key]:
                    try:
                        remesa[key] = int(str(remesa[key]))
                    except (ValueError, TypeError):
                        pass

            # Detalles
            if "detalle" in remesa and isinstance(remesa["detalle"], list):
                for det in remesa["detalle"]:
                    # Números a float
                    for key in [
                        "detalle_peso",
                        "detalle_cantidad",
                        "detalle_volumen",
                        "detalle_valordeclarado",
                    ]:
                        if key in det and det[key]:
                            try:
                                det[key] = float(det[key])
                            except (ValueError, TypeError):
                                pass

                    # Código producto a int
                    if (
                        "detalle_producto_codigo" in det
                        and det["detalle_producto_codigo"]
                    ):
                        try:
                            det["detalle_producto_codigo"] = int(
                                det["detalle_producto_codigo"]
                            )
                        except (ValueError, TypeError):
                            pass

            # Destinatario ciudad código: MANTENER COMO STRING (DANE)
            dest = remesa.get("destinatario", {})
            if (
                dest
                and "destinatario_ciudad_codigo" in dest
                and dest["destinatario_ciudad_codigo"]
            ):
                try:
                    dane_str = (
                        str(dest["destinatario_ciudad_codigo"]).replace(" ", "").strip()
                    )
                    if len(dane_str) <= 8:
                        dest["destinatario_ciudad_codigo"] = dane_str
                except (ValueError, TypeError):
                    pass

        return payload

    def buildRemesaFromOrder(
        self, ctx: Dict[str, Any], order: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Construye una remesa a partir de una orden."""
        # Encabezado
        encabezado = {
            "ciudad_codigo_origen": self.resolvers["ciudadDane"](
                {"ctx": ctx, "order": order, "role": "origen"}
            ),
            "ciudad_codigo_destino": self.resolvers["ciudadDane"](
                {"ctx": ctx, "order": order, "role": "destino"}
            ),
            "tipo_servicio": TIPO_SERVICIO_PAQUETEO,
        }

        # Cliente
        cliente = TPCliente()

        # Remitente
        remitente = TPRemitente()

        # Destinatario
        nombre = self.normalizeText(self.pickFirstAvailable(order, ["nombrecliente"]))
        direccion = self.normalizeText(
            self.pickFirstAvailable(order, ["direccion_despacho"])
        )
        contactoRaw = self.pickFirstAvailable(order, ["contacto"])
        telefono = self.extractFirstDigits(contactoRaw) or ""

        nitRaw = self.pickFirstAvailable(order, ["nit"])
        numeroDoc = self.extractNitWithDv(nitRaw)

        if numeroDoc:
            # Si el NIT original tenía guión, es NIT; sino es cédula
            tipoDoc = TIPODOC_NIT if "-" in (nitRaw or "") else TIPODOC_CEDULA
        else:
            tipoDoc = TIPODOC_CEDULA
            numeroDoc = self.normalizeText(
                self.pickFirstAvailable(order, ["numpedido"]) or "0"
            )

        destinatario = TPDestinatario(
            # destinatario_codigo vacío según especificación de Transprensa
            destinatario_codigo=None,
            tipo_documentodestinatario_codigo=tipoDoc,
            destinatario_documento=numeroDoc,
            destinatario_nombre=nombre,
            destinatario_direccion=direccion,
            destinatario_telefono=telefono,
            destinatario_ciudad_codigo=encabezado["ciudad_codigo_destino"],
        )

        # Detalles
        detalles: List[TPDetalle] = []
        lines = order.get("order_detail") or order.get("lines") or []
        if isinstance(lines, dict):
            lines = [lines]

        if lines:
            for line in lines:
                articulo = line.get("articulo", {})
                descripcion = (
                    self.normalizeText(
                        articulo.get("descripcion") or line.get("descripcion", "")
                    )
                    or "CAJA"
                )
                # Usar el id numérico del artículo, si no hay usar referencia
                producto_codigo = (
                    str(articulo.get("id"))
                    if articulo.get("id")
                    else (
                        self.normalizeText(
                            articulo.get("referencia") or line.get("referencia", "")
                        )
                        or "3559"
                    )
                )
                # Valor declarado: usar preciounitario * cantidad, o cantidad si no hay precio
                precio_unitario = float(articulo.get("preciounitario") or 0)
                cantidad = float(line.get("qtyreservado", 1))
                valor_declarado = (
                    precio_unitario * cantidad if precio_unitario > 0 else cantidad
                )

                # Peso y volumen: si son 0 o falsy, usar 1 como default
                peso = float(articulo.get("peso") or line.get("peso") or 1)
                volumen = float(articulo.get("volumen") or line.get("volumen") or 1)
                peso = peso if peso > 0 else 1
                volumen = volumen if volumen > 0 else 1

                detalles.append(
                    TPDetalle(
                        detalle_cantidad=str(line.get("qtyreservado", 1)),
                        detalle_descripcion=descripcion,
                        detalle_producto_codigo=producto_codigo,
                        detalle_peso=str(peso),
                        detalle_volumen=str(volumen),
                        detalle_valordeclarado=str(valor_declarado),
                    )
                )
        else:
            detalles.append(TPDetalle(**self.detalleDefaults))

        otros = {
            "centro_costo": CENTRO_COSTO_MEDELLIN,
            "forma_pago": FORMA_PAGO_CREDITO,
            "documento_cliente": self.toNumeric(
                self.pickFirstAvailable(order, ["nit"])
            ),
            "remesa_observacion": self.toStr(
                self.pickFirstAvailable(order, ["notas"])
                or "SIN VERIFICAR PESO NI CONTENIDO"
            ),
            "remesa_codigo": self.toStr(
                self.pickFirstAvailable(order, ["numpedido"])
                or self.pickFirstAvailable(order, ["picking", "pedidorelacionado"])
            ),
        }

        remesa = TPRemesa(
            **encabezado,
            cliente=cliente,
            remitente=remitente,
            destinatario=destinatario,
            detalle=detalles,
            **otros,
        )

        return self.pruneNoneValues(asdict(remesa))

    def validatePayload(self, payload: Dict[str, Any]) -> None:
        """Valida que el payload cumpla con requisitos Transprensa."""
        errors = []
        for idx, r in enumerate(payload.get("remesas", []), start=1):
            for k in [
                "ciudad_codigo_origen",
                "ciudad_codigo_destino",
                "tipo_servicio",
                "centro_costo",
                "forma_pago",
            ]:
                if not r.get(k):
                    errors.append(f"[remesa {idx}] Falta obligatorio: {k}")

            remit = r.get("remitente", {})
            if not remit.get("remitente_codigo"):
                errors.append(
                    f"[remesa {idx}] Falta obligatorio: remitente.remitente_codigo"
                )

            dest = r.get("destinatario", {})
            for k in [
                "tipo_documentodestinatario_codigo",
                "destinatario_documento",
                "destinatario_nombre",
                "destinatario_direccion",
                "destinatario_telefono",
                "destinatario_ciudad_codigo",
            ]:
                if not dest.get(k):
                    errors.append(f"[remesa {idx}] Falta obligatorio: destinatario.{k}")

            detalles = r.get("detalle", [])
            if not detalles:
                errors.append(f"[remesa {idx}] Debe incluir al menos un detalle.")
            else:
                for j, dline in enumerate(detalles, start=1):
                    for k in [
                        "detalle_peso",
                        "detalle_cantidad",
                        "detalle_descripcion",
                        "detalle_volumen",
                        "detalle_valordeclarado",
                        "detalle_producto_codigo",
                    ]:
                        if not dline.get(k):
                            errors.append(
                                f"[remesa {idx}] Falta obligatorio en detalle {j}: {k}"
                            )

        if errors:
            raise ValueError(
                "Validación de payload Transprensa:\n - " + "\n - ".join(errors)
            )
