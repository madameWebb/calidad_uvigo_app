from django.db import models

# Create your models here.
class Indicadores(models.Model):
    # Un campo de texto para el nombre (máximo 100 caracteres)
    codigo = models.CharField(max_length=100)
    denominacion_indicador = models.CharField(max_length=255)
    
    # Un campo de texto más largo para la denominación y la descripción
    denominacion = models.TextField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)

    # Enlace web
    fuente = models.URLField(max_length=500, blank=True, null=True)
    
    # Un campo numérico para los irpd, ya que van del 1 al 7, con un largo de 1 es suficinte
    irpd = models.IntegerField(default=1)

    # Guarda la fecha y hora EXACTA cuando se crea el registro por primera vez
    creacion = models.DateTimeField(auto_now_add=True)
    
    # Guarda la fecha y hora EXACTA cada vez que se edite o modifique el registro
    actualizacion = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.denominacion