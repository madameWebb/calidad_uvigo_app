from django.shortcuts import render, get_object_or_404
from django.apps import apps

# Modelos que se muestran en el área pública, y el nombre legible que verá el usuario
MODELOS_PUBLICOS = {
    'indicadores': 'Indicadores',
    'irpd': 'IRPD',
    'centros': 'Centros',
    'localizadores': 'Localizadores',
    'responsables': 'Responsables',
    'seguimentos': 'Seguimentos',
    'titulos': 'Títulos',
    'codigos': 'Códigos',
}


def index(request):
    tablas = [
        {'slug': slug, 'nome': nome}
        for slug, nome in MODELOS_PUBLICOS.items()
    ]
    return render(request, 'gestion/index.html', {'tablas': tablas})


def listado(request, modelo):
    # Comprobamos que el modelo pedido está en nuestra lista permitida
    nome_tabla = MODELOS_PUBLICOS.get(modelo)
    if nome_tabla is None:
        get_object_or_404(None)  # fuerza un 404 si alguien pide algo no permitido

    # Obtenemos la clase del modelo real (ej: 'indicadores' -> Indicadores)
    ModeloClase = apps.get_model('gestion', modelo)

    # Sacamos los nombres de los campos "normales" (sin contar relaciones inversas, etc.)
    campos = [
        campo.verbose_name.capitalize()
        for campo in ModeloClase._meta.fields
        if campo.name not in ['creado_por', 'modificado_por', 'history']
    ]

    objetos = ModeloClase.objects.all()

    filas = []
    for obj in objetos:
        fila = [
            getattr(obj, campo.name)
            for campo in ModeloClase._meta.fields
            if campo.name not in ['creado_por', 'modificado_por', 'history']
        ]
        filas.append(fila)

    return render(request, 'gestion/listado.html', {
        'nome_tabla': nome_tabla,
        'columnas': campos,
        'filas': filas,
    })

