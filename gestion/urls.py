from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('indicadores/', views.indicadores_publicos, name='indicadores'),
    path('irpd/', views.irpd_publicos, name='irpd'),
    path('centros/', views.centros_publicos, name='centros'),
    path('seguimentos-centros/', views.seguimentos_centros_publicos, name='seguimentos_centros'),
    path('seguimentos-centros/<int:centro_id>/<str:orixe_datos>/', views.seguimentos_centro_detalle_publicos, name='seguimentos_centro_detalle'),
    path('titulos/', views.titulos_publicos, name='titulos'),
    path('responsables/', views.responsables_publicos, name='responsables'),
    path('listado/<str:modelo>/', views.listado, name='listado'),
]