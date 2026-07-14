"""
models.py — Modelos de datos da aplicación Calidade UVIGO

Define a estrutura da base de datos para a xestión de indicadores de calidade
da Universidade de Vigo. Inclúe modelos para centros, títulos, indicadores,
seguimentos e avaliacións do PDI.

Autor: Virginia García Álvarez
Proxecto: Prácticas DAW — Área de Calidade UVIGO
"""

from django.conf import settings
from django.db import models
from simple_history.models import HistoricalRecords
from datetime import date
from django.core.validators import MinValueValidator


def generar_curso_choices():
    """
    Xera dinamicamente as opcións de curso académico para os campos de selección.
    
    Devolve un rango de 6 cursos: 3 anteriores ao actual e 2 posteriores.
    Formato: 'XX/YY' (ex: '23/24', '24/25')
    """
    año_actual = date.today().year
    choices = []
    for i in range(-3, 3):
        inicio = año_actual + i
        choices.append((
            f"{str(inicio)[-2:]}/{str(inicio+1)[-2:]}",
            f"{str(inicio)[-2:]}/{str(inicio+1)[-2:]}"
        ))
    return choices


def get_responsable_por_defecto():
    """
    Devolve o ID do responsable por defecto ('Coordinador de calidade').
    Créao se non existe. Úsase como valor por defecto no modelo Indicadores.
    """
    responsable, creado = Responsables.objects.get_or_create(
        denominacion="Coordinador de calidade"
    )
    return responsable.pk


class ModeloBase(models.Model):
    """
    Clase abstracta base para todos os modelos da aplicación.
    
    Proporciona:
    - Rexistro automático de datas de creación e modificación
    - Trazabilidade de usuarios (quen creou e quen modificou)
    - Historial de cambios mediante django-simple-history
    
    Ao ser abstracta (abstract = True), non crea táboa na BD.
    Todos os modelos que herdan dela terán estes campos automaticamente.
    """
    # Data e hora de creación (asígnase automaticamente ao crear o rexistro)
    creacion = models.DateTimeField(auto_now_add=True)
    
    # Data e hora da última modificación (actualízase automaticamente en cada gardado)
    actualizacion = models.DateTimeField(auto_now=True)
    
    # Usuario que creou o rexistro (obrigatorio, non se pode borrar o usuario se ten rexistros)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='%(class)s_creados'
    )
    
    # Usuario que modificou o rexistro por última vez (opcional)
    modificado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='%(class)s_modificados',
        null=True,
        blank=True
    )
    
    # Historial automático de cambios (herdado por todos os modelos fillos)
    history = HistoricalRecords(inherit=True)

    class Meta:
        abstract = True  # Non crea táboa na BD; é só unha plantilla


# ============================================================
# ESTRUTURA ACADÉMICA
# ============================================================

class IRPD(ModeloBase):
    """
    Informe de Revisión do Sistema pola Dirección.
    
    Clasifica os indicadores segundo os criterios do sistema de calidade.
    Cada indicador pertence a un criterio IRPD (ex: criterio 1, criterio 2...).
    O criterio '8' úsase como fallback para indicadores sen clasificar.
    """
    criterio = models.CharField(max_length=20, unique=True)
    denominacion = models.CharField(max_length=255)
    estandar = models.TextField(blank=True, null=True)
    descricion = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "IRPD"
        verbose_name_plural = "IRPDs"
        ordering = ('criterio',)

    def __str__(self):
        return self.denominacion


class Responsables(ModeloBase):
    """
    Roles responsables do seguimento dos indicadores.
    
    Exemplos: 'Coordinador de calidade', 'Decanato ou dirección do centro'.
    Non son persoas concretas senón roles ou cargos.
    """
    denominacion = models.CharField(max_length=255)
    descricion = models.TextField(blank=True, null=True, verbose_name="Descrición")

    class Meta:
        verbose_name = "Responsable"
        verbose_name_plural = "Responsables"
        ordering = ('denominacion',)

    def __str__(self):
        return self.denominacion


class Localizadores(ModeloBase):
    """
    Campus universitarios da UVIGO.
    
    Cada localizador identifica un campus (Vigo, Ourense, Pontevedra).
    O código do localizador forma parte do código identificador único de cada centro.
    """
    codigo = models.CharField(max_length=50)
    campus = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Localización"
        verbose_name_plural = "Localizaciones"

    def __str__(self):
        return self.campus


class Centros(ModeloBase):
    """
    Centros universitarios da UVIGO (facultades, escolas, etc.).
    
    O código identificador único dun centro combina o código do localizador
    (campus) co código do propio centro. Exemplo: campus '1' + centro '01' = '101'.
    
    Campos URL:
    - direccion_web: páxina web oficial do centro
    - equipo_decanal_directivo: páxina do equipo de goberno do centro
    """
    codigo_localizador = models.ForeignKey(Localizadores, on_delete=models.PROTECT, related_name='centros')
    codigo = models.CharField(max_length=50)
    denominacion = models.CharField(max_length=255)
    direccion_web = models.URLField(max_length=500, blank=True, null=True)
    equipo_decanal_directivo = models.URLField(
        verbose_name="Equipo Decanal/Directivo",
        help_text="Enlace á páxina do equipo decanal ou directivo"
    )

    class Meta:
        verbose_name = "Centro"
        verbose_name_plural = "Centros"
        ordering = ('denominacion',)

    def __str__(self):
        return self.denominacion


class Titulos(ModeloBase):
    """
    Titulacións universitarias impartidas nos centros da UVIGO.
    
    Un mesmo título (ex: 'Grao en Dereito') pode impartirse en varios centros,
    polo que existirán rexistros distintos por centro.
    
    Tipos: Grao, Dobre Grao, Máster.
    """
    TIPO_CHOICES = [
        ('grao', 'Grao'),
        ('dobre grao', 'Dobre Grao'),
        ('máster', 'Máster'),
    ]
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    denominacion = models.CharField(max_length=255)
    centro = models.ForeignKey(Centros, on_delete=models.PROTECT, related_name='titulos')

    class Meta:
        verbose_name = "Título"
        verbose_name_plural = "Títulos"
        ordering = ('denominacion',)

    def __str__(self):
        return self.denominacion


class Codigos(ModeloBase):
    """
    Códigos identificadores externos de cada titulación.
    
    Cada título ten un único conxunto de códigos nos sistemas externos:
    - plan_sigma / estudio_sigma: códigos no sistema SIGMA (xestión académica UVIGO)
    - xescampus: código na plataforma XesCampus
    - ruct: código no Rexistro de Universidades, Centros e Títulos (ministerio)
    
    Relación 1:1 con Titulos (cada título ten como máximo un conxunto de códigos).
    Se se elimina o título, elimínanse os códigos automaticamente (CASCADE).
    """
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


class MateriasAvaliadas(ModeloBase):
    """
    Asignaturas avaliadas no marco do seguimento de indicadores de calidade.
    
    Cada materia ten un código único (código de asignatura no sistema SIGMA)
    e está asociada a un título concreto nun centro concreto.
    
    Os indicadores asociados a cada materia gárdanse mediante a relación
    ManyToMany definida en Indicadores.materia.
    """
    codigo = models.CharField(max_length=50, unique=True, verbose_name="Código materia")
    materia = models.CharField(max_length=255, verbose_name="Asignatura")
    titulo = models.ForeignKey(Titulos, on_delete=models.PROTECT, related_name='materias')

    class Meta:
        verbose_name = "Materia Avaliada"
        verbose_name_plural = "Materias Avaliadas"

    def __str__(self):
        return f"{self.codigo} - {self.materia}"


# ============================================================
# INDICADORES DE CALIDADE
# ============================================================

class Indicadores(ModeloBase):
    """
    Indicadores de calidade do sistema de xestión da UVIGO.
    
    Tipos de indicador:
    - institucional: aplícase a todos os centros da UVIGO
    - estratéxico: propio do centro (definido por cada centro)
    - calidade: indicadores dos programas de calidade
    
    Sentido do indicador:
    - positivo ('A máis, mellor'): valores máis altos son mellores (ex: taxa de éxito)
    - negativo ('A menos, mellor'): valores máis baixos son mellores (ex: taxa de abandono)
    
    O sentido úsase para calcular automaticamente se se acadou a meta nos seguimentos.
    
    Relacións:
    - centros: centros onde se aplica este indicador (M:N)
    - titulos: títulos onde se aplica este indicador (M:N)
    - materia: materias asociadas a este indicador (M:N)
    """
    TIPO_INDICADOR_CHOICES = [
        ('institucional', 'Institucional'),
        ('estratexico', 'Estratéxico'),
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
    responsable = models.ForeignKey(
        Responsables,
        on_delete=models.PROTECT,
        related_name='indicadores',
        default=get_responsable_por_defecto
    )

    SENTIDO_CHOICES = [
        ('positivo', 'A máis, mellor'),   # ex: nº matriculados, taxa de éxito
        ('negativo', 'A menos, mellor'),  # ex: taxa de abandono, nº queixas
    ]
    sentido = models.CharField(max_length=10, choices=SENTIDO_CHOICES)

    centros = models.ManyToManyField(Centros, related_name='indicadores', blank=True)
    titulos = models.ManyToManyField(Titulos, related_name='indicadores', blank=True)
    materia = models.ManyToManyField(MateriasAvaliadas, related_name='indicadores', blank=True)

    def procedemento_titulo(self):
        """
        Devolve o título do procedemento asociado (primeira liña).
        
        O procedemento_asociado pode ter varias liñas:
        - Primeira liña: nome do procedemento (ex: 'PE-01 Xestión do PAS')
        - Liñas seguintes: obxectivos ou programas asociados
        
        Úsase no encabezado das tarxetas da vista pública.
        """
        if '\n' in self.procedemento_asociado:
            return self.procedemento_asociado.split('\n')[0].strip()
        return self.procedemento_asociado

    def procedemento_items(self):
        """
        Devolve os ítems do procedemento como lista (liñas despois da primeira).
        
        Úsase no corpo despregable das tarxetas da vista pública.
        Devolve lista baleira se o procedemento só ten unha liña.
        """
        if '\n' not in self.procedemento_asociado:
            return []
        parte = self.procedemento_asociado.split('\n', 1)[1].strip()
        return [item.strip() for item in parte.split('\n')]

    class Meta:
        verbose_name = "Indicador"
        verbose_name_plural = "Indicadores"
        ordering = ('codigo', 'denominacion')

    def __str__(self):
        return self.denominacion


# ============================================================
# AVALIACIÓNS DO PDI
# ============================================================

class AvaliacionsPdis(ModeloBase):
    """
    Resultados da avaliación do PDI (Persoal Docente e Investigador) por titulación e curso.
    
    Os datos provén do programa DOCENTIA e reflicten o resultado da avaliación
    do profesorado en cada titulación.
    
    Categorías de avaliación: excelente, notable, favorable, desfavorable.
    O campo 'totales' calcúlase automaticamente como suma das catro categorías.
    
    O campo 'indicador' é opcional (M:N): por defecto asígnase o indicador I7-3
    ('Resultados do PDI avaliado'), pero pode cambiarse se o centro usa un diferente.
    
    A 'data_limite' calcúlase automaticamente: 31 de decembro, ano e medio despois
    da finalización do curso (ex: curso 23/24 → límite 31/12/2025).
    """
    indicador = models.ManyToManyField(
        Indicadores,
        related_name='avaliacions_pdis',
        blank=True,
        help_text='Cubrir só en caso de que o indicador sexa diferente de '
                  '"Resultados do PDI avaliado", co procedemento asociado "PE-02 Xestión de PDI"'
    )
    titulo = models.ForeignKey(Titulos, on_delete=models.PROTECT, related_name='avaliacion_pdis')
    orixe_datos = models.CharField(
        max_length=10,
        choices=generar_curso_choices,
        verbose_name="Orixe dos datos (curso)",
        help_text="Curso de orixe dos datos (non o curso no que se introducen)"
    )
    data_limite = models.DateField(
        verbose_name="Data límite para a introducción dos datos",
        blank=True,
        null=True
    )
    totales = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Total PDIs"
    )
    excelentes = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Número de PDIs excelentes"
    )
    notables = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Número de PDIs notables"
    )
    favorables = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Número de PDIs favorables"
    )
    desfavorables = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Número de PDIs desfavorables"
    )

    class Meta:
        verbose_name = "Avaliación PDI"
        verbose_name_plural = "Avaliacións PDI"
        unique_together = ('titulo', 'orixe_datos')

    def __str__(self):
        return f"{self.titulo} - {self.orixe_datos}"

    def save(self, *args, **kwargs):
        """
        Gardado personalizado:
        1. Calcula data_limite automaticamente se non está definida
        2. Calcula totales como suma das categorías
        3. Se é un rexistro novo e non ten indicador, asigna I7-3 por defecto
        """
        # Calcular data límite: 31 de decembro do ano seguinte á finalización do curso
        if not self.data_limite:
            ano_finalizacion = int(self.orixe_datos.split('/')[1])
            self.data_limite = date(2000 + ano_finalizacion + 1, 12, 31)

        # Calcular total automaticamente
        self.totales = self.excelentes + self.notables + self.favorables + self.desfavorables

        is_new = self.pk is None
        super().save(*args, **kwargs)

        # Asignar indicador por defecto (I7-3) se é novo e non ten indicador
        if is_new and not self.indicador.exists():
            indicador_default = Indicadores.objects.filter(codigo='I7-3').first()
            if indicador_default:
                self.indicador.add(indicador_default)


# ============================================================
# SEGUIMENTOS DE INDICADORES
# ============================================================

class SeguimentoBase(ModeloBase):
    """
    Clase abstracta base para os seguimentos de indicadores.
    
    Un seguimento rexistra os valores (meta e resultado) dun indicador
    nun período académico concreto (orixe_datos).
    
    Campos herdados por Seguimentos e SeguimentosTitulos:
    - meta: valor obxectivo a acadar
    - tipo_meta: se a meta é un número absoluto ou porcentaxe
    - resultado: valor real acadado (pode ser -1 se non aplica)
    - data_limite: data límite para introducir os datos (calculada automaticamente)
    - valoracion_final: resultado final una vez pechado o período
    - observacions: notas ou comentarios sobre o seguimento
    
    Propiedades calculadas:
    - valoracion: compara resultado con meta segundo o sentido do indicador
    - pechar_se_corresponde: pecha o seguimento cando chega a data límite
    """
    indicador = models.ForeignKey(
        Indicadores,
        on_delete=models.PROTECT,
        related_name='%(class)ss'
    )
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
    # None = sen valorar aínda; True = meta acadada; False = meta non acadada
    valoracion_final = models.BooleanField(null=True, blank=True)
    observacions = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """Calcula data_limite automaticamente se non está definida."""
        if not self.data_limite:
            ano_finalizacion = int(self.orixe_datos.split('/')[1])
            self.data_limite = date(2000 + ano_finalizacion + 1, 12, 31)
        super().save(*args, **kwargs)

    @property
    def valoracion(self):
        """
        Calcula se se acadou a meta segundo o sentido do indicador.
        
        - Indicador positivo (a máis, mellor): resultado >= meta → acadada
        - Indicador negativo (a menos, mellor): resultado <= meta → acadada
        
        Devolve None se non hai resultado ou meta definidos.
        Devolve True se a meta foi acadada, False se non.
        """
        if self.resultado is None or self.meta is None:
            return None
        if self.indicador.sentido == 'positivo':
            return self.resultado >= self.meta
        else:
            return self.resultado <= self.meta

    def pechar_se_corresponde(self):
        """
        Pecha o seguimento automaticamente se chegou a data límite.
        
        Se a data actual é igual ou posterior á data límite e o seguimento
        non está pechado, calcula e garda a valoración final.
        
        Devolve o valor de valoracion_final (True/False/None).
        """
        if self.valoracion_final is None and date.today() >= self.data_limite:
            self.valoracion_final = self.valoracion
            self.save(update_fields=['valoracion_final'])
        return self.valoracion_final


class Seguimentos(SeguimentoBase):
    """
    Seguimento dun indicador a nivel de centro nun curso académico.
    
    Rexistra os valores (meta e resultado) dun indicador para un centro
    concreto nun curso concreto. Usado para indicadores institucionais
    e de calidade que se aplican ao centro no seu conxunto.
    """
    centro = models.ForeignKey(Centros, on_delete=models.PROTECT, related_name='seguimentos')

    class Meta:
        verbose_name = "Seguimento do Centro"
        verbose_name_plural = "Seguimento dos Centro"
        ordering = ('indicador__denominacion',)

    def __str__(self):
        return f"{self.indicador} - {self.centro} - {self.orixe_datos}"


class SeguimentosTitulos(SeguimentoBase):
    """
    Seguimento dun indicador a nivel de titulación nun curso académico.
    
    Similar a Seguimentos pero para indicadores que se aplican a nivel
    de titulación específica (en lugar de ao centro no seu conxunto).
    """
    titulo = models.ForeignKey(Titulos, on_delete=models.PROTECT, related_name='seguimentosTitulo')

    class Meta:
        verbose_name = "Seguimento do Título"
        verbose_name_plural = "Seguimento dos Títulos"
        ordering = ('indicador__denominacion',)

    def __str__(self):
        return f"{self.indicador} - {self.titulo} - {self.orixe_datos}"


class SeguementoMaterias(ModeloBase):
    """
    Seguimento dun indicador a nivel de materia (asignatura) nun curso académico.
    
    A diferenza de Seguimentos e SeguimentosTitulos, este modelo non herda de
    SeguimentoBase porque os seus campos son específicos para materias:
    - Os valores son sempre porcentaxes (taxa de éxito, taxa de rendemento)
    - Non ten tipo_meta nin observacións
    - Inclúe o campo 'taxa' (valor bruto) do que se deriva o resultado
    
    Lóxica de valoración por porcentaxes:
    - Sen meta (meta=0 ou None): 'Sen meta'
    - taxa >= meta: 'Conseguida'
    - taxa >= meta/2: 'Parcialmente conseguida'
    - taxa < meta/2: 'Non conseguida'
    
    O campo 'resultado' calcúlase automaticamente: igual á taxa se hai meta,
    ou 0 se non hai meta definida.
    
    A 'data_limite' calcúlase automaticamente igual que en SeguimentoBase.
    """
    materia = models.ForeignKey(
        MateriasAvaliadas,
        on_delete=models.PROTECT,
        related_name='seguementos'
    )
    indicador = models.ForeignKey(
        Indicadores,
        on_delete=models.PROTECT,
        related_name='seguementos_materias'
    )
    orixe_datos = models.CharField(
        max_length=10,
        choices=generar_curso_choices,
        verbose_name="Orixe dos datos (curso)"
    )
    meta = models.DecimalField(
        max_digits=5, decimal_places=2,
        null=True, blank=True,
        verbose_name="Meta (%)"
    )
    taxa = models.DecimalField(
        max_digits=5, decimal_places=2,
        null=True, blank=True,
        verbose_name="Taxa (%)"
    )
    resultado = models.DecimalField(
        max_digits=5, decimal_places=2,
        null=True, blank=True,
        verbose_name="Resultado (%)"
    )
    data_limite = models.DateField(
        verbose_name="Data límite para a introducción dos datos",
        help_text="Calculada automaticamente: 31 de decembro, ano e medio despóis da finalización do curso",
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = "Seguemento de Materia"
        verbose_name_plural = "Seguementos de Materias"
        unique_together = ('materia', 'indicador', 'orixe_datos')

    def __str__(self):
        return f"{self.materia} - {self.indicador} - {self.orixe_datos}"

    @property
    def valoracion(self):
        """
        Calcula a valoración baseándose na comparación taxa/meta en porcentaxes.
        
        Devolve unha tupla (código, texto_para_mostrar):
        - ('sen_meta', 'Sen meta'): meta non definida ou igual a 0
        - ('conseguida', 'Conseguida (X%)'): taxa >= meta
        - ('parcial', 'Parcialmente conseguida (X%)'): meta/2 <= taxa < meta
        - ('non_conseguida', 'Non conseguida (X%)'): taxa < meta/2
        """
        if self.meta is None or self.meta == 0:
            return ('sen_meta', 'Sen meta')
        if self.taxa >= self.meta:
            return ('conseguida', f'Conseguida ({self.taxa}%)')
        if self.taxa >= self.meta / 2:
            return ('parcial', f'Parcialmente conseguida ({self.taxa}%)')
        return ('non_conseguida', f'Non conseguida ({self.taxa}%)')

    def save(self, *args, **kwargs):
        """
        Gardado personalizado:
        1. Calcula data_limite automaticamente se non está definida
        2. Calcula resultado: igual á taxa se hai meta, 0 se non hai meta
        """
        # Calcular data límite
        if not self.data_limite:
            ano_finalizacion = int(self.orixe_datos.split('/')[1])
            self.data_limite = date(2000 + ano_finalizacion + 1, 12, 31)

        # Calcular resultado
        if self.meta is None or self.meta == 0:
            self.resultado = 0
        else:
            self.resultado = self.taxa

        super().save(*args, **kwargs)