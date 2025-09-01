from email.policy import default
from django.db import models

class TdaWmsArtCon(models.Model):
    productoean = models.CharField(max_length=100)
    id_product_shopify = models.CharField(max_length=100, blank=True, null=True)
    id_product_variant_shopify = models.CharField(max_length=100, blank=True, null=True)
    id_product_bigcommerce = models.CharField(max_length=100, blank=True, null=True)
    id_product_variant_bigcommerce = models.CharField(max_length=50, blank=True, null=True)
    id_product_quickbooks = models.CharField(max_length=50, blank=True, null=True)
    id = models.AutoField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'TDA_WMS_ART_CON'