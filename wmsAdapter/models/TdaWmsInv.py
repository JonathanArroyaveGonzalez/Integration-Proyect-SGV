from email.policy import default
from django.db import models

class TdaWmsInv(models.Model):
    bod = models.CharField(max_length=40)
    ubicacion = models.CharField(max_length=60)
    productoean = models.CharField(db_column='productoEAN', max_length=50)  # Field name made lowercase.
    saldopt = models.DecimalField(db_column='saldoPT', max_digits=14, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    descripcion = models.CharField(max_length=400)
    fecharegistro = models.DateTimeField(db_column='fechaRegistro', blank=True, null=True)  # Field name made lowercase.
    codigoalmacen = models.CharField(db_column='codigoAlmacen', max_length=20, blank=True, null=True)  # Field name made lowercase.
    cantbloqueadoerp = models.DecimalField(db_column='cantBloqueadoERP', max_digits=14, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    estadodetransferencia = models.IntegerField(blank=True, null=True)
    referencia = models.CharField(max_length=50)
    valor = models.IntegerField(blank=True, null=True)
    tipo_inventario = models.CharField(max_length=50, blank=True, null=True)
    saldowms = models.DecimalField(db_column='saldoWMS', max_digits=16, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    etl = models.CharField(max_length=10, blank=True, null=True)
    fecha_ultima_actualizacion = models.DateTimeField(blank=True, null=True)
    fecha_prox_actualizacion = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'TDA_WMS_INV'
        unique_together = (('bod', 'ubicacion', 'productoean'),)