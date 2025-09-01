from django.db import models


class TdaWmsArtExt(models.Model):
    productoean = models.CharField(unique=True, max_length=20, blank=True, null=True)
    manejalote = models.BooleanField(blank=True, null=True)
    lote = models.CharField(max_length=50, blank=True, null=True)
    id = models.AutoField(db_column='id', auto_created=True, primary_key=True) 
    
    class Meta:
        managed = False
        db_table = 'tda_wms_art_ext'