from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
import logging
logger = logging.getLogger(__name__)



@dataclass
class ProductMapper:
    productoean: str
    descripcion: str
    referencia: str
    inventariable: int
    um1: str
    bodega: str
    factor: float
    estado: int
    qtyequivalente: Optional[float] = 1
    presentacion: Optional[str] = None
    costo: Optional[float] = 0.0
    referenciamdc: Optional[str] = None
    descripcioningles: Optional[str] = None
    item: Optional[str] = None
    u_inv: Optional[str] = None
    grupo: Optional[str] = None
    subgrupo: Optional[str] = None
    extension1: Optional[str] = None
    extension2: Optional[str] = None
    nuevoean: Optional[str] = None
    origencompra: Optional[str] = None
    tipo: Optional[str] = None
    f120_tipo_item: Optional[str] = None
    fecharegistro: Optional[str] = None
    peso: Optional[float] = None
    procedencia: Optional[str] = None
    estadotransferencia: Optional[int] = None
    volumen: Optional[float] = 0.0
    proveedor: Optional[str] = None
    preciounitario: Optional[float] = None
    ingredientes: Optional[str] = None
    instrucciones_de_uso: Optional[str] = None
    u_inv_p: Optional[str] = None
    observacion: Optional[str] = None
    controla_status_calidad: Optional[int] = None
    alergenos: Optional[str] = None

    def __post_init__(self):
        # Truncamiento defensivo al crear el objeto
        self.descripcion = self.truncate_description(self.descripcion)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte el objeto en un diccionario, omitiendo claves con valores None o "".
        """
        return {
            k: v for k, v in self.__dict__.items()
            if v is not None and v != ""
        }

    def to_wms_format(self) -> Dict[str, Any]:
        """
        Convierte a formato requerido por el WMS, con descripción truncada adicional.
        """
        data = self.to_dict()
        if "descripcion" in data:
            data["descripcion"] = self.truncate_description(data["descripcion"])
        return data

    @staticmethod
    def truncate_description(text: Optional[str], max_length: int = 250) -> str:
        """
        Trunca inteligentemente una descripción sin cortar palabras.
        """
        if not text:
            return ""
        if len(text) <= max_length:
            return text
        truncated = text[:max_length]
        last_space = truncated.rfind(" ")
        if last_space > max_length * 0.8:
            return truncated[:last_space].strip() + "..."
        else:
            return truncated.strip() + "..."

    @classmethod
    def from_meli_item(cls, meli_item: Dict[str, Any]) -> "ProductMapper":
        attributes = {
            attr.get("id"): attr.get("value_name")
            for attr in meli_item.get("attributes", [])
        }

        ean = attributes.get("GTIN") or attributes.get("SELLER_SKU") or ""
        peso = None

        peso_attr = next(
            (a for a in meli_item.get("attributes", []) if a["id"] == "UNIT_WEIGHT"),
            None,
        )
        if peso_attr:
            values = peso_attr.get("values", [])
            if values and isinstance(values[0], dict):
                struct = values[0].get("struct")
                if struct:
                    peso = struct.get("number")

        # Descripción: usar descripción detallada si existe, o el título
        description_data = meli_item.get("description_data", {})
        plain_text = description_data.get("plain_text", "").strip()
        title = meli_item.get("title", "").strip()

        if plain_text and len(plain_text) < 50 and title:
            raw_description = f"{title} - {plain_text}"
        else:
            raw_description = plain_text or title

        return cls(
            productoean=ean,
            descripcion=raw_description,
            referencia=meli_item.get("id", ean),
            inventariable=1,
            um1="UND",
            bodega="01",
            factor=1,
            estado=1 if meli_item.get("status") == "active" else 0,
            qtyequivalente=1,
            costo=0.0,
            presentacion=attributes.get("PACKAGING_TYPE"),
            descripcioningles="",
            item=ean,
            referenciamdc=ean,
            grupo=meli_item.get("category_id"),
            subgrupo=attributes.get("LINE"),
            extension1=attributes.get("MODEL"),
            nuevoean=ean,
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
        return (
            f"<ProductMapper ean={self.productoean} "
            f"desc='{self.descripcion[:20]}...' estado={self.estado}>"
        )

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

@dataclass
class InventoryMapper:
    """
    Class representing the mapping of inventory data.

    Attributes:
        bod (str): Bodega donde se almacena el producto. Default = "01".
        ubicacion (str): Ubicación específica dentro de la bodega. Default = "01".
        productoean (str): Código EAN del producto.
        descripcion (str): Descripción del producto.
        fecharegistro (Optional[str]): Fecha de registro del producto.
        codigoalmacen (Optional[str]): Código del almacén.
        estadodetransferencia (Optional[int]): Estado de la transferencia.
        referencia (Optional[str]): Referencia del producto.
        valor (Optional[float]): Valor del producto. Default = 0.0.
        tipo_inventario (Optional[str]): Tipo de inventario al que pertenece el producto.
        etl (Optional[str]): Estado ETL del registro.
        fecha_ultima_actualizacion (Optional[str]): Fecha de la última actualización.
        fecha_prox_actualizacion (Optional[str]): Fecha de la próxima actualización.
        saldopt (Optional[float]): Saldo del producto terminado. Default = 0.0.
        cantbloqueadoerp (Optional[float]): Cantidad bloqueada en el ERP. Default = 0.0.
        saldowms (Optional[float]): Saldo del producto en el WMS. Default = 0.0.
    """

    bod: str = "01"
    ubicacion: str = "01"
    productoean: str = ""       # default vacío
    descripcion: str = ""       # default vacío
    fecharegistro: Optional[str] = None
    codigoalmacen: Optional[str] = "0"
    estadodetransferencia: Optional[int] = 0
    referencia: Optional[str] = None
    valor: Optional[float] = 0.0
    tipo_inventario: Optional[str] = "0"
    etl: Optional[str] = None
    fecha_ultima_actualizacion: Optional[str] = None
    fecha_prox_actualizacion: Optional[str] = None

    saldopt: Optional[float] = 0.0  # default definido
    cantbloqueadoerp: Optional[float] = 0.0
    saldowms: Optional[float] = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte el objeto en un diccionario, omitiendo claves con valores None o "".
        """
        return {
            k: v for k, v in self.__dict__.items()
            if v is not None and v != ""
        }

    def to_wms_format(self) -> Dict[str, Any]:
        """
        Convierte a formato requerido por el WMS.
        """
        data = self.to_dict()
        # Aquí podrías aplicar reglas específicas para WMS, ej:
        if "descripcion" in data:
            data["descripcion"] = self.truncate_description(data["descripcion"])
        return data

    @staticmethod
    def truncate_description(text: Optional[str], max_length: int = 250) -> str:
        """
        Trunca inteligentemente una descripción sin cortar palabras.
        """
        if not text:
            return ""
        if len(text) <= max_length:
            return text
        truncated = text[:max_length]
        last_space = truncated.rfind(" ")
        if last_space > max_length * 0.8:
            return truncated[:last_space].strip() + "..."
        else:
            return truncated.strip() + "..."

    @classmethod
    def from_meli_item(cls, meli_item: Dict[str, Any]) -> "InventoryMapper":
        attributes = {
            attr.get("id"): attr.get("value_name")
            for attr in meli_item.get("attributes", [])
        }

        ean = attributes.get("GTIN") or attributes.get("SELLER_SKU") or ""
        id = meli_item.get("id", ean)
        quantity = meli_item.get("available_quantity", 0)
        date_created = datetime.now().isoformat(timespec="milliseconds")
        last_updated = meli_item.get("last_updated")

        # Descripción: usar descripción detallada si existe, o el título
        description_data = meli_item.get("description_data", {})
        plain_text = description_data.get("plain_text", "").strip()
        title = meli_item.get("title", "").strip()

        if plain_text and len(plain_text) < 50 and title:
            raw_description = f"{title} - {plain_text}"
        else:
            raw_description = plain_text or title

        return cls(
            productoean= ean,
            descripcion= raw_description,
            fecharegistro= date_created,
            codigoalmacen= "0",
            estadodetransferencia= 0,
            referencia= id,
            valor= 0.0,
            tipo_inventario= "0",
            etl= None,
            fecha_ultima_actualizacion= last_updated,
            fecha_prox_actualizacion= None,

            saldopt= float(quantity),
            cantbloqueadoerp= 0.0,
            saldowms= 0.0
        )

    def __repr__(self):
        return (
            f"<InventoryMapper ean={self.productoean} "
            f"bod={self.bod} saldo_wms={self.saldowms}>"
        )



@dataclass
class OrderMapper:
    """
    Mapper único para órdenes de MercadoLibre a formato WMS.
    Mapea tanto el header de la orden como sus líneas de detalle.
    """
    
    # ============ HEADER FIELDS (Required) ============
    tipodocto: str
    doctoerp: str
    numpedido: str
    item: str
    nombrecliente: str
    direccion_despacho: str
    ciudad_despacho: str
    ciudad: str
    estadoerp: str
    bodega: str
    order_detail: List[Dict[str, Any]]
    
    # ============ HEADER FIELDS (Optional) ============
    fechaplaneacion: Optional[str] = None
    f_pedido: Optional[str] = None
    contacto: Optional[str] = None
    email: Optional[str] = None
    notas: Optional[str] = None
    pais_despacho: Optional[str] = None
    departamento_despacho: Optional[str] = None
    sucursal_despacho: Optional[str] = None
    idsucursal: Optional[str] = None
    pedidorelacionado: Optional[str] = None
    cargue: Optional[str] = None
    nit: Optional[str] = None
    estadopicking: Optional[int] = None
    fecharegistro: Optional[str] = None
    fpedido: Optional[str] = None
    fechtrans: Optional[str] = None
    transportadora: Optional[str] = None
    centrooperacion: Optional[str] = None
    picking_batch: Optional[str] = None
    field_condicionpago: Optional[str] = None
    field_documentoreferencia: Optional[str] = None
    vendedor2: Optional[str] = None
    numguia: Optional[str] = None
    f_ultima_actualizacion: Optional[str] = None
    bodegaerp: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for WMS API, omitting None values."""
        return {
            k: v for k, v in self.__dict__.items()
            if v is not None
        }

    def to_wms_format(self) -> List[Dict[str, Any]]:
        """Convert to WMS API format (array with single order)."""
        return [self.to_dict()]

    @staticmethod
    def _format_date(date_str: Optional[str]) -> Optional[str]:
        """
        Format ISO date to SQL Server format (YYYY-MM-DD HH:MM:SS).
        
        Args:
            date_str: ISO format date string
            
        Returns:
            Formatted date string or None
        """
        if not date_str:
            return None
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            logger.warning(f"Could not parse date: {date_str}, error: {e}")
            return None

    @staticmethod
    def _build_order_detail_item(
        order_item: Dict[str, Any],
        order_id: str,
        buyer_id: str,
        bodega: str
    ) -> Dict[str, Any]:
        """
        Build a single order detail line item.
        
        Args:
            order_item: Single item from order_items array
            order_id: MercadoLibre order ID
            buyer_id: Buyer ID
            bodega: Warehouse code
            
        Returns:
            Dictionary with order detail fields
        """
        item = order_item.get("item", {})
        item_id = item.get("id", "")
        
        # Get EAN/SKU
        ean = item_id  # Default to item ID
        
        # Try to get from variation_attributes
        variation_attrs = item.get("variation_attributes", [])
        for attr in variation_attrs:
            if attr.get("id") == "GTIN":
                ean = attr.get("value_name", ean)
                break
        
        # Try seller_sku if no GTIN
        if ean == item_id and item.get("seller_sku"):
            ean = item.get("seller_sku")
        
        quantity = float(order_item.get("quantity", 0))
        unit_price = float(order_item.get("unit_price", 0))
        
        # Truncate description
        description = item.get("title", "")[:250]
        
        return {
            "referencia": item_id,
            "refpadre": item_id,
            "descripcion": description,
            "qtypedido": quantity,
            "qtyreservado": quantity,
            "productoean": ean,
            "costo": unit_price,
            "bodega": bodega,
            "tipodocto": "",
            "doctoerp": order_id,
            "qtyenpicking": 0.0,
            "estadodetransferencia": 0,
            "item": buyer_id,
            "idco": bodega,
            "preciounitario": unit_price,
            "descripcionco": description,
            "factor": 1,
            "numpedido": order_id,
            "field_qtypedidabase": quantity
        }

    @classmethod
    def from_meli_order(
        cls,
        meli_order: Dict[str, Any],
        buyer_data: Optional[Dict[str, Any]] = None,
        bodega: str = "Principal"
    ) -> "OrderMapper":
        """
        Create OrderMapper from MercadoLibre order data.
        
        Args:
            meli_order: Complete order data from MercadoLibre API
            buyer_data: Optional buyer information from /users/{buyer_id} endpoint
            bodega: Warehouse code (default: "381")
            
        Returns:
            OrderMapper instance with all mapped fields
        """
        # ============ EXTRACT ORDER ID ============
        order_id = str(meli_order.get("id", ""))
        
        # ============ BUYER INFORMATION ============
        buyer = meli_order.get("buyer", {})
        buyer_id = str(buyer.get("id", ""))
        
        if buyer_data:
            # Use detailed buyer data from /users endpoint
            first_name = buyer_data.get("first_name", "")
            last_name = buyer_data.get("last_name", "")
            buyer_name = f"{first_name} {last_name}".strip() or buyer_data.get("nickname", "Unknown")
            buyer_email = buyer_data.get("email")
            
            # Phone
            buyer_phone_data = buyer_data.get("phone", {})
            if buyer_phone_data:
                area = buyer_phone_data.get("area_code", "")
                number = buyer_phone_data.get("number", "")
                buyer_phone = f"{area}{number}" if area and number else None
            else:
                buyer_phone = None
            
            # NIT from identification
            identification = buyer_data.get("identification", {})
            nit = identification.get("number") or buyer_id
        else:
            # Fallback to basic buyer info from order
            buyer_name = buyer.get("nickname", "Unknown")
            buyer_email = None
            buyer_phone = None
            nit = buyer_id
        
        # ============ SHIPPING INFORMATION ============
        shipping = meli_order.get("shipping", {})
        shipping_id = shipping.get("id")
        
        # For orders without shipping details, use defaults
        city = "N/A"
        state = ""
        country = ""
        full_address = "N/A"
        shipping_method = "Standard"
        
        # Try to get receiver address if available
        receiver_address = shipping.get("receiver_address", {})
        if receiver_address:
            city_data = receiver_address.get("city", {})
            city = city_data.get("name", "N/A")
            
            state_data = receiver_address.get("state", {})
            state = state_data.get("name", "")
            
            country_data = receiver_address.get("country", {})
            country = country_data.get("id", "")
            
            # Build address
            street_name = receiver_address.get("street_name", "")
            street_number = receiver_address.get("street_number", "")
            
            if street_name or street_number:
                address_parts = [street_name, street_number]
                full_address = ", ".join(filter(None, address_parts))
        
        # Shipping method
        if shipping.get("shipping_method_id"):
            shipping_method = shipping.get("shipping_method_id")
        
        # ============ ORDER STATUS ============
        status = meli_order.get("status", "")
        
        # Map ML status to WMS status
        if status == "paid":
            estado_picking = 15
            estado_erp = "99"
        elif status == "confirmed":
            estado_picking = 3
            estado_erp = "1"
        elif status == "cancelled":
            estado_picking = 0
            estado_erp = "0"
        else:
            estado_picking = 0
            estado_erp = "0"
        
        # ============ PAYMENT INFORMATION ============
        payments = meli_order.get("payments", [])
        payment_method = ""
        if payments and len(payments) > 0:
            payment_method = payments[0].get("payment_type_id", "")
        
        # ============ DATES ============
        date_created = meli_order.get("date_created")
        date_closed = meli_order.get("date_closed")
        
        f_pedido = cls._format_date(date_created)
        fecharegistro = cls._format_date(date_created)
        fechtrans = cls._format_date(date_closed)
        f_ultima_actualizacion = cls._format_date(date_created)
        
        # ============ ORDER ITEMS (DETAIL) ============
        order_items = meli_order.get("order_items", [])
        order_details = [
            cls._build_order_detail_item(item, order_id, buyer_id, bodega)
            for item in order_items
        ]
        
        # ============ BUILD NOTES ============
        notes_parts = [f"ML Order: {order_id}"]
        if status:
            notes_parts.append(f"Status: {status}")
        if payment_method:
            notes_parts.append(f"Payment: {payment_method}")
        
        # Add tags if available
        tags = meli_order.get("tags", [])
        if tags:
            notes_parts.append(f"Tags: {', '.join(tags)}")
        
        notas = " | ".join(notes_parts)
        
        # ============ RETURN MAPPED ORDER ============
        return cls(
            # Required fields
            tipodocto="ML",
            doctoerp=order_id,
            numpedido=order_id,
            item=buyer_id,
            nombrecliente=buyer_name,
            direccion_despacho=full_address,
            ciudad_despacho=city,
            ciudad=city,
            estadoerp=estado_erp,
            bodega="Principal",
            order_detail=order_details,
            
            # Optional fields
            f_pedido=f_pedido,
            contacto=buyer_phone or buyer_name,
            email=buyer_email,
            notas=notas,
            pais_despacho=country.lower() if country else None,
            departamento_despacho=state,
            nit=nit,
            estadopicking=estado_picking,
            fecharegistro=fecharegistro,
            fpedido=f_pedido,
            fechtrans=fechtrans,
            transportadora=shipping_method,
            centrooperacion=bodega,
            field_condicionpago=payment_method,
            field_documentoreferencia=order_id,
            vendedor2="MercadoLibre",
            numguia=str(shipping_id) if shipping_id else None,
            f_ultima_actualizacion=f_ultima_actualizacion,
            bodegaerp="Principal"
        )

    def __repr__(self):
        return (
            f"OrderMapper(order_id={self.doctoerp}, buyer={self.nit}, "
            f"items={len(self.order_detail)}, status={self.estadoerp})"
        )
