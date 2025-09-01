from django.db import models
from wmsAdapter.models import *


class TdaWmsEpk(models.Model):
    tipodocto = models.CharField(db_column='tipoDocto', max_length=20)  # Field name made lowercase.
    doctoerp = models.CharField(db_column='doctoERP', max_length=50)  # Field name made lowercase.
    picking = models.AutoField(primary_key=True)
    numpedido = models.CharField(db_column='numPedido', max_length=30, blank=True, null=True)  # Field name made lowercase.
    fechaplaneacion = models.DateTimeField(blank=True, null=True)
    f_pedido = models.DateTimeField(blank=True, null=True)
    item = models.CharField(max_length=50, blank=True, null=True)
    nombrecliente = models.CharField(max_length=200, blank=True, null=True)
    contacto = models.CharField(max_length=200, blank=True, null=True)
    email = models.CharField(max_length=200, blank=True, null=True)
    notas = models.CharField(max_length=500, blank=True, null=True)
    ciudad_despacho = models.CharField(db_column='ciudad despacho', max_length=150, blank=True, null=True)  # Field renamed to remove unsuitable characters.
    pais_despacho = models.CharField(db_column='pais Despacho', max_length=100, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    departamento_despacho = models.CharField(db_column='departamento Despacho', max_length=150, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    sucursal_despacho = models.CharField(db_column='sucursal Despacho', max_length=100, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    direccion_despacho = models.CharField(db_column='direccion Despacho', max_length=500, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    idsucursal = models.CharField(max_length=50, blank=True, null=True)
    ciudad = models.CharField(max_length=150, blank=True, null=True)
    pedidorelacionado = models.CharField(db_column='pedidoRelacionado', max_length=50, blank=True, null=True)  # Field name made lowercase.
    cargue = models.CharField(max_length=50, blank=True, null=True)
    nit = models.CharField(max_length=50, blank=True, null=True)
    estadopicking = models.IntegerField(db_column='estadoPicking', blank=True, null=True)  # Field name made lowercase.
    fecharegistro = models.DateTimeField(db_column='fechaRegistro', blank=True, null=True)  # Field name made lowercase.
    fpedido = models.DateTimeField(db_column='fPedido', blank=True, null=True)  # Field name made lowercase.
    fechtrans = models.DateTimeField(db_column='fechTrans', blank=True, null=True)  # Field name made lowercase.
    transportadora = models.CharField(max_length=100, blank=True, null=True)
    centrooperacion = models.CharField(db_column='centroOperacion', max_length=20, blank=True, null=True)  # Field name made lowercase.
    estadoerp = models.CharField(db_column='estadoERP', max_length=20, blank=True, null=True)  # Field name made lowercase.
    picking_batch = models.CharField(max_length=20, blank=True, null=True)
    field_condicionpago = models.CharField(db_column='_condicionpago', max_length=20, blank=True, null=True)  # Field renamed because it started with '_'.
    field_documentoreferencia = models.CharField(db_column='_documentoReferencia', max_length=50, blank=True, null=True)  # Field name made lowercase. Field renamed because it started with '_'.
    bodega = models.CharField(max_length=20, blank=True, null=True)
    vendedor2 = models.CharField(max_length=50, blank=True, null=True)
    numguia = models.CharField(max_length=50, blank=True, null=True)
    # id = models.AutoField()
    f_ultima_actualizacion = models.DateTimeField(blank=True, null=True)
    bodegaerp = models.CharField(db_column='BodegaERP', max_length=40, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'TDA_WMS_EPK'
        unique_together = (('tipodocto', 'doctoerp', 'numpedido', 'picking'),)
