from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('listado/<str:modelo>/', views.listado, name='listado'),
]