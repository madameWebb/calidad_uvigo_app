"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.views.static import serve
import os
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent

admin.site.site_header = "Calidade UVIGO"
admin.site.site_title = "Calidade UVIGO"
admin.site.index_title = "Área de xestión"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('gestion.urls')),
    path('admin/gestion/img/<str:filename>', serve, {
        'document_root': os.path.join(BASE_DIR, 'gestion/static/admin/img')
    }),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
