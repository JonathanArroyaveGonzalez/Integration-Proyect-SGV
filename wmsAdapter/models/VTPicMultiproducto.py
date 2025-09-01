# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class VTPicMultiproducto(models.Model):
    cajap = models.FloatField()
    ubicacion = models.CharField(max_length=50, blank=True, null=True)
    barcode = models.CharField(max_length=50)
    referencia = models.CharField(max_length=50, blank=True, null=True)
    entradas = models.DecimalField(max_digits=16, decimal_places=4, blank=True, null=True)
    salidas = models.DecimalField(max_digits=16, decimal_places=4, blank=True, null=True)
    fechaultimomvto = models.DateTimeField(blank=True, null=True)
    idempleado = models.IntegerField(blank=True, null=True)
    transaccion = models.CharField(max_length=50, blank=True, null=True)
    saldo = models.DecimalField(max_digits=17, decimal_places=4, blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'V_T_pic_multiproducto'
