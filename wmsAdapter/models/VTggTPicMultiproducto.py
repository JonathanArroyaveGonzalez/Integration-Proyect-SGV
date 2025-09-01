from django.db import models


class VTggTPicMultiproducto(models.Model):
    cajap = models.IntegerField() # Field name made lowercase.
    barcode = models.CharField(max_length=50, blank=True, null=True)
    referencia = models.CharField(max_length=50, blank=True, null=True)
    entradas = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True)
    salidas = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True)
    idempleado = models.IntegerField(blank=True, null=True)
    fecha = models.DateTimeField(blank=True, null=True)
    ubicacion_sale = models.CharField(max_length=20, blank=True, null=True)
    ean = models.CharField(max_length=50, blank=True, null=True)
    transaccion = models.CharField(max_length=50, blank=True, null=True)
    id = models.IntegerField(primary_key=True)
    saldo = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'V_TGG_T_pic_multiproducto'
