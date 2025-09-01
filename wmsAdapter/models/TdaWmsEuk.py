from django.db import models
from wmsAdapter.models import *

class TdaWmsEuk(models.Model):
    tipodocto = models.CharField(db_column='tipoDocto', max_length=20)  # Field name made lowercase.
    doctoerp = models.CharField(db_column='doctoERP', max_length=30)  # Field name made lowercase.
    numdocumento = models.CharField(db_column='numdocumento', max_length=50)
    fecha = models.DateTimeField(blank=True, null=True)
    # item = models.ForeignKey('TdaWmsPrv', models.DO_NOTHING, db_column='item', blank=True, null=True)
    item = models.CharField(db_column='item', max_length=50, blank=True, null=True)
    nombreproveedor = models.CharField(db_column='nombreProveedor', max_length=200, blank=True, null=True)  # Field name made lowercase.
    contacto = models.CharField(max_length=200, blank=True, null=True)
    email = models.CharField(max_length=500, blank=True, null=True)
    nit = models.CharField(max_length=30, blank=True, null=True)
    estadodocumentoubicacion = models.IntegerField(blank=True, null=True)
    fecharegistro = models.DateTimeField(db_column='fechaRegistro', blank=True, null=True)  # Field name made lowercase.
    bl = models.CharField(max_length=50, blank=True, null=True)
    contenedor = models.CharField(max_length=50, blank=True, null=True)
    embarque = models.CharField(max_length=50, blank=True, null=True)
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    unido = models.CharField(db_column='UNIDO', max_length=50, blank=True, null=True)  # Field name made lowercase.
    etd = models.DateTimeField(blank=True, null=True)
    eta = models.DateTimeField(blank=True, null=True)
    codigoarticulo = models.CharField(db_column='codigoArticulo', max_length=50, blank=True, null=True)  # Field name made lowercase.
    f_ultima_actualizacion = models.DateTimeField(blank=True, null=True)
    bodega = models.CharField(max_length=30, blank=True, null=True)
    bodegaerp = models.CharField(db_column='BodegaERP', max_length=40, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'TDA_WMS_EUK'
        unique_together = (('tipodocto', 'doctoerp', 'numdocumento'),)
