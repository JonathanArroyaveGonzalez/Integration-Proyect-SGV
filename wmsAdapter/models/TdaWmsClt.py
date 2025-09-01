from email.policy import default
from django.db import models
from wmsAdapter.models import *
import json

class TdaWmsClt(models.Model):
    nit = models.CharField(max_length=50, blank=True, null=True)
    nombrecliente = models.CharField(db_column='nombreCliente', max_length=250, blank=True, null=True)  # Field name made lowercase.
    direccion = models.CharField(db_column='Direccion', max_length=500, blank=True, null=True)  # Field name made lowercase.
    isactivoproveedor = models.IntegerField(db_column='isActivoProveedor', blank=True, null=True)  # Field name made lowercase.
    condicionescompra = models.CharField(db_column='CondicionesCompra', max_length=6, blank=True, null=True)  # Field name made lowercase.
    codigopais = models.CharField(db_column='CodigoPais', max_length=6, blank=True, null=True)  # Field name made lowercase.
    monedadefacturacion = models.CharField(db_column='MonedaDeFacturacion', max_length=3, blank=True, null=True)  # Field name made lowercase.
    item = models.CharField(primary_key=True, max_length=50)
    activocliente = models.IntegerField(db_column='ActivoCliente', blank=True, null=True)  # Field name made lowercase.
    ciudaddestino = models.CharField(db_column='CiudadDestino', max_length=100, blank=True, null=True)  # Field name made lowercase.
    dptodestino = models.CharField(db_column='DptoDestino', max_length=100, blank=True, null=True)  # Field name made lowercase.
    paisdestino = models.CharField(db_column='PaisDestino', max_length=100, blank=True, null=True)  # Field name made lowercase.
    codciudaddestino = models.CharField(db_column='CodCiudadDestino', max_length=100, blank=True, null=True)  # Field name made lowercase.
    coddptodestino = models.CharField(db_column='CodDptoDestino', max_length=100, blank=True, null=True)  # Field name made lowercase.
    codpaisdestino = models.CharField(db_column='CodPaisDestino', max_length=100, blank=True, null=True)  # Field name made lowercase.
    fecharegistro = models.CharField(db_column='fechaRegistro', max_length=20, blank=True, null=True)  # Field name made lowercase.
    telefono = models.CharField(db_column='Telefono', max_length=100, blank=True, null=True)  # Field name made lowercase.
    cuidad = models.CharField(db_column='Cuidad', max_length=100, blank=True, null=True)  # Field name made lowercase.
    cuidaddespacho = models.CharField(db_column='CuidadDespacho', max_length=100, blank=True, null=True)  # Field name made lowercase.
    notas = models.CharField(db_column='Notas', max_length=500, blank=True, null=True)  # Field name made lowercase.
    contacto = models.CharField(max_length=200, blank=True, null=True)
    email = models.CharField(max_length=500, blank=True, null=True)
    paisdespacho = models.CharField(db_column='paisDespacho', max_length=250, blank=True, null=True)  # Field name made lowercase.
    departamentodespacho = models.CharField(db_column='departamentoDespacho', max_length=250, blank=True, null=True)  # Field name made lowercase.
    sucursaldespacho = models.CharField(db_column='sucursalDespacho', max_length=100, blank=True, null=True)  # Field name made lowercase.
    idsucursal = models.CharField(db_column='idSucursal', max_length=50, blank=True, null=True)  # Field name made lowercase.
    isactivocliente = models.IntegerField(blank=True, null=True)
    isactivoproveed = models.IntegerField(blank=True, null=True)
    estadotransferencia = models.IntegerField(blank=True, null=True)
    vendedor = models.CharField(max_length=50, blank=True, null=True)
    zip_code = models.CharField(max_length=20, blank=True, null=True)
    licencia = models.CharField(max_length=20, blank=True, null=True)
    compania = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'TDA_WMS_CLT'
        unique_together = (('item', 'nit'),)
