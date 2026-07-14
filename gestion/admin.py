"""
admin.py — Configuración da área de xestión (Django Admin)

Define como se xestionan os modelos na área de administración.
Personaliza listados, filtros, buscadores e formularios para facilitar
o traballo dos usuarios con permisos de xestión.

Paleta de cores do admin (definida en templates/admin/base_site.html):
    - Morado principal: #4a3f8f
    - Dourado para texto en barras: #f0c040
    - Morado medio (migas de pan): #6b5fb5

Autor: Virginia García Álvarez
Proxecto: Prácticas DAW — Área de Calidade UVIGO
"""

from django.contrib import admin
from .models import (
    Indicadores, IRPD, Localizadores, Centros,
    Seguimentos, SeguimentosTitulos, Titulos, Codigos,
    Responsables, AvaliacionsPdis, MateriasAvaliadas, SeguementoMaterias
)
from django.db import models
from django import forms


# ============================================================
# CLASE BASE DO ADMIN
# ============================================================

class BaseAdmin(admin.ModelAdmin):
    """
    Clase base para todos os admins da aplicación.
    
    Proporciona:
    - Ocultación automática dos campos de auditoría (creado_por, modificado_por)
      nos formularios (xestiónanse automaticamente no save_model)
    - Campos de texto máis anchos (100 caracteres) para mellor usabilidade
    - Asignación automática do usuario que crea/modifica cada rexistro
    """
    # Ocultar campos de auditoría do formulario (xestiónanse automaticamente)
    exclude = ('creado_por', 'modificado_por')

    # Facer os campos de texto máis anchos para mellor usabilidade
    formfield_overrides = {
        models.CharField: {'widget': forms.TextInput(attrs={'size': '100'})},
    }

    def save_model(self, request, obj, form, change):
        """
        Asigna automaticamente o usuario actual como creador ou modificador.
        
        - Novo rexistro (change=False): asigna creado_por
        - Rexistro existente (change=True): asigna modificado_por
        """
        if not change:
            obj.creado_por = request.user
        else:
            obj.modificado_por = request.user
        super().save_model(request, obj, form, change)


# ============================================================
# ADMINS DE ESTRUTURA ACADÉMICA
# ============================================================

class IndicadoresAdmin(BaseAdmin):
    """
    Admin para xestionar os indicadores de calidade.
    
    Mostra código, denominación, procedemento e tipo en listado.
    Permite filtrar por tipo, IRPD e sentido.
    Os campos M:N (centros e títulos) úsanse con selector horizontal (filter_horizontal).
    """
    list_display = ('codigo', 'denominacion', 'procedemento_asociado', 'tipo_indicador')
    list_filter = ('tipo_indicador', 'irpd', 'sentido')
    search_fields = ('codigo', 'denominacion', 'procedemento_asociado')
    # filter_horizontal: mostra dúas caixas lado a lado para seleccionar relacións M:N
    filter_horizontal = ('centros', 'titulos')


class IRPDAdmin(BaseAdmin):
    """Admin para os criterios IRPD (Informe de Revisión do Sistema pola Dirección)."""
    list_display = ('criterio', 'denominacion',)
    search_fields = ('denominacion',)
    fieldsets = (
        ('Información dos IRPDs', {
            'fields': ('criterio', 'denominacion', 'estandar', 'descricion',)
        }),
    )


class LocalizadoresAdmin(BaseAdmin):
    """Admin para os campus universitarios (Vigo, Ourense, Pontevedra)."""
    pass


class CentrosAdmin(BaseAdmin):
    """
    Admin para os centros universitarios.
    
    Permite buscar por código e denominación, e filtrar por campus.
    """
    list_display = ('codigo', 'denominacion',)
    search_fields = ('codigo', 'denominacion',)
    list_filter = ('codigo_localizador',)
    fieldsets = (
        ('Información do Centro', {
            'fields': ('codigo_localizador', 'codigo', 'denominacion', 'direccion_web', 'equipo_decanal_directivo',)
        }),
    )


class CodigosInline(admin.StackedInline):
    """
    Inline para mostrar os códigos SIGMA dunha titulación dentro do seu formulario.
    
    Permite ver e editar os códigos directamente desde a páxina de edición do título.
    Non se permite eliminar códigos desde aquí (can_delete=False):
    os códigos elimínanse automaticamente cando se elimina o título (CASCADE no modelo).
    
    Campos: plan_sigma, estudio_sigma, xescampus, ruct, notas
    """
    model = Codigos
    extra = 0  # Non mostrar formularios baleiros adicionais
    fields = ('plan_sigma', 'estudio_sigma', 'xescampus', 'ruct', 'notas')
    can_delete = False  # Eliminar só cando se elimine o título (CASCADE)


class TitulosAdmin(BaseAdmin):
    """
    Admin para as titulacións universitarias.
    
    Inclúe o inline de Codigos para ver e editar os códigos SIGMA
    directamente desde o formulario do título.
    Usa raw_id_fields para o centro (búsqueda por ID en lugar de dropdown).
    """
    list_display = ('denominacion', 'tipo', 'centro')
    list_filter = ('centro', 'tipo', 'centro__codigo_localizador')
    search_fields = ('denominacion',)
    raw_id_fields = ('centro',)  # Selector de ID en lugar de dropdown (máis eficiente con moitos centros)
    inlines = [CodigosInline]
    fieldsets = (
        ('Información do Título', {
            'fields': ('denominacion', 'tipo', 'centro')
        }),
    )


class CodigosAdmin(BaseAdmin):
    """
    Admin para os códigos SIGMA das titulacións. SÓ CONSULTA.
    
    Os códigos xestiónanse desde a páxina de edición dos títulos (CodigosInline).
    Desde aquí só se pode consultar — non crear, editar nin eliminar.
    
    Razón: os códigos son datos externos (SIGMA, XesCampus, RUCT) que se importan
    desde Excel e non deben modificarse manualmente de forma illada.
    """
    list_display = ('plan_sigma', 'titulo',)
    list_filter = ('titulo__centro',)
    search_fields = ('plan_sigma', 'titulo__denominacion',)
    raw_id_fields = ('titulo',)
    ordering = ('plan_sigma', 'titulo__denominacion')
    fieldsets = (
        ('Información dos códigos', {
            'fields': ('plan_sigma', 'estudio_sigma', 'xescampus', 'ruct', 'notas')
        }),
        ('Relación', {
            'fields': ('titulo',)
        }),
    )

    def has_add_permission(self, request):
        return False  # Non se pode crear desde aquí

    def has_change_permission(self, request, obj=None):
        return False  # Non se pode editar desde aquí

    def has_delete_permission(self, request, obj=None):
        return False  # Non se pode eliminar desde aquí (só con CASCADE ao eliminar título)


class ResponsablesAdmin(BaseAdmin):
    """Admin para os roles responsables do seguimento de indicadores."""
    list_display = ('denominacion',)
    search_fields = ('denominacion',)
    ordering = ('denominacion',)


# ============================================================
# ADMIN DE AVALIACIÓNS DO PDI
# ============================================================

class AvaliacionsPdisForm(forms.ModelForm):
    """
    Formulario personalizado para AvaliacionsPdis.
    
    Engade restricións nos campos numéricos:
    - Valor mínimo: 0 (non se permiten negativos)
    - Valor inicial: 0 (para evitar campos baleiros)
    - Step: 1 (só números enteiros)
    
    O campo 'totales' non aparece no formulario porque se calcula
    automaticamente no save() do modelo como suma das categorías.
    """
    excelentes = forms.IntegerField(min_value=0, initial=0, widget=forms.NumberInput(attrs={'step': 1, 'min': 0}))
    notables = forms.IntegerField(min_value=0, initial=0, widget=forms.NumberInput(attrs={'step': 1, 'min': 0}))
    favorables = forms.IntegerField(min_value=0, initial=0, widget=forms.NumberInput(attrs={'step': 1, 'min': 0}))
    desfavorables = forms.IntegerField(min_value=0, initial=0, widget=forms.NumberInput(attrs={'step': 1, 'min': 0}))

    class Meta:
        model = AvaliacionsPdis
        fields = '__all__'


class AvaliacionsPdisAdmin(BaseAdmin):
    """
    Admin para as avaliacións do PDI por titulación e curso.
    
    Métodos personalizados de display:
    - get_indicadores: mostra os códigos dos indicadores asociados (M:N)
    - titulo__centro: mostra o centro ao que pertence a titulación
    
    Lóxica especial en save_related:
    Se non se selecciona ningún indicador ao gardar, asígnase automaticamente
    o indicador I7-3 ('Resultados do PDI avaliado') por defecto.
    """
    readonly_fields = ('data_limite',)  # Calculada automaticamente no modelo
    form = AvaliacionsPdisForm
    raw_id_fields = ('indicador', 'titulo',)
    list_display = ('orixe_datos', 'get_indicadores', 'titulo__centro', 'titulo', 'totales')
    list_filter = ('orixe_datos', 'titulo__centro', 'titulo__centro__codigo_localizador')
    search_fields = ('indicador__codigo', 'titulo__denominacion', 'titulo__id')
    ordering = ('titulo',)

    def get_indicadores(self, obj):
        """Devolve os códigos dos indicadores separados por coma para mostrar no listado."""
        return ', '.join([str(i.codigo) for i in obj.indicador.all()])
    get_indicadores.short_description = 'Indicadores'

    @admin.display(description='Centro')
    def titulo__centro(self, obj):
        """Devolve o centro da titulación para mostrar no listado."""
        return obj.titulo.centro

    fieldsets = (
        ('Información das avaliacións', {
            'fields': ('orixe_datos', 'indicador', 'titulo', 'data_limite')
        }),
        ('Avaliacións dos PDIs', {
            'fields': ('excelentes', 'notables', 'favorables', 'desfavorables')
        }),
    )

    def save_related(self, request, form, formsets, change):
        """
        Asigna o indicador I7-3 por defecto se non se seleccionou ningún.
        
        Execútase despois de gardar as relacións M:N, polo que pode comprobar
        se o campo M:N 'indicador' quedou baleiro e asignar o valor por defecto.
        """
        super().save_related(request, form, formsets, change)
        obj = form.instance
        if not obj.indicador.exists():
            indicador_default = Indicadores.objects.filter(codigo='I7-3').first()
            if indicador_default:
                obj.indicador.add(indicador_default)


# ============================================================
# ADMINS DE MATERIAS E SEGUIMENTOS
# ============================================================

class MateriasAvaliadasAdmin(BaseAdmin):
    """
    Admin para as materias (asignaturas) avaliadas.
    
    Permite buscar por código, nome da materia e denominación do título.
    Usa raw_id_fields para o título (eficiente con moitas titulacións).
    """
    list_display = ('codigo', 'materia', 'titulo')
    list_filter = ('titulo__centro',)
    search_fields = ('codigo', 'materia', 'titulo__denominacion')
    raw_id_fields = ('titulo',)
    ordering = ('codigo', 'titulo__denominacion')


class SeguimentosAdmin(BaseAdmin):
    """
    Admin para os seguimentos de indicadores a nivel de centro.
    
    data_limite é readonly porque se calcula automaticamente no modelo.
    Usa raw_id_fields para indicador e centro (eficiente con moitos rexistros).
    """
    readonly_fields = ('data_limite',)
    list_filter = ('centro', 'orixe_datos', 'indicador__tipo_indicador', 'valoracion_final')
    search_fields = ('indicador__codigo', 'indicador__denominacion', 'centro__denominacion', 'orixe_datos')
    raw_id_fields = ('indicador', 'centro')
    fieldsets = (
        ('Información dos seguimentos do centro', {
            'fields': ('centro', 'indicador', 'orixe_datos', 'meta', 'tipo_meta', 'resultado', 'observacions', 'data_limite')
        }),
    )


class SeguimentosTitulosAdmin(BaseAdmin):
    """
    Admin para os seguimentos de indicadores a nivel de titulación.
    
    Similar a SeguimentosAdmin pero para titulacións en lugar de centros.
    """
    readonly_fields = ('data_limite',)
    list_filter = ('titulo__centro', 'orixe_datos', 'indicador__tipo_indicador', 'valoracion_final')
    search_fields = ('indicador__codigo', 'indicador__denominacion', 'titulo__denominacion', 'titulo__centro__denominacion', 'orixe_datos')
    raw_id_fields = ('indicador', 'titulo')
    fieldsets = (
        ('Información dos seguimentos do título', {
            'fields': ('titulo', 'indicador', 'orixe_datos', 'meta', 'tipo_meta', 'resultado', 'observacions', 'data_limite',)
        }),
    )


class SeguementoMateriasAdmin(BaseAdmin):
    """
    Admin para os seguimentos de indicadores a nivel de materia (asignatura).
    
    resultado e data_limite son readonly porque se calculan automaticamente no modelo:
    - resultado = taxa (se hai meta) ou 0 (se non hai meta)
    - data_limite = 31/12 do ano seguinte á finalización do curso
    """
    readonly_fields = ('resultado', 'data_limite')
    list_display = ('materia__codigo', 'materia', 'resultado')
    list_filter = ('orixe_datos', 'materia__titulo__centro', 'resultado',)
    search_fields = ('materia__codigo', 'materia__materia', 'orixe_datos')
    raw_id_fields = ('materia', 'indicador')
    ordering = ('materia__codigo',)
    fieldsets = (
        ('Información das materias', {
            'fields': ('orixe_datos', 'indicador', 'materia',)
        }),
        ('Seguemento das materias', {
            'fields': ('meta', 'taxa', 'resultado', 'data_limite')
        }),
    )


# ============================================================
# REXISTRO DOS MODELOS NO ADMIN
# ============================================================

admin.site.register(Indicadores, IndicadoresAdmin)
admin.site.register(IRPD, IRPDAdmin)
admin.site.register(Localizadores, LocalizadoresAdmin)
admin.site.register(Centros, CentrosAdmin)
admin.site.register(Seguimentos, SeguimentosAdmin)
admin.site.register(SeguimentosTitulos, SeguimentosTitulosAdmin)
admin.site.register(Titulos, TitulosAdmin)
admin.site.register(Codigos, CodigosAdmin)
admin.site.register(Responsables, ResponsablesAdmin)
admin.site.register(AvaliacionsPdis, AvaliacionsPdisAdmin)
admin.site.register(MateriasAvaliadas, MateriasAvaliadasAdmin)
admin.site.register(SeguementoMaterias, SeguementoMateriasAdmin)