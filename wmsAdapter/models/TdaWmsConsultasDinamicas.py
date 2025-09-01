from django.db import models


class TdaWmsConsultasDinamicas(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    codigo = models.CharField(max_length=255, blank=False, null=False, unique=True)
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    query = models.TextField(blank=True, null=True)  # This field type is a guess.
    fecharegistro = models.DateTimeField(db_column='fechaRegistro', blank=True, null=True)  # Field name made lowercase.
    conexion = models.CharField(max_length=1000, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'TDA_WMS_CONSULTAS_DINAMICAS'
