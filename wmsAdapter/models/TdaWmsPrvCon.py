from django.db import models


class TdaWmsPrvCon(models.Model):
    item = models.CharField(max_length=50)
    id_quickbooks = models.CharField(max_length=50, blank=True, null=True)
    # id = models.AutoField()

    class Meta:
        managed = False
        db_table = 'tda_wms_prv_con'
