from django.db import models


class TdaWmsDpnLog(models.Model):
    tipodocto = models.CharField(max_length=50, blank=True, null=True)
    doctoerp = models.CharField(db_column='doctoERP', max_length=20, blank=True, null=True)  # Field name made lowercase.
    numpedido = models.CharField(max_length=50)
    picking = models.CharField(max_length=20)
    lineaidop = models.IntegerField()
    productoean = models.CharField(db_column='productoEAN', max_length=50)  # Field name made lowercase.
    qtypedido = models.DecimalField(max_digits=16, decimal_places=4, blank=True, null=True)
    bodega = models.CharField(max_length=20)
    fecharegistro = models.DateTimeField(blank=True, null=True)
    qtypicking = models.DecimalField(max_digits=16, decimal_places=4, blank=True, null=True)
    loteproveedor = models.IntegerField(blank=True, null=True)
    pedproveedor = models.CharField(max_length=50, blank=True, null=True)
    id = models.AutoField(primary_key=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tda_wms_dpn_log'