from django.db import models


class TdaWmsRelacionSeriales(models.Model):
    documento = models.CharField(primary_key=True, max_length=50)
    cajamp = models.CharField(db_column='CajaMP', max_length=50, blank=True, null=True)  # Field name made lowercase.
    productoean = models.CharField(db_column='ProductoEAN', max_length=50)  # Field name made lowercase.
    barcode = models.CharField(db_column='Barcode', max_length=50, blank=True, null=True)  # Field name made lowercase.
    numserial = models.CharField(db_column='NumSerial', max_length=50)  # Field name made lowercase.
    empleadopalletiza = models.CharField(db_column='EmpleadoPalletiza', max_length=100, blank=True, null=True)  # Field name made lowercase.
    fecharegistro = models.DateTimeField(db_column='FechaRegistro', blank=True, null=True)  # Field name made lowercase.
    estadotransferencia = models.IntegerField(db_column='EstadoTransferencia', blank=True, null=True)  # Field name made lowercase.
    fechatransferencia = models.DateTimeField(db_column='FechaTransferencia', blank=True, null=True)  # Field name made lowercase.
    ubicacion = models.CharField(db_column='UBICACION', max_length=50, blank=True, null=True)  # Field name made lowercase.
    estado = models.CharField(db_column='ESTADO', max_length=50, blank=True, null=True)  # Field name made lowercase.
    numchasis = models.CharField(max_length=50, blank=True, null=True)
    caja = models.IntegerField(blank=True, null=True)
    pedproveedor = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'TDA_WMS_RELACION_SERIALES'
        unique_together = (('documento', 'productoean', 'numserial'),)