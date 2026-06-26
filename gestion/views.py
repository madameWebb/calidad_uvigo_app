from django.shortcuts import render, get_object_or_404
from django.apps import apps

# Modelos que se muestran en el área pública, y el nombre legible que verá el usuario
MODELOS_PUBLICOS = {
    'responsables': 'Responsables',
    'seguimentos': 'Seguimentos dos centros',
    'seguimentosTitulos': 'Seguimentos dos títulos',
    'codigos': 'Códigos',
}


def index(request):
    tablas = [
        {'slug': slug, 'nome': nome}
        for slug, nome in MODELOS_PUBLICOS.items()
    ]
    return render(request, 'gestion/index.html', {'tablas': tablas})

def listado(request, modelo):
    nome_tabla = MODELOS_PUBLICOS.get(modelo)
    if nome_tabla is None: 
        get_object_or_404(None)
    
    ModeloClase = apps.get_model('gestion', modelo)
    
    # Campos a excluir siempre
    campos_excluidos = ['id', 'creacion', 'actualizacion', 'creado_por', 'modificado_por', 'history']
    
    # Lógica especial para Centros
    if modelo == 'centros':
        campos = ['Campus', 'Código', 'Denominación', 'Dirección Web']
        objetos = ModeloClase.objects.all()
        filas = []
        for obj in objetos:
            fila = [
                obj.codigo_localizador.campus,  # Localización
                f"{obj.codigo_localizador.codigo}{obj.codigo}",  # Código concatenado
                obj.denominacion,
                obj.direccion_webb or '-'
            ]
            filas.append(fila)
    else:
        # Resto de modelos, genérico
        campos = [campo.verbose_name.capitalize() for campo in ModeloClase._meta.fields
                  if campo.name not in campos_excluidos]
        objetos = ModeloClase.objects.all()
        filas = [[getattr(obj, campo.name) for campo in ModeloClase._meta.fields
                  if campo.name not in campos_excluidos]
                 for obj in objetos]
    
    return render(request, 'gestion/listado.html', {
        'nome_tabla': nome_tabla, 
        'columnas': campos, 
        'filas': filas
    })

def indicadores_publicos(request):
    from gestion.models import Indicadores
    
    indicadores = Indicadores.objects.select_related('irpd', 'responsable').all()
    
    return render(request, 'gestion/indicadores.html', {
        'indicadores': indicadores
    })

def irpd_publicos(request):
    from gestion.models import IRPD
    
    irpds = IRPD.objects.all()
    
    return render(request, 'gestion/irpd.html', {
        'irpds': irpds
    })
def centros_publicos(request):
    from gestion.models import Centros
    
    centros = Centros.objects.select_related('codigo_localizador').all()
    
    return render(request, 'gestion/centros.html', {
        'centros': centros
    })
def titulos_publicos(request):
    from gestion.models import Titulos
    
    titulos = Titulos.objects.select_related('centro', 'centro__codigo_localizador').all()
    
    return render(request, 'gestion/titulos.html', {
        'titulos': titulos
    })