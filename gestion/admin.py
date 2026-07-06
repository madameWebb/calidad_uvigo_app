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
    pass    

class LocalizadoresAdmin(BaseAdmin):
    pass   

class CentrosAdmin(BaseAdmin):
    pass

class SeguimentosAdmin(BaseAdmin):
    pass

class SeguimentosTitulosAdmin(BaseAdmin):
    pass

class CodigosInline(admin.StackedInline):
    model = Codigos
    extra = 0
    fields = ('plan_sigma', 'estudio_sigma', 'xescampus', 'ruct', 'notas')
    can_delete = False

class TitulosAdmin(BaseAdmin):
    list_display = ('denominacion', 'tipo', 'centro')
    list_filter = ('denominacion',)
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
    
    fieldsets = (
        ('Códigos', {
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