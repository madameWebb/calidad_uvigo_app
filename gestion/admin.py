from django.contrib import admin
from .models import Indicadores, IRPD
from django.db import models
from django import forms

class IndicadoresAdmin(admin.ModelAdmin):
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

class IRPDAdmin(admin.ModelAdmin):
    exclude = ('creado_por', 'modificado_por')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.creado_por = request.user
        else:
            obj.modificado_por = request.user
        super().save_model(request, obj, form, change)

admin.site.register(Indicadores, IndicadoresAdmin)
admin.site.register(IRPD, IRPDAdmin)