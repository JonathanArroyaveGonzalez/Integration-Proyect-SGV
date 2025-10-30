from email.policy import default
from django.db import models

class TdaWmsPrv(models.Model):
    nit = models.CharField(max_length=50, blank=True, null=True)
    nombrecliente = models.CharField(db_column='nombreCliente', max_length=250, blank=True, null=True)  # Field name made lowercase.
    direccion = models.CharField(max_length=250, blank=True, null=True)
    isactivoproveedor = models.IntegerField(db_column='isActivoProveedor', blank=True, null=True)  # Field name made lowercase.
    condicionescompra = models.CharField(db_column='condicionesCompra', max_length=6, blank=True, null=True)  # Field name made lowercase.
    codigopais = models.CharField(db_column='codigoPais', max_length=6, blank=True, null=True)  # Field name made lowercase.
    monedadefacturacion = models.CharField(db_column='monedaDeFacturacion', max_length=3, blank=True, null=True)  # Field name made lowercase.
    item = models.CharField(primary_key=True, max_length=50, default=None)
    activocliente = models.IntegerField(db_column='activoCliente', blank=True, null=True)  # Field name made lowercase.
    fecharegistro = models.DateTimeField(blank=True, null=True)
    estadotransferencia = models.IntegerField(blank=True, null=True)
    sucursal = models.CharField(max_length=20, blank=True, null=True)
    email = models.CharField(max_length=250, blank=True, null=True)
    beneficiario = models.IntegerField(blank=True, null=True)
    item_sucursal = models.CharField(db_column='Item_sucursal', max_length=20, blank=True, null=True)  # Field name made lowercase.
    codigoter = models.CharField(db_column='codigoTer', max_length=10, blank=True, null=True)  # Field name made lowercase.
    # id = models.AutoField()

    class Meta:
        managed = False
        db_table = 'TDA_WMS_PRV'
        