from django.db import models


class TdaWmsCecoMrm(models.Model):
    centrocostos = models.CharField(max_length=20, blank=True, null=True)
    bod_alma_origen = models.CharField(max_length=20, blank=True, null=True)
    ubicacion = models.CharField(max_length=20, blank=True, null=True)
    productoean = models.CharField(max_length=50, blank=True, null=True)
    cantidad_egreso = models.DecimalField(max_digits=18, decimal_places=3, blank=True, null=True)
    fecha_documento = models.DateTimeField(blank=True, null=True)
    fecha_contabilizacion = models.DateTimeField(blank=True, null=True)
    motivomerma = models.CharField(max_length=250, blank=True, null=True)
    idempleado = models.IntegerField(blank=True, null=True)
    estadotransferencia = models.IntegerField(blank=True, null=True)
    pedproveedor = models.CharField(max_length=20, blank=True, null=True)
    loteproveedor = models.IntegerField(blank=True, null=True)
    id = models.AutoField(primary_key=True)
    cajap = models.IntegerField(blank=True, null=True)
    transaccion = models.CharField(max_length=20, blank=True, null=True)
    usuario = models.CharField(max_length=200, blank=True, null=True)
    item = models.CharField(max_length=50, blank=True, null=True)


    class Meta:
        managed = False
        db_table = 'TDA_WMS_CECO_MRM'