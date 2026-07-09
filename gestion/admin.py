from django.contrib import admin
from .models import Indicadores, IRPD, Localizadores, Centros, Seguimentos, SeguimentosTitulos, Titulos, Codigos, Responsables
from django.db import models
from django import forms

class BaseAdmin(admin.ModelAdmin):
    exclude = ('creado_por', 'modificado_por')  # ocultamos estos campos del formulario

    formfield_overrides = {
        models.CharField: {'widget': forms.TextInput(attrs={'size': '100'})},
    }

    def save_model(self, request, obj, form, change):
        if not change:
            obj.creado_por = request.user
        else:
            obj.modificado_por = request.user
        super().save_model(request, obj, form, change)

class IndicadoresAdmin(BaseAdmin):
    list_display = ('codigo', 'denominacion', 'procedemento_asociado', 'tipo_indicador')
    list_filter = ('tipo_indicador', 'irpd', 'sentido')
    search_fields = ('codigo', 'denominacion', 'procedemento_asociado')
    filter_horizontal = ('centros', 'titulos')
    

class IRPDAdmin(BaseAdmin):
    list_display = ('criterio', 'denominacion',)
    search_fields = ('denominacion',)
    
    fieldsets = (
        ('Información dos IRPDs', {
            'fields': ('criterio', 'denominacion', 'estandar', 'descricion',)
        }),    
    )   

class LocalizadoresAdmin(BaseAdmin):
    pass   

class CentrosAdmin(BaseAdmin):
    list_display = ('codigo', 'denominacion',)
    search_fields = ('codigo', 'denominacion',)
    list_filter = ('codigo_localizador',)
    
    fieldsets = (
        ('Información dos IRPDs', {
            'fields': ('codigo_localizador','codigo', 'denominacion', 'direccion_web', 'equipo_decanal_directivo',)
        }),    
    )   

class SeguimentosAdmin(BaseAdmin):
    list_filter = ('centro', 'orixe_datos', 'indicador__tipo_indicador', 'valoracion_final')
    search_fields = ('indicador__codigo', 'indicador__denominacion', 'centro__denominacion', 'orixe_datos')
    raw_id_fields = ('indicador', 'centro')
    fieldsets = (
        ('Información dos seguimentos do centro', {
            'fields': ('centro', 'indicador', 'orixe_datos', 'meta', 'tipo_meta', 'resultado', 'observacions')
        }),    
    )

class SeguimentosTitulosAdmin(BaseAdmin):
    list_filter = ('titulo__centro', 'orixe_datos', 'indicador__tipo_indicador', 'valoracion_final')
    search_fields = ('indicador__codigo', 'indicador__denominacion', 'titulo__denominacion', 'titulo__centro__denominacion', 'orixe_datos')
    raw_id_fields = ('indicador', 'titulo')
    fieldsets = (
        ('Información dos seguimentos do centro', {
            'fields': ('titulo', 'indicador', 'orixe_datos', 'meta', 'tipo_meta', 'resultado', 'observacions')
        }),    
    )

class CodigosInline(admin.StackedInline):
    model = Codigos
    extra = 0
    fields = ('plan_sigma', 'estudio_sigma', 'xescampus', 'ruct', 'notas')
    can_delete = False

class TitulosAdmin(BaseAdmin):
    list_display = ('denominacion', 'tipo', 'centro')
    list_filter = ('centro','tipo', 'centro__codigo_localizador')
    search_fields = ('denominacion',)
    raw_id_fields = ('centro',)
    inlines = [CodigosInline]
    
    fieldsets = (
        ('Información do Título', {
            'fields': ('denominacion', 'tipo', 'centro')
        }),    
    )

class CodigosAdmin(BaseAdmin):
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
        return False  # No crear

    def has_change_permission(self, request, obj=None):
        return False  # No editar

    def has_delete_permission(self, request, obj=None):
        return False  # No eliminar


class ResponsablesAdmin(BaseAdmin):
    list_display = ('denominacion',)
    search_fields = ('denominacion',)
    ordering = ('denominacion',)

admin.site.register(Indicadores, IndicadoresAdmin)
admin.site.register(IRPD, IRPDAdmin)
admin.site.register(Localizadores, LocalizadoresAdmin)
admin.site.register(Centros, CentrosAdmin)
admin.site.register(Seguimentos, SeguimentosAdmin)
admin.site.register(SeguimentosTitulos, SeguimentosTitulosAdmin)
admin.site.register(Titulos, TitulosAdmin)
admin.site.register(Codigos, CodigosAdmin)
admin.site.register(Responsables, ResponsablesAdmin)