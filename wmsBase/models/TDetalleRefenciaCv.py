from django.db import models


class TDetalleRefenciaCv(models.Model):
    productoean = models.CharField(db_column='productoEAN', max_length=50)  # Field name made lowercase.
    codigoreferencia = models.CharField(max_length=50, blank=True, null=True)
    diasvigenciaproveedor = models.IntegerField(blank=True, null=True)
    diasvigenciacedi = models.IntegerField(blank=True, null=True)
    cantidadempaque = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True)
    peso = models.DecimalField(max_digits=14, decimal_places=3, blank=True, null=True)
    volumen = models.DecimalField(max_digits=14, decimal_places=3, blank=True, null=True)
    fechamodificacion = models.DateTimeField(db_column='fechaModificacion', blank=True, null=True)  # Field name made lowercase.
    stockmin = models.DecimalField(db_column='stockMin', max_digits=14, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    stockmax = models.DecimalField(db_column='stockMax', max_digits=14, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    bodega = models.CharField(max_length=20)
    codgrupoprm = models.CharField(db_column='codGrupoPrm', max_length=10, blank=True, null=True)  # Field name made lowercase.
    controla_status_calidad = models.IntegerField(db_column='controla_status_Calidad', blank=True, null=True)  # Field name made lowercase.
    factor_estibado = models.IntegerField(blank=True, null=True)
    controlafechavencimiento = models.IntegerField(db_column='controlaFechaVencimiento', blank=True, null=True)  # Field name made lowercase.
    listavigencias = models.IntegerField(primary_key=True)
    dim_x = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True)
    dim_y = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True)
    dim_z = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True)
    imageurl = models.CharField(max_length=350, blank=True, null=True)
    doble_unidad_de_medida = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 't_detalle_refencia_CV'
        unique_together = (('listavigencias', 'productoean', 'bodega'),)
