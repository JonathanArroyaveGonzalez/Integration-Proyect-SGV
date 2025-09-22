from typing import Optional, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


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
                nombrecliente=nombrecliente,
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
