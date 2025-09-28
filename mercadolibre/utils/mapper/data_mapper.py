from typing import Optional, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ProductMapper:
    def __init__(
        self,
        productoean: str,
        descripcion: str,
        referencia: str,
        inventariable: int,
        um1: str,
        bodega: str,
        factor: float,
        estado: int,
        qtyequivalente: Optional[float] = None,
        presentacion: Optional[str] = None,
        costo: Optional[float] = None,
        referenciamdc: Optional[str] = None,
        descripcioningles: Optional[str] = None,
        item: Optional[str] = None,
        u_inv: Optional[str] = None,
        grupo: Optional[str] = None,
        subgrupo: Optional[str] = None,
        extension1: Optional[str] = None,
        extension2: Optional[str] = None,
        nuevoean: Optional[str] = None,
        origencompra: Optional[str] = None,
        tipo: Optional[str] = None,
        f120_tipo_item: Optional[str] = None,
        fecharegistro: Optional[str] = None,
        peso: Optional[float] = None,
        procedencia: Optional[str] = None,
        estadotransferencia: Optional[int] = None,
        volumen: Optional[float] = None,
        proveedor: Optional[str] = None,
        preciounitario: Optional[float] = None,
        ingredientes: Optional[str] = None,
        instrucciones_de_uso: Optional[str] = None,
        u_inv_p: Optional[str] = None,
        observacion: Optional[str] = None,
        controla_status_calidad: Optional[int] = None,
        alergenos: Optional[str] = None,
    ):
        self.productoean = productoean
        # 🔒 Truncar siempre al asignar
        self.descripcion = ProductMapper.truncate_description(descripcion)
        self.referencia = referencia
        self.inventariable = inventariable
        self.um1 = um1
        self.presentacion = presentacion
        self.costo = costo
        self.referenciamdc = referenciamdc
        self.descripcioningles = descripcioningles
        self.item = item
        self.u_inv = u_inv
        self.grupo = grupo
        self.subgrupo = subgrupo
        self.extension1 = extension1
        self.extension2 = extension2
        self.nuevoean = nuevoean
        self.qtyequivalente = qtyequivalente
        self.origencompra = origencompra
        self.tipo = tipo
        self.factor = factor
        self.f120_tipo_item = f120_tipo_item
        self.fecharegistro = fecharegistro
        self.peso = peso
        self.bodega = bodega
        self.procedencia = procedencia
        self.estadotransferencia = estadotransferencia
        self.volumen = volumen
        self.proveedor = proveedor
        self.preciounitario = preciounitario
        self.ingredientes = ingredientes
        self.instrucciones_de_uso = instrucciones_de_uso
        self.u_inv_p = u_inv_p
        self.observacion = observacion
        self.controla_status_calidad = controla_status_calidad
        self.estado = estado
        self.alergenos = alergenos

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if v is not None}

    def to_wms_format(self) -> Dict[str, Any]:
        """
        Convierte el ProductMapper al formato requerido por el WMS
        """
        data = self.to_dict()
        # 🔒 Re-truncar antes de enviar (doble seguridad)
        if "descripcion" in data:
            data["descripcion"] = ProductMapper.truncate_description(data["descripcion"])
        return data

    @staticmethod
    def truncate_description(text: str, max_length: int = 250) -> str:
        """
        Trunca inteligentemente una descripción sin cortar palabras.
        """
        if not text or len(text) <= max_length:
            return text

        truncated = text[:max_length]
        last_space = truncated.rfind(" ")

        if last_space > max_length * 0.8:  # Evitar cortar palabra al final
            return truncated[:last_space].strip() + "..."
        else:
            return truncated.strip() + "..."

    @classmethod
    def from_meli_item(cls, meli_item: Dict[str, Any]) -> "ProductMapper":
        attributes = {attr["id"]: attr.get("value_name") for attr in meli_item.get("attributes", [])}

        ean = attributes.get("GTIN") or attributes.get("SELLER_SKU")
        referencia = attributes.get("id")

        peso_attr = next((a for a in meli_item.get("attributes", []) if a["id"] == "UNIT_WEIGHT"), None)
        peso = peso_attr["values"][0]["struct"]["number"] if peso_attr and peso_attr["values"][0]["struct"] else None

        stock = meli_item.get("available_quantity")

        # Descripción detallada si existe, si no usar title
        description_data = meli_item.get("description_data")
        plain_text = description_data.get("plain_text") if description_data else None
        raw_description = plain_text.strip() if plain_text else meli_item.get("title", "")

        # 🔒 Truncar siempre
        descripcion = ProductMapper.truncate_description(raw_description)

        return cls(
            productoean=ean or "",
            descripcion=descripcion,
            referencia=meli_item.get("id", "SELLER_SKU"),
            inventariable=1,
            um1="UND",
            bodega="01",
            factor=1,
            estado=1 if meli_item.get("status") == "active" else 0,
            qtyequivalente=1,
            costo=0.0,
            presentacion=attributes.get("PACKAGING_TYPE"),
            descripcioningles=None,
            item=ean,
            referenciamdc=ean,
            grupo=meli_item.get("category_id"),
            subgrupo=attributes.get("LINE"),
            extension1=attributes.get("MODEL"),
            nuevoean=ean,
            #tipo=attributes.get("COFFEE_TYPE"),
            tipo="Producto terminado",
            f120_tipo_item=None,
            fecharegistro=meli_item.get("date_created"),
            peso=peso,
            procedencia=meli_item.get("seller_address", {}).get("state", {}).get("name"),
            volumen=0,
            proveedor=str(meli_item.get("seller_id")),
            preciounitario=meli_item.get("price"),
            observacion=meli_item.get("permalink"),
            alergenos=None,
        )

    def __repr__(self):
        return f"ProductMapper({self.productoean}, {self.descripcion}, qty={self.qtyequivalente}, estado={self.estado})"

class BarCodeMapper:
    def __init__(
        self, 
        idinternoean: str, 
        codbarrasasignado: str, 
        cantidad: int = 1,
        qtynew: Optional[float] = None,
        fechacrea: Optional[str] = None,
        pesobruto: Optional[float] = None,
        qtytara: Optional[float] = None,
        cantidad_tara: Optional[float] = None
    ):
        self.idinternoean = idinternoean
        self.codbarrasasignado = codbarrasasignado
        self.cantidad = cantidad
        self.qtynew = qtynew
        self.fechacrea = fechacrea
        self.pesobruto = pesobruto
        self.qtytara = qtytara
        self.cantidad_tara = cantidad_tara

    def to_dict(self) -> Dict[str, Any]:
        return {
            "idinternoean": self.idinternoean,
            "codbarrasasignado": self.codbarrasasignado,
            "cantidad": self.cantidad,
            "qtynew": self.qtynew,
            "fechacrea": self.fechacrea,
            "pesobruto": self.pesobruto,
            "qtytara": self.qtytara,
            "cantidad_tara": self.cantidad_tara
        }

    @classmethod
    def from_meli_item(cls, meli_item: Dict[str, Any]) -> Optional["BarCodeMapper"]:
        """
        Construye un BarCodeMapper a partir de un item de Mercado Libre.
        Si no se encuentra un EAN válido, retorna None.
        """
        from datetime import datetime
        
        attributes = {attr["id"]: attr.get("value_name") for attr in meli_item.get("attributes", [])}
        ean = attributes.get("GTIN") or attributes.get("SELLER_SKU")

        if ean :
            # Formatear fecha de creación
            fecha_creacion = meli_item.get("date_created")
            if fecha_creacion:
                # Convertir a formato ISO con milisegundos si es necesario
                try:
                    fecha_dt = datetime.fromisoformat(fecha_creacion.replace('Z', '+00:00'))
                    fechacrea = fecha_dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]  # Formato con 3 decimales
                except (ValueError, AttributeError):
                    fechacrea = fecha_creacion
            else:
                fechacrea = None

            return cls(
                idinternoean=ean,
                codbarrasasignado=ean,
                #cantidad=meli_item.get("available_quantity", 1),
                cantidad=1,
                qtynew=None,
                fechacrea=fechacrea,
                pesobruto=None,
                qtytara=None,
                cantidad_tara=None
            )
        return None

    def __repr__(self):
        return f"BarCodeMapper(idinternoean={self.idinternoean}, codbarrasasignado={self.codbarrasasignado})"
    
class CustomerMapper:
    def __init__(
        self,
        nit: Optional[str] = None,
        nombrecliente: Optional[str] = None,
        direccion: Optional[str] = None,
        isactivoproveedor: Optional[int] = None,
        condicionescompra: Optional[str] = None,
        codigopais: Optional[str] = None,
        monedadefacturacion: Optional[str] = None,
        item: Optional[str] = None,
        activocliente: Optional[int] = None,
        ciudaddestino: Optional[str] = None,
        dptodestino: Optional[str] = None,
        paisdestino: Optional[str] = None,
        codciudaddestino: Optional[str] = None,
        coddptodestino: Optional[str] = None,
        codpaisdestino: Optional[str] = None,
        fecharegistro: Optional[str] = None,
        telefono: Optional[str] = None,
        cuidad: Optional[str] = None,
        cuidaddespacho: Optional[str] = None,
        notas: Optional[str] = None,
        contacto: Optional[str] = None,
        email: Optional[str] = None,
        paisdespacho: Optional[str] = None,
        departamentodespacho: Optional[str] = None,
        sucursaldespacho: Optional[str] = None,
        idsucursal: Optional[str] = None,
        isactivocliente: Optional[int] = None,
        isactivoproveed: Optional[int] = None,
        estadotransferencia: Optional[int] = None,
        vendedor: Optional[str] = None,
        zip_code: Optional[str] = None,
        licencia: Optional[str] = None,
        compania: Optional[str] = None,
    ):
        self.nit = nit
        self.nombrecliente = nombrecliente
        self.direccion = direccion
        self.isactivoproveedor = isactivoproveedor
        self.condicionescompra = condicionescompra
        self.codigopais = codigopais
        self.monedadefacturacion = monedadefacturacion
        self.item = item
        self.activocliente = activocliente
        self.ciudaddestino = ciudaddestino
        self.dptodestino = dptodestino
        self.paisdestino = paisdestino
        self.codciudaddestino = codciudaddestino
        self.coddptodestino = coddptodestino
        self.codpaisdestino = codpaisdestino
        self.fecharegistro = fecharegistro
        self.telefono = telefono
        self.cuidad = cuidad
        self.cuidaddespacho = cuidaddespacho
        self.notas = notas
        self.contacto = contacto
        self.email = email
        self.paisdespacho = paisdespacho
        self.departamentodespacho = departamentodespacho
        self.sucursaldespacho = sucursaldespacho
        self.idsucursal = idsucursal
        self.isactivocliente = isactivocliente
        self.isactivoproveed = isactivoproveed
        self.estadotransferencia = estadotransferencia
        self.vendedor = vendedor
        self.zip_code = zip_code
        self.licencia = licencia
        self.compania = compania

    def to_dict(self) -> Dict[str, Any]:
        """
        Serializa el objeto a un diccionario filtrando None
        """
        return {k: v for k, v in self.__dict__.items() if v is not None}

    @classmethod
    def from_meli_customer(cls, ml_customer_data: Dict[str, Any]) -> "CustomerMapper":
        """
        Crea un CustomerMapper desde la respuesta de MercadoLibre.
        Convierte fecha al formato YYYY-MM-DD HH:MM:SS para SQL Server.
        """
        try:
            nit = ml_customer_data.get("identification", {}).get("number")
            nombrecliente = f"{ml_customer_data.get('first_name', '')} {ml_customer_data.get('last_name', '')}".strip()
            direccion = ml_customer_data.get("address", {}).get("address")
            ciudad = ml_customer_data.get("address", {}).get("city")
            codigopais = ml_customer_data.get("country_id")
            zip_code = ml_customer_data.get("address", {}).get("zip_code")
            telefono = None
            phone_obj = ml_customer_data.get("phone")
            if phone_obj and phone_obj.get("area_code") and phone_obj.get("number"):
                telefono = f"{phone_obj.get('area_code')}{phone_obj.get('number')}"
            email = ml_customer_data.get("email")
            item = str(ml_customer_data.get("id"))

            # === Conversión de fecha para SQL Server ===
            fecharegistro = None
            fecha_raw = ml_customer_data.get("registration_date")
            if fecha_raw:
                try:
                    dt = datetime.fromisoformat(fecha_raw.replace("Z", "+00:00"))
                    fecharegistro = dt.strftime("%Y-%m-%d %H:%M:%S")
                except Exception as e:
                    logger.warning(f"No se pudo parsear fecha: {fecha_raw}, error: {e}")

            return cls(
                nit=nit,
                nombrecliente=nombrecliente
                or ml_customer_data.get("nickname"),  # TODO : Quitar nickame
                direccion=direccion,
                fecharegistro=fecharegistro,
                codigopais=codigopais,
                telefono=telefono,
                cuidad=ciudad,
                contacto=nombrecliente,
                email=email,
                zip_code=zip_code,
                item=item,
                isactivocliente=1,
            )

        except Exception as e:
            logger.error(f"Error mapeando customer: {e}")
            return None

    def __repr__(self):
        return f"CustomerMapper({self.nombrecliente}, nit={self.nit}, item={self.item})"
