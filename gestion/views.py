from django.shortcuts import render
from .models import Indicadores, IRPD

def lista_indicadores_publica(request):
    # Cogemos todos los registros de la tabla en la base de datos
    todos_los_indicadores = Indicadores.objects.all()
    
    # Se los mandamos a una página web que llamaremos 'indicadores.html'
    return render(request, 'gestion/indicadores.html', {'indicadores': todos_los_indicadores})

def lista_irpd_publica(request):
    # Cogemos todos los registros de la tabla en la base de datos
    todos_los_irpd = IRPD.objects.all()
    
    return render(request, 'gestion/irpd.html', {'irpd': todos_los_irpd})

