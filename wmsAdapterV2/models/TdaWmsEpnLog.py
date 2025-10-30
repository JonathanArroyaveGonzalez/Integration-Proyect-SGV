# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class TdaWmsEpnLog(models.Model):
    tipodocto = models.CharField(max_length=50)
    doctoerp = models.CharField(db_column='doctoERP', max_length=20)  # Field name made lowercase.
    picking = models.CharField(max_length=20)
    numpedido = models.CharField(max_length=50)
    fecharegistro = models.DateTimeField(blank=True, null=True)
    bodega = models.CharField(max_length=20)
    productoean = models.CharField(db_column='productoEAN', max_length=50)  # Field name made lowercase.
    referencia = models.CharField(max_length=50, blank=True, null=True)
    pedproveedor = models.CharField(max_length=50, blank=True, null=True)
    loteproveedor = models.CharField(max_length=50, blank=True, null=True)
    ord_no = models.CharField(max_length=50, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'TDA_WMS_EPN_LOG'
