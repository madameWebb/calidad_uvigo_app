from django.conf import settings
from django.db import models
from simple_history.models import HistoricalRecords


# Create your models here.
class IRPD(models.Model):
    # Códigos fijos del 1 al 7
    criterio = models.CharField(max_length=20, unique=True)
    denominacion = models.CharField(max_length=255)

    # Guarda la fecha y hora EXACTA cuando se crea el registro por primera vez
    creacion = models.DateTimeField(auto_now_add=True)

    # Guarda la fecha y hora EXACTA cada vez que se edite o modifique el registro
    actualizacion = models.DateTimeField(auto_now=True)

    # Usuario que creó el registro (obligatorio)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='irpd_creados'
    )

    # Usuario que modificó el registro por última vez (solo cuando se edite)
    modificado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='irpd_modificados',
        null=True,
        blank=True
    )

    history = HistoricalRecords()

    def __str__(self):
        return self.denominacion
    class Meta:
        verbose_name = "IRPD"
        verbose_name_plural = "IRPDs"


class Indicadores(models.Model):
    # Un campo de texto para el código (máximo 100 caracteres)
    codigo = models.CharField(max_length=100)
    denominacion_indicador = models.CharField(max_length=255)
    denominacion = models.CharField(max_length=500, blank=True, null=True)

    # Un campo de texto más largo para la descripción
    descripcion = models.TextField(blank=True, null=True)

    # Enlace web
    fuente = models.URLField(max_length=500, blank=True, null=True)

    # Relación con IRPD (obligatoria: cada indicador debe llevar un IRPD)
    irpd = models.ForeignKey(
        IRPD,
        on_delete=models.PROTECT,
        related_name='indicadores'
    )

    # Guarda la fecha y hora EXACTA cuando se crea el registro por primera vez
    creacion = models.DateTimeField(auto_now_add=True)

    # Guarda la fecha y hora EXACTA cada vez que se edite o modifique el registro
    actualizacion = models.DateTimeField(auto_now=True)

    # Usuario que creó el registro (obligatorio)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='indicadores_creados'
    )

    # Usuario que modificó el registro por última vez (solo cuando se edite)
    modificado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='indicadores_modificados',
        null=True,
        blank=True
    )

    history = HistoricalRecords()

    def __str__(self):
        return self.denominacion
    class Meta:
        verbose_name = "Indicador"
        verbose_name_plural = "Indicadores"