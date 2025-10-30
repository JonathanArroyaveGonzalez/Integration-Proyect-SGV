from django.db import models

class TdaWmsKit(models.Model):
    productoean_pack = models.CharField(db_column='productoEAN_pack', max_length=50)  # Field name made lowercase.
    descripcion_pack = models.TextField(db_column='Descripcion_pack', blank=True, null=True)  # Field name made lowercase.
    productoean_product = models.CharField(db_column='productoEAN_product', max_length=50)  # Field name made lowercase.
    descripcion_product = models.TextField(db_column='Descripcion_product', blank=True, null=True)  # Field name made lowercase.
    cantidad = models.DecimalField(db_column='Cantidad', max_digits=14, decimal_places=3)  # Field name made lowercase.
    bodega = models.CharField(max_length=20, blank=True, null=True)
    proveedor = models.CharField(max_length=50, blank=True, null=True)
    estado = models.IntegerField(blank=True, null=True)
    fecharegistro = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'TDA_WMS_KIT'
