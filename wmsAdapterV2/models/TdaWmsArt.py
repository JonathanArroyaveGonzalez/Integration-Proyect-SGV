from email.policy import default
from django.db import models
import json

class TdaWmsArt(models.Model):
    productoean = models.CharField(db_column='productoEAN', max_length=50)  # Field name made lowercase.
    descripcion = models.CharField(max_length=250, blank=True, null=True)
    referencia = models.CharField(max_length=50)
    inventariable = models.IntegerField(blank=True, null=True)
    um1 = models.CharField(max_length=10, blank=True, null=True)
    presentacion = models.CharField(max_length=100, blank=True, null=True)
    costo = models.DecimalField(max_digits=16, decimal_places=4, blank=True, null=True)
    referenciamdc = models.CharField(db_column='referenciaMDC', max_length=50, blank=True, null=True)  # Field name made lowercase.
    descripcioningles = models.CharField(db_column='descripcionIngles', max_length=250, blank=True, null=True)  # Field name made lowercase.
    item = models.CharField(max_length=50, blank=True, null=True)
    u_inv = models.CharField(db_column='u_Inv', max_length=25, blank=True, null=True)  # Field name made lowercase.
    grupo = models.CharField(max_length=100, blank=True, null=True)
    subgrupo = models.CharField(max_length=100, blank=True, null=True)
    extension1 = models.CharField(max_length=50, blank=True, null=True)
    extension2 = models.CharField(max_length=50, blank=True, null=True)
    nuevoean = models.CharField(db_column='nuevoEAN', max_length=100)  # Field name made lowercase.
    qtyequivalente = models.DecimalField(db_column='qtyEquivalente', max_digits=14, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    origencompra = models.CharField(db_column='origenCompra', max_length=4, blank=True, null=True)  # Field name made lowercase.
    tipo = models.CharField(max_length=30, blank=True, null=True)
    factor = models.DecimalField(max_digits=14, decimal_places=3, blank=True, null=True)
    f120_tipo_item = models.CharField(max_length=10, blank=True, null=True)
    fecharegistro = models.DateTimeField(db_column='fechaRegistro', blank=True, null=True)  # Field name made lowercase.
    peso = models.DecimalField(max_digits=14, decimal_places=3, blank=True, null=True)
    bodega = models.CharField(max_length=20, blank=True, null=True)
    procedencia = models.CharField(max_length=20, blank=True, null=True)
    estadotransferencia = models.IntegerField(blank=True, null=True)
    volumen = models.DecimalField(max_digits=14, decimal_places=3, blank=True, null=True)
    proveedor = models.CharField(max_length=50, blank=True, null=True)
    preciounitario = models.DecimalField(max_digits=16, decimal_places=4, blank=True, null=True)
    ingredientes = models.CharField(db_column='Ingredientes', max_length=2000, blank=True, null=True)  # Field name made lowercase.
    instrucciones_de_uso = models.CharField(db_column='Instrucciones de uso', max_length=300, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    u_inv_p = models.CharField(db_column='u_Inv_p', max_length=10, blank=True, null=True)  # Field name made lowercase.
    observacion = models.CharField(max_length=250, blank=True, null=True)
    controla_status_calidad = models.IntegerField(blank=True, null=True)
    estado = models.IntegerField(blank=True, null=True)
    alergenos = models.CharField(max_length=1200, blank=True, null=True)
    id = models.AutoField(db_column='id', auto_created=True, primary_key=True) 
        
    class Meta:
        managed = False
        db_table = 'TDA_WMS_ART'
        unique_together = (('productoean', 'referencia', 'nuevoean'),)