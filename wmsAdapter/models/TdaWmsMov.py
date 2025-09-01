# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class TdaWmsMov(models.Model):
    id = models.IntegerField(primary_key=True)
    caja = models.IntegerField()
    ubicacion_inicial = models.CharField(max_length=30)
    ubicacion_final = models.CharField(max_length=30)
    idempleado = models.IntegerField(blank=True, null=True)
    fecha = models.DateTimeField(blank=True, null=True)
    estadodetransferencia = models.IntegerField(blank=True, null=True)
    fechatransferencia = models.DateTimeField(blank=True, null=True)
    saldo = models.DecimalField(max_digits=16, decimal_places=4, blank=True, null=True)
    productoean = models.CharField(max_length=50, blank=True, null=True)
    loteproveedor = models.CharField(max_length=30, blank=True, null=True)
    bodega_inicial = models.CharField(max_length=30, blank=True, null=True)
    bodega_final = models.CharField(max_length=30, blank=True, null=True)
    transaccion = models.CharField(max_length=50, blank=True, null=True)
    pallet = models.IntegerField(blank=True, null=True)
    documentooc = models.CharField(max_length=50, blank=True, null=True)
    tipodocto = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tda_wms_mov'
