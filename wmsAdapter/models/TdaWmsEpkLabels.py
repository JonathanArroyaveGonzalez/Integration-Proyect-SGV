from django.db import models


class TdaWmsEpkLabels(models.Model):
    picking = models.IntegerField(blank=True, null=True)
    guia = models.CharField(max_length=500, blank=True, null=True)
    pdf = models.TextField(blank=True, null=True)
    fecharegistro = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tda_wms_epk_labels'
