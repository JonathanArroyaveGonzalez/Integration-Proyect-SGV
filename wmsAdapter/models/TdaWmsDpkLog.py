
from django.db import models

class TdaWmsDpkLog(models.Model):
    # id = models.IntegerField(primary_key=True)
    tipodocto = models.CharField(db_column='tipoDocto', max_length=100, blank=True, null=True)  # Field name made lowercase.
    doctoerp = models.CharField(db_column='doctoERP', max_length=100, blank=True, null=True)  # Field name made lowercase.
    numpedido = models.CharField(max_length=100, blank=True, null=True)
    fecharegistro = models.DateTimeField(db_column='fechaRegistro', blank=True, null=True)  # Field name made lowercase.
    referencia = models.CharField(db_column='Referencia', max_length=255, blank=True, null=True)  # Field name made lowercase.
    refpadre = models.CharField(db_column='RefPadre', max_length=255, blank=True, null=True)  # Field name made lowercase.
    descripcion = models.CharField(db_column='Descripcion', max_length=255, blank=True, null=True)  # Field name made lowercase.
    picking = models.IntegerField(blank=True, null=True)
    lineaidpicking = models.IntegerField(db_column='lineaIdPicking', blank=True, null=True)  # Field name made lowercase.
    bodega = models.CharField(db_column='Bodega', max_length=100, blank=True, null=True)  # Field name made lowercase.
    qtyenpicking = models.FloatField(db_column='qtyenPicking', blank=True, null=True)  # Field name made lowercase.
    pedproveedor = models.CharField(max_length=100, blank=True, null=True)
    loteproveedor = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tda_wms_dpk_log'
