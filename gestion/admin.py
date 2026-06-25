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

class TitulosAdmin(BaseAdmin):
    pass

class CodigosAdmin(BaseAdmin):
    pass

class ResponsablesAdmin(BaseAdmin):
    pass

admin.site.register(Indicadores, IndicadoresAdmin)
admin.site.register(IRPD, IRPDAdmin)
admin.site.register(Localizadores, LocalizadoresAdmin)
admin.site.register(Centros, CentrosAdmin)
admin.site.register(Seguimentos, SeguimentosAdmin)
admin.site.register(SeguimentosTitulos, SeguimentosTitulosAdmin)
admin.site.register(Titulos, TitulosAdmin)
admin.site.register(Codigos, CodigosAdmin)
admin.site.register(Responsables, CodigosAdmin)