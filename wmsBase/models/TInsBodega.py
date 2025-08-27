# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class TInsBodega(models.Model):
    bodega = models.CharField(db_column='Bodega', primary_key=True, max_length=15)  # Field name made lowercase.
    descripcion = models.CharField(db_column='Descripcion', max_length=50, blank=True, null=True)  # Field name made lowercase.
    ubicacionf_c = models.CharField(db_column='UbicacionF_C', max_length=50, blank=True, null=True)  # Field name made lowercase.
    tipu = models.IntegerField(db_column='Tipu', blank=True, null=True)  # Field name made lowercase.
    prcierre = models.BooleanField()
    codcc = models.CharField(db_column='codCC', max_length=6, blank=True, null=True)  # Field name made lowercase.
    regional = models.CharField(db_column='Regional', max_length=2, blank=True, null=True)  # Field name made lowercase.
    imgmapa = models.BinaryField(db_column='ImgMapa', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 't_ins_bodega'
