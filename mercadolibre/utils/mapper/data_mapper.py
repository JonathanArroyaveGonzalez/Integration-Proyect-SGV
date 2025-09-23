from typing import Optional, Dict, Any


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
        self.descripcion = descripcion
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

    @classmethod
    def from_meli_item(cls, meli_item: Dict[str, Any]) -> "ProductMapper":
        """
        Construye un ProductMapper a partir de un item de Mercado Libre.
        Si algún atributo no está presente, se asigna None.
        """
        # Extraer atributos en un dict por ID
        attributes = {attr["id"]: attr.get("value_name") for attr in meli_item.get("attributes", [])}

        # EAN / SKU / Referencia
        ean = attributes.get("GTIN") or attributes.get("SELLER_SKU")
        referencia = attributes.get("id") 

        # Peso en gramos (si existe)
        peso_attr = next((a for a in meli_item.get("attributes", []) if a["id"] == "UNIT_WEIGHT"), None)
        peso = peso_attr["values"][0]["struct"]["number"] if peso_attr and peso_attr["values"][0]["struct"] else None

        # Stock disponible
        stock = meli_item.get("available_quantity")

        return cls(
            productoean=ean or "",
            descripcion=meli_item.get("title", ""),
            referencia=meli_item.get("id", "SELLER_SKU"),
            inventariable=1,
            um1="UND",
            bodega="BOD01",
            factor=1.0,
            estado=1 if meli_item.get("status") == "active" else 0,
            qtyequivalente=float(stock) if stock is not None else None,
            costo=None,
            presentacion=attributes.get("PACKAGING_TYPE"),
            descripcioningles=None,
            item=meli_item.get("title"),
            grupo=meli_item.get("category_id"),
            subgrupo=attributes.get("LINE"),
            extension1=attributes.get("MODEL"),
            nuevoean=ean,
            tipo=attributes.get("COFFEE_TYPE"),
            f120_tipo_item=None,
            fecharegistro=meli_item.get("date_created"),
            peso=peso,
            procedencia=meli_item.get("seller_address", {}).get("city", {}).get("name"),
            proveedor=str(meli_item.get("seller_id")),
            preciounitario=meli_item.get("price"),
            observacion=meli_item.get("permalink"),
            alergenos=None
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
                cantidad=meli_item.get("available_quantity", 1),
                qtynew=None,
                fechacrea=fechacrea,
                pesobruto=None,
                qtytara=None,
                cantidad_tara=None
            )
        return None

    def __repr__(self):
        return f"BarCodeMapper(idinternoean={self.idinternoean}, codbarrasasignado={self.codbarrasasignado})"