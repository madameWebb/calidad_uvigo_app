from django.conf import settings
from django.db import models
from simple_history.models import HistoricalRecords
from datetime import date

def generar_curso_choices():
    año_actual = date.today().year
    choices = []
    for i in range(-3, 3):  # desde 3 años atrás hasta 2 años por delante
        inicio = año_actual + i
        choices.append((
            f"{str(inicio)[-2:]}/{str(inicio+1)[-2:]}",
            f"{str(inicio)[-2:]}/{str(inicio+1)[-2:]}"
        ))
    return choices

def get_responsable_por_defecto():
    responsable, creado = Responsables.objects.get_or_create(
        denominacion="Coordinador de calidade"
    )
    return responsable.pk


# Create your models here.
class ModeloBase(models.Model):
    # Guarda la fecha y hora EXACTA cuando se crea el registro por primera vez
    creacion = models.DateTimeField(auto_now_add=True)
    
    # Guarda la fecha y hora EXACTA cada vez que se edite o modifique el registro
    actualizacion = models.DateTimeField(auto_now=True)
    
    # Usuario que creó el registro (obligatorio)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='%(class)s_creados'
    )
    
    # Usuario que modificó el registro por última vez (solo cuando se edite)
    modificado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='%(class)s_modificados',
        null=True,
        blank=True
    )

    history = HistoricalRecords(inherit=True)

    class Meta:
        abstract = True  # ← esta línea es la clave: dice "esto no es una tabla real"

class IRPD(ModeloBase):
    criterio = models.CharField(max_length=20, unique=True)
    denominacion = models.CharField(max_length=255)
    estandar = models.TextField(blank=True, null=True)
    descricion = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "IRPD"
        verbose_name_plural = "IRPDs"

    def __str__(self):
        return self.denominacion

class Responsables(ModeloBase):
    denominacion = models.CharField(max_length=255)
    descricion = models.TextField(blank=True, null=True, verbose_name="Descrición")
    
    class Meta:
        verbose_name = "Responsable"
        verbose_name_plural = "Responsables"
        ordering = ('denominacion',)
    
    def __str__(self):
        return self.denominacion   
 
class Localizadores(ModeloBase):
    codigo = models.CharField(max_length=50)
    campus = models.CharField(max_length=255)
    
    class Meta:
        verbose_name = "Localización"
        verbose_name_plural = "Localizaciones"

    def __str__(self):
        return self.campus
    
class Centros(ModeloBase):
    codigo_localizador = models.ForeignKey(Localizadores, on_delete=models.PROTECT, related_name='centros')
    codigo = models.CharField(max_length=50)
    denominacion= models.CharField(max_length=255)
    direccion_web = models.URLField(max_length=500, blank=True, null=True)
    equipo_decanal_directivo = models.URLField(
        verbose_name="Equipo Decanal/Directivo",
        help_text="Enlace á páxina do equipo decanal ou directivo"
    )
    
    class Meta:
        verbose_name = "Centro"
        verbose_name_plural = "Centros"

    def __str__(self):
        return self.denominacion

class Titulos(ModeloBase):
    TIPO_CHOICES = [('grao', 'Grao'), ('dobre grao', 'Dobre Grao'), ('máster', 'Máster'),]
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    denominacion = models.CharField(max_length=255)
    centro = models.ForeignKey(Centros, on_delete=models.PROTECT, related_name='titulos')
    
    class Meta:
        verbose_name = "Título"
        verbose_name_plural = "Títulos"

    def __str__(self):
        return self.denominacion

class Codigos(ModeloBase):
    titulo = models.OneToOneField(Titulos, on_delete=models.CASCADE, related_name='codigos', unique=True)
    plan_sigma = models.CharField(max_length=20, unique=True)
    estudio_sigma = models.CharField(max_length=20, null=True, blank=True)
    xescampus = models.CharField(max_length=20, null=True, blank=True)
    ruct = models.CharField(max_length=20, null=True, blank=True)
    notas = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Código"
        verbose_name_plural = "Códigos"

    def __str__(self):
        return self.plan_sigma

class Indicadores(ModeloBase):
    TIPO_INDICADOR_CHOICES = [
        ('institucional', 'Institucional'),
        ('estratexico', 'Estratégico'),
        ('calidade', 'Calidade'),
    ]
    codigo = models.CharField(max_length=50)
    tipo_indicador = models.CharField(
        max_length=20,
        choices=TIPO_INDICADOR_CHOICES,
        default='institucional',
        verbose_name="Tipo de Indicador"
    )
    denominacion = models.CharField(max_length=255)
    procedemento_asociado = models.CharField(max_length=255, verbose_name="Procedemento Asociado")
    descricion = models.TextField(blank=True, null=True)
    fonte = models.URLField(max_length=500, blank=True, null=True)
    irpd = models.ForeignKey(IRPD, on_delete=models.PROTECT, related_name='indicadores')
    responsable = models.ForeignKey(Responsables, on_delete=models.PROTECT, related_name='indicadores', default=get_responsable_por_defecto)
    SENTIDO_CHOICES = [
    ('positivo', 'A máis, mellor'),      # ej: matriculados
    ('negativo', 'A menos, mellor'),    # ej: tasa de abandono
    ]
    sentido = models.CharField(max_length=10, choices=SENTIDO_CHOICES)
    centros = models.ManyToManyField(Centros, related_name='indicadores', blank=True)
    titulos = models.ManyToManyField(Titulos, related_name='indicadores', blank=True)
    def procedemento_titulo(self):
        """Retorna solo hasta que encuentra un guión entre espacios"""
        if '\n' in self.procedemento_asociado:
            return self.procedemento_asociado.split('\n')[0].strip()
        return self.procedemento_asociado
    
    def procedemento_items(self):
        """Retorna los items después de los dos puntos como lista"""
        if '\n' not in self.procedemento_asociado:
            return []
        parte = self.procedemento_asociado.split('\n', 1)[1].strip()
        return [item.strip() for item in parte.split('\n')]


    class Meta:
        verbose_name = "Indicador"
        verbose_name_plural = "Indicadores"

    def __str__(self):
        return self.denominacion
    
class SeguimentoBase(ModeloBase):
    """Campos y lógica comunes a los seguimientos de centro y de título."""
    indicador = models.ForeignKey(Indicadores, on_delete=models.PROTECT, related_name='%(class)ss')
    orixe_datos = models.CharField(
        max_length=10,
        choices=generar_curso_choices,
        verbose_name="Orixe dos datos (curso):",
        help_text="Curso de orixe dos datos (non o curso no que se introducen)"
    )
    meta = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    TIPO_META_CHOICES = [
        ('numero', 'Número'),
        ('porcentaje', 'Porcentaje'),
    ]
    tipo_meta = models.CharField(max_length=10, choices=TIPO_META_CHOICES)
    resultado = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    data_limite = models.DateField(
        verbose_name="Data límite para a introducción dos datos",
        help_text="Calculada automaticamente: 31 de decembro, ano e medio despóis da finalización do curso",
        blank=True
    )
    valoracion_final = models.BooleanField(null=True, blank=True)
    observacions = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.data_limite:
            ano_finalizacion = int(self.orixe_datos.split('/')[1])
            self.data_limite = date(2000 + ano_finalizacion + 1, 12, 31)
        super().save(*args, **kwargs)

    @property
    def valoracion(self):
        if self.resultado is None or self.meta is None:
            return None
        if self.indicador.sentido == 'positivo':
            return self.resultado >= self.meta
        else:
            return self.resultado <= self.meta

    def pechar_se_corresponde(self):
        if self.valoracion_final is None and date.today() >= self.data_limite:
            self.valoracion_final = self.valoracion
            self.save(update_fields=['valoracion_final'])
        return self.valoracion_final

class Seguimentos(SeguimentoBase):
    centro = models.ForeignKey(Centros, on_delete=models.PROTECT, related_name='seguimentos')

    class Meta:
        verbose_name = "Seguimento do Centro"
        verbose_name_plural = "Seguimento dos Centro"

    def __str__(self):
        return f"{self.indicador} - {self.centro} - {self.orixe_datos}"


class SeguimentosTitulos(SeguimentoBase):
    titulo = models.ForeignKey(Titulos, on_delete=models.PROTECT, related_name='seguimentosTitulo')

    class Meta:
        verbose_name = "Seguimento do Título"
        verbose_name_plural = "Seguimento dos Títulos"

    def __str__(self):
        return f"{self.indicador} - {self.titulo} - {self.orixe_datos}"