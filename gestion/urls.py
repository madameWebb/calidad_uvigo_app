from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('indicadores/', views.indicadores_publicos, name='indicadores'),
    path('irpd/', views.irpd_publicos, name='irpd'),
    path('centros/', views.centros_publicos, name='centros'),
    path('titulos/', views.titulos_publicos, name='titulos'),
    path('listado/<str:modelo>/', views.listado, name='listado'),
]