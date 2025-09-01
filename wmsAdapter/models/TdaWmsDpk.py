from django.db import models
from wmsAdapter.models.TdaWmsEpk import TdaWmsEpk
from wmsAdapter.models.TdaWmsArt import TdaWmsArt

class TdaWmsDpk(models.Model):
    referencia = models.CharField(db_column='Referencia', max_length=50, blank=True, null=True)  # Field name made lowercase.
    refpadre = models.CharField(db_column='RefPadre', max_length=50, blank=True, null=True)  # Field name made lowercase.
    descripcion = models.CharField(db_column='Descripcion', max_length=180, blank=True, null=True)  # Field name made lowercase.
    qtypedido = models.DecimalField(db_column='qtyPedido', max_digits=16, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    qtyreservado = models.DecimalField(db_column='qtyReservado', max_digits=16, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    # productoean = models.ForeignKey(TdaWmsArt, models.DO_NOTHING, db_column='productoEAN')  # Field name made lowercase.
    # picking = models.ForeignKey(TdaWmsEpk, models.DO_NOTHING, db_column='picking')
    productoean = models.CharField(db_column='productoEAN',max_length=50 )  # Field name made lowercase.
    picking = models.CharField(db_column='picking', max_length=20)  # Field name made lowercase.
    lineaidpicking = models.IntegerField(db_column='LineaIdPicking')  # Field name made lowercase.
    #lineaidpicking = models.AutoField(primary_key=True)
    costo = models.DecimalField(db_column='Costo', max_digits=14, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    bodega = models.CharField(db_column='Bodega', max_length=50, blank=True, null=True)  # Field name made lowercase.
    tipodocto = models.CharField(db_column='tipoDocto', max_length=20, blank=True, null=True)  # Field name made lowercase.
    doctoerp = models.CharField(db_column='doctoERP', max_length=50)  # Field name made lowercase.
    qtyenpicking = models.DecimalField(max_digits=16, decimal_places=4, blank=True, null=True)
    estadodetransferencia = models.IntegerField(blank=True, null=True)
    fecharegistro = models.DateTimeField(db_column='fechaRegistro', blank=True, null=True)  # Field name made lowercase.
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    ubicacion_plan = models.CharField(max_length=20, blank=True, null=True)
    fechatransferencia = models.DateTimeField(blank=True, null=True)
    clasifart = models.CharField(max_length=20, blank=True, null=True)
    serial = models.CharField(max_length=50, blank=True, null=True)
    item = models.CharField(max_length=50, blank=True, null=True)
    idco = models.CharField(db_column='idCo', max_length=20, blank=True, null=True)  # Field name made lowercase.
    qtyremisionado = models.DecimalField(db_column='qtyRemisionado', max_digits=14, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    qtyfacturado = models.DecimalField(db_column='qtyFacturado', max_digits=14, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    preciounitario = models.DecimalField(db_column='precioUnitario', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    notasitem = models.CharField(max_length=500, blank=True, null=True)
    descripcionco = models.CharField(db_column='descripcionCo', max_length=80, blank=True, null=True)  # Field name made lowercase.
    factor = models.IntegerField(blank=True, null=True)
    numpedido = models.CharField(max_length=30, blank=True, null=True)
    pedproveedor = models.CharField(max_length=50, blank=True, null=True)
    loteproveedor = models.CharField(max_length=20, blank=True, null=True)
    field_qtypedidabase = models.DecimalField(db_column='_qtypedidabase', max_digits=14, decimal_places=2, blank=True, null=True)  # Field renamed because it started with '_'.
    # lineaidpickingint = models.IntegerField(db_column='lineaIdPickingInt', blank=True, null=True)  # Field name made lowercase.
    # lineaidpickingint = models.AutoField(primary_key=True, default=0)
    f_ultima_actualizacion = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'TDA_WMS_DPK'
        unique_together = (('lineaidpicking', 'picking', 'picking', 'productoean', 'loteproveedor', 'estadodetransferencia'),)
