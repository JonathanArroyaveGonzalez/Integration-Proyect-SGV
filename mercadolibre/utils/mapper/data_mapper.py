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

