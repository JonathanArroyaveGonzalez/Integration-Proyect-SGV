from django.db import models
from wmsAdapter.models import *

class TdaWmsEpn(models.Model):
    tipodocto = models.CharField(max_length=50)
    doctoerp = models.CharField(db_column='doctoERP', max_length=20)  # Field name made lowercase.
    # picking = models.CharField(primary_key=True, max_length=20)
    picking = models.AutoField(primary_key=True)
    numpedido = models.CharField(max_length=50)
    fechaplaneacion = models.DateTimeField(blank=True, null=True)
    fechapedido = models.DateTimeField(blank=True, null=True)
    # item = models.ForeignKey('TdaWmsPrv', models.DO_NOTHING, db_column='item')
    item = models.CharField(db_column='item', max_length=50)
    fecharegistro = models.DateTimeField(blank=True, null=True)
    bodega = models.CharField(max_length=20)
    estadodetransferencia = models.IntegerField(blank=True, null=True)
    fechatransferencia = models.DateTimeField(blank=True, null=True)
    descripcion = models.CharField(max_length=200, blank=True, null=True)
    cantidad = models.IntegerField()
    unidadempaque = models.CharField(max_length=20, blank=True, null=True)
    cantidadempaque = models.IntegerField()
    productoean = models.CharField(db_column='productoEAN', max_length=50)  # Field name made lowercase.
    referencia = models.CharField(max_length=50, blank=True, null=True)
    item_art = models.CharField(max_length=50, blank=True, null=True)
    planificador = models.CharField(max_length=50, blank=True, null=True)
    estadoerp = models.CharField(db_column='estadoERP', max_length=20, blank=True, null=True)  # Field name made lowercase.
    qtyenpicking = models.DecimalField(max_digits=18, decimal_places=4, blank=True, null=True)
    pedproveedor = models.CharField(max_length=50, blank=True, null=True)
    loteproveedor = models.CharField(max_length=50, blank=True, null=True)
    ord_no = models.CharField(max_length=50, blank=True, null=True)
    fechavence = models.DateTimeField(blank=True, null=True)
    f_ultima_actualizacion = models.DateTimeField(blank=True, null=True)
    bodegaerp = models.CharField(db_column='BodegaERP', max_length=40, blank=True, null=True)  # Field name made lowercase.
    # id = models.AutoField()

    class Meta:
        managed = False
        db_table = 'TDA_WMS_EPN'
        unique_together = (('tipodocto', 'doctoerp', 'picking', 'numpedido'),)
