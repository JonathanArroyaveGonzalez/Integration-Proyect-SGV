from django.utils import timezone

from wmsAdapter.functions.TdaWmsEuk.create import create_euk
from wmsAdapter.models import TdaWmsEuk

def create_header_purchase_order(db_name, order, supplier):
    header = order["encabezado"]
    principal_data = order["datosprincipales"]

    doctoerp = header["snumsop"]
    ordenfecha = header["fprocesam"]

    bod = principal_data["iinventario"]
    
    # Extracting client information
    item = supplier["item"]
    nombre = supplier["nombrecliente"]
    email = supplier["email"]
    contacto = supplier["direccion"]

    fecha_actual = timezone.now().isoformat()

    neweuk = {
        "tipodocto": "ORC",
        "doctoerp": doctoerp,
        "numdocumento": doctoerp,
        "fecha": ordenfecha,
        "item": item,
        "nombreproveedor": nombre,
        "contacto": contacto,
        "email": email,
        "nit": item,
        "estadodocumentoubicacion": 1,
        "fecharegistro": fecha_actual,
        "bl": None,
        "contenedor": None,
        "embarque": None,
        "unido": doctoerp + '-' + doctoerp,
        "etd": None,
        "eta": None,
        "codigoarticulo": None,
        "f_ultima_actualizacion": fecha_actual,
        "bodega": "01",
        "bodegaerp": bod
    }

    response = create_euk(None, db_name, neweuk)
    if response == 'created successfully':
        euk = list(TdaWmsEuk.objects.using(db_name).filter(doctoerp=doctoerp).values())
        return euk[0]
    else:
        raise ValueError('Creating euk error')