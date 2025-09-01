# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class VTInvPic(models.Model):
    bodepicking = models.CharField(max_length=20, blank=True, null=True)
    cod_producto = models.CharField(max_length=50, blank=True, null=True)
    barcode = models.CharField(max_length=50, blank=True, null=True)
    ref = models.CharField(max_length=50, blank=True, null=True)
    cajap = models.IntegerField(blank=True, null=True)
    tipo = models.CharField(max_length=20, blank=True, null=True)
    lote = models.CharField(max_length=20, blank=True, null=True)
    entradas = models.DecimalField(max_digits=16, decimal_places=4, blank=True, null=True)
    salidas = models.DecimalField(max_digits=16, decimal_places=4, blank=True, null=True)
    ubicacion = models.CharField(max_length=20, blank=True, null=True)
    ubicacion_pod = models.CharField(max_length=20, blank=True, null=True)
    saldo = models.DecimalField(max_digits=17, decimal_places=4, blank=True, null=True)
    nro = models.IntegerField(db_column='Nro', blank=True, null=True)  # Field name made lowercase.
    cod_producto_pic = models.CharField(max_length=50, blank=True, null=True)
    zonapiso = models.CharField(max_length=10, blank=True, null=True)
    origen = models.CharField(max_length=30, blank=True, null=True)
    prioridadrotacion = models.IntegerField(blank=True, null=True)
    vigencia = models.IntegerField(blank=True, null=True)
    descripcion = models.CharField(max_length=250, blank=True, null=True)
    um1 = models.CharField(max_length=10, blank=True, null=True)
    pedproveedor = models.CharField(db_column='PedProveedor', max_length=50, blank=True, null=True)  # Field name made lowercase.
    numcontrolliberacion = models.CharField(db_column='NumControlLiberacion', max_length=20, blank=True, null=True)  # Field name made lowercase.
    fecha = models.DateTimeField()

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'V_T_INV_PIC'
