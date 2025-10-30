from django.db import models

class TRelacionCodbarras(models.Model):
    # id = models.AutoField(db_column='id',auto_created=True, primary_key=True)  # Field name made lowercase.
    idinternoean = models.CharField(db_column='IdInternoEAN', max_length=50)  # Field name made lowercase.
    codbarrasasignado = models.CharField(db_column='CodBarrasAsignado', max_length=50, primary_key=True)  # Field name made lowercase.
    cantidad = models.FloatField(db_column='Cantidad', blank=True, null=True)  # Field name made lowercase.
    qtynew = models.DecimalField(db_column='qtyNew', max_digits=14, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    fechacrea = models.DateTimeField(blank=True, null=True)
    pesobruto = models.DecimalField(max_digits=14, decimal_places=5, blank=True, null=True)
    qtytara = models.DecimalField(max_digits=14, decimal_places=5, blank=True, null=True)
    cantidad_tara = models.DecimalField(db_column='Cantidad_tara', max_digits=16, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    # qtypesounitario = models.DecimalField(max_digits=34, decimal_places=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 't_relacion_codbarras'
        unique_together = (('idinternoean', 'codbarrasasignado'),)
