# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class TdaWmsRfidRead(models.Model):
    id = models.IntegerField(primary_key=True)
    fecha_registro = models.DateTimeField()
    rfid_tag = models.CharField(max_length=50)
    id_empleado = models.IntegerField()
    tipo_docto = models.CharField(max_length=20)
    num_docto = models.CharField(max_length=10)
    cod_bod = models.CharField(max_length=20, blank=True, null=True)
    estado_lectura = models.IntegerField(blank=True, null=True)
    fecha_transmision = models.DateTimeField(blank=True, null=True)
    box_reference = models.IntegerField(blank=True, null=True)
    ubic_reference = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tda_wms_rfid_read'
        unique_together = (('rfid_tag', 'tipo_docto', 'num_docto', 'cod_bod'),)
