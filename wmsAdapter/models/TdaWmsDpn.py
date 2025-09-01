from django.db import models
from wmsAdapter.models import *

class TdaWmsDpn(models.Model):
    numpedido = models.CharField(max_length=50)
    # productoean = models.ForeignKey(TdaWmsArt, models.DO_NOTHING, db_column='productoEAN')  # Field name made lowercase.
    productoean = models.CharField(db_column='productoEAN', max_length=50)  # Field name made lowercase.
    # picking = models.ForeignKey('TdaWmsEpn', models.DO_NOTHING, db_column='picking')
    picking = models.CharField(db_column='picking', max_length=50)
    # lineaidop = models.IntegerField(db_column='lineaidop')
    #lineaidop = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=200, blank=True, null=True)
    ref = models.CharField(max_length=50, blank=True, null=True)
    qtypedido = models.DecimalField(max_digits=16, decimal_places=4, blank=True, null=True)
    qtyreservado = models.DecimalField(max_digits=16, decimal_places=4, blank=True, null=True)
    bodega = models.CharField(max_length=20)
    ubicacion_plan = models.CharField(max_length=20, blank=True, null=True)
    fecharegistro = models.DateTimeField(blank=True, null=True)
    estadotransferencia = models.IntegerField(blank=True, null=True)
    fechatransferencia = models.DateTimeField(blank=True, null=True)
    qtypicking = models.DecimalField(max_digits=16, decimal_places=4, blank=True, null=True)
    tipodocto = models.CharField(max_length=50, blank=True, null=True)
    doctoerp = models.CharField(db_column='doctoERP', max_length=20, blank=True, null=True)  # Field name made lowercase.
    loteproveedor = models.IntegerField(blank=True, null=True)
    pedproveedor = models.CharField(max_length=50, blank=True, null=True)
    f_ultima_actualizacion = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'TDA_WMS_DPN'
        unique_together = (('numpedido', 'productoean', 'picking', 'loteproveedor'),)