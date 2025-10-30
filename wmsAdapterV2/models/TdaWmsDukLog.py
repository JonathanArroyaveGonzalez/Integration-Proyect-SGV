# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class TdaWmsDukLog(models.Model):
    tipodocto = models.CharField(db_column='tipoDocto', max_length=100, blank=True, null=True)  # Field name made lowercase.
    doctoerp = models.CharField(db_column='doctoERP', max_length=100, blank=True, null=True)  # Field name made lowercase.
    numdocumento = models.CharField(max_length=100, blank=True, null=True)
    fecharegistro = models.DateTimeField(db_column='fechaRegistro', blank=True, null=True)  # Field name made lowercase.
    referencia = models.CharField(db_column='Referencia', max_length=255, blank=True, null=True)  # Field name made lowercase.
    refpadre = models.CharField(db_column='RefPadre', max_length=255, blank=True, null=True)  # Field name made lowercase.
    descripcion = models.CharField(db_column='Descripcion', max_length=255, blank=True, null=True)  # Field name made lowercase.
    lineaidpicking = models.IntegerField(db_column='lineaIdPicking', blank=True, null=True)  # Field name made lowercase.
    bodega = models.CharField(db_column='Bodega', max_length=100, blank=True, null=True)  # Field name made lowercase.
    qtyenpicking = models.FloatField(db_column='qtyenPicking', blank=True, null=True)  # Field name made lowercase.
    pedproveedor = models.CharField(max_length=100, blank=True, null=True)
    loteproveedor = models.CharField(max_length=100, blank=True, null=True)
    ord_no = models.CharField(max_length=100, blank=True, null=True)
    id_duk = models.IntegerField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    id = models.AutoField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'tda_wms_duk_log'
