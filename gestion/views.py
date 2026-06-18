from django.shortcuts import render
from .models import Indicadores

def lista_indicadores_publica(request):
    # Cogemos todos los registros de la tabla en la base de datos
    todos_los_indicadores = Indicadores.objects.all()
    
    # Se los mandamos a una página web que llamaremos 'lista.html'
    return render(request, 'gestion/lista.html', {'indicadores': todos_los_indicadores})
