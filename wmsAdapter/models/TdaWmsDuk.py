from django.db import models
from wmsAdapter.models import *

class TdaWmsDuk(models.Model):
    referencia = models.CharField(max_length=50, blank=True, null=True)
    refpadre = models.CharField(db_column='refPadre', max_length=50, blank=True, null=True)  # Field name made lowercase.
    descripcion = models.CharField(max_length=180, blank=True, null=True)
    qtypedido = models.DecimalField(db_column='qtyPedido', max_digits=14, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    qtyreservado = models.DecimalField(db_column='qtyReservado', max_digits=14, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    # productoean = models.ForeignKey(TdaWmsArt, models.DO_NOTHING, db_column='productoEAN')  # Field name made lowercase.
    productoean = models.CharField(db_column='productoEAN',max_length=50 )  # Field name made lowercase.
    lineaidpicking = models.IntegerField(db_column='lineaIdPicking')  # Field name made lowercase.
    costo = models.DecimalField(max_digits=14, decimal_places=4, blank=True, null=True)
    bodega = models.CharField(max_length=20)
    tipodocto = models.CharField(db_column='tipoDocto', max_length=20)  # Field name made lowercase.
    doctoerp = models.CharField(db_column='doctoERP', max_length=30)  # Field name made lowercase.
    qtyenpicking = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True)
    estadodetransferencia = models.IntegerField(blank=True, null=True)
    fecharegistro = models.DateTimeField(db_column='fechaRegistro', blank=True, null=True)  # Field name made lowercase.
    ubicacion = models.CharField(max_length=20, blank=True, null=True)
    numdocumento = models.CharField(max_length=50)
    item = models.CharField(max_length=50, blank=True, null=True)
    ubicacion_sale = models.CharField(db_column='ubicacion_Sale', max_length=20, blank=True, null=True)  # Field name made lowercase.
    origen = models.CharField(max_length=20, blank=True, null=True)
    caja_destino = models.FloatField(blank=True, null=True)
    fechaestadoalmdirigido = models.DateTimeField(blank=True, null=True)
    unido = models.CharField(db_column='UNIDO', max_length=50, blank=True, null=True)  # Field name made lowercase.
    etd = models.DateTimeField(blank=True, null=True)
    eta = models.DateTimeField(blank=True, null=True)
    pedproveedor = models.CharField(max_length=50, blank=True, null=True)
    ord_no = models.CharField(max_length=50, blank=True, null=True)
    loteproveedor = models.CharField(max_length=20, blank=True, null=True)
    codigoarticulo = models.CharField(db_column='codigoArticulo', max_length=50, blank=True, null=True)  # Field name made lowercase.
    cantidadempaque = models.IntegerField(blank=True, null=True)
    f_ultima_actualizacion = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'TDA_WMS_DUK'