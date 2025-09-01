# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class VTDetallePrepack(models.Model):
    pedproveedor = models.CharField(db_column='PedProveedor', max_length=50, blank=True, null=True)  # Field name made lowercase.
    iddetpripack = models.IntegerField(db_column='IddetPripack')  # Field name made lowercase.
    numpicking = models.IntegerField(db_column='NumPicking', blank=True, null=True)  # Field name made lowercase.
    conscaja = models.CharField(db_column='ConsCaja', max_length=50, blank=True, null=True)  # Field name made lowercase.
    product = models.CharField(max_length=50, blank=True, null=True)
    cant = models.DecimalField(db_column='Cant', max_digits=16, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    fecha = models.DateTimeField(blank=True, null=True)
    lothe = models.CharField(max_length=50, blank=True, null=True)
    origen = models.CharField(max_length=150, blank=True, null=True)
    precioventa = models.FloatField(db_column='precioVenta', blank=True, null=True)  # Field name made lowercase.
    bonificacion = models.FloatField(blank=True, null=True)
    diponepick = models.DecimalField(db_column='diponePick', max_digits=16, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    saldoaduana = models.DecimalField(db_column='saldoAduana', max_digits=16, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    bode = models.CharField(max_length=20, blank=True, null=True)
    cmv = models.FloatField(blank=True, null=True)
    pedido = models.CharField(max_length=50, blank=True, null=True)
    listapre = models.IntegerField(blank=True, null=True)
    descuento = models.FloatField(blank=True, null=True)
    estadolinea = models.IntegerField(blank=True, null=True)
    cospromedio = models.FloatField(blank=True, null=True)
    alerta = models.CharField(max_length=50, blank=True, null=True)
    descripcion = models.CharField(max_length=250, blank=True, null=True)
    ref = models.CharField(max_length=50, blank=True, null=True)
    transaccion = models.CharField(max_length=50, blank=True, null=True)
    zonapiso = models.CharField(max_length=20, blank=True, null=True)
    ubicacion_asig = models.CharField(max_length=20, blank=True, null=True)
    cargue = models.CharField(max_length=50, blank=True, null=True)
    barcode = models.CharField(max_length=50, blank=True, null=True)
    bl = models.CharField(db_column='BL', max_length=50, blank=True, null=True)  # Field name made lowercase.
    tipodocto = models.CharField(db_column='TipoDocto', max_length=20, blank=True, null=True)  # Field name made lowercase.
    documentoerp = models.CharField(db_column='DocumentoERP', max_length=50, blank=True, null=True)  # Field name made lowercase.
    numpedido = models.CharField(db_column='NumPedido', max_length=50, blank=True, null=True)  # Field name made lowercase.
    referencia = models.CharField(max_length=50, blank=True, null=True)
    loteop = models.CharField(db_column='loteOp', max_length=50, blank=True, null=True)  # Field name made lowercase.
    op = models.CharField(db_column='Op', max_length=71, blank=True, null=True)  # Field name made lowercase.
    um1 = models.CharField(max_length=10, blank=True, null=True)
    referencia_material = models.CharField(max_length=50, blank=True, null=True)
    nombre_referencia = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'V_T_DETALLE_PREPACK'
