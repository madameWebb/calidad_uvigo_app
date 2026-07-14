"""
views.py — Vistas públicas da aplicación Calidade UVIGO

Define todas as vistas accesibles sen autenticación. Organízanse en dous grupos:
1. Vistas de listado/consulta: mostran información de centros, títulos, indicadores, etc.
2. Vistas de detalle: mostran o seguimento dun elemento concreto nun curso académico

Convención de URLs con cursos académicos:
    Os cursos no formato '23/24' conteñen '/' que non é válido nunha URL.
    Por iso as URLs usan '-' (ex: '23-24') e as vistas converten a '/' ao recibilos.

Autor: Virginia García Álvarez
Proxecto: Prácticas DAW — Área de Calidade UVIGO
"""

from django.shortcuts import render, get_object_or_404
from django.apps import apps


# ============================================================
# CONFIGURACIÓN DE MODELOS PÚBLICOS
# ============================================================

# Dicionario de modelos accesibles na vista xenérica de listado.
# Clave: nome do modelo en Django | Valor: nome lexible para o usuario
# NOTA: Os modelos con vistas propias (Centros, Títulos, Indicadores, etc.)
# non se inclúen aquí para evitar duplicidades no menú.
MODELOS_PUBLICOS = {
    # Actualmente baleiro: todos os modelos teñen vista propia
    # Para engadir un modelo xenérico: 'NomeModelo': 'Nome para o usuario'
}


# ============================================================
# VISTA PRINCIPAL
# ============================================================

def index(request):
    """
    Páxina de inicio da área pública.
    
    Mostra o menú principal con ligazóns a todas as seccións.
    Tamén inclúe os modelos do dicionario MODELOS_PUBLICOS como ligazóns xenéricas.
    """
    tablas = [
        {'slug': slug, 'nome': nome}
        for slug, nome in MODELOS_PUBLICOS.items()
    ]
    return render(request, 'gestion/index.html', {'tablas': tablas})


# ============================================================
# VISTA XENÉRICA DE LISTADO
# ============================================================

def listado(request, modelo):
    """
    Vista xenérica para mostrar calquera modelo en formato táboa.
    
    Só mostra os modelos definidos en MODELOS_PUBLICOS.
    Para Centros aplica lóxica especial para concatenar código e localización.
    Para o resto de modelos, mostra todos os campos excepto os de auditoría.
    
    Args:
        modelo: nome do modelo Django (ex: 'Responsables')
    """
    nome_tabla = MODELOS_PUBLICOS.get(modelo)
    if nome_tabla is None:
        get_object_or_404(None)  # Devolve 404 se o modelo non está en MODELOS_PUBLICOS

    ModeloClase = apps.get_model('gestion', modelo)

    # Campos de auditoría que nunca se mostran ao usuario
    campos_excluidos = ['id', 'creacion', 'actualizacion', 'creado_por', 'modificado_por', 'history']

    if modelo == 'centros':
        # Lóxica especial para Centros: concatenar campus + código
        campos = ['Campus', 'Código', 'Denominación', 'Dirección Web']
        objetos = ModeloClase.objects.all()
        filas = []
        for obj in objetos:
            fila = [
                obj.codigo_localizador.campus,
                f"{obj.codigo_localizador.codigo}{obj.codigo}",
                obj.denominacion,
                obj.direccion_webb or '-'
            ]
            filas.append(fila)
    else:
        # Resto de modelos: mostrar todos os campos non excluídos
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


# ============================================================
# VISTAS DE INFORMACIÓN XERAL
# ============================================================

def indicadores_publicos(request):
    """
    Lista todos os indicadores de calidade con posibilidade de filtralos.
    
    Usa select_related para evitar consultas N+1 ao acceder a irpd e responsable.
    O template mostra tarxetas expandibles con código, denominación e procedemento.
    """
    from gestion.models import Indicadores
    indicadores = Indicadores.objects.select_related('irpd', 'responsable').all()
    return render(request, 'gestion/indicadores.html', {'indicadores': indicadores})


def irpd_publicos(request):
    """
    Lista todos os criterios IRPD (Informe de Revisión do Sistema pola Dirección).
    
    Mostra criterio, denominación, estándares e descrición en tarxetas expandibles.
    """
    from gestion.models import IRPD
    irpds = IRPD.objects.all()
    return render(request, 'gestion/irpd.html', {'irpds': irpds})


def centros_publicos(request):
    """
    Lista todos os centros universitarios da UVIGO.
    
    Mostra campus, código, denominación e ligazóns web en táboa con filtros.
    Usa select_related para acceder ao campus (código_localizador) eficientemente.
    """
    from gestion.models import Centros
    centros = Centros.objects.select_related('codigo_localizador').all()
    return render(request, 'gestion/centros.html', {'centros': centros})


def titulos_publicos(request):
    """
    Lista todas as titulacións da UVIGO en tarxetas expandibles.
    
    Mostra código SIGMA, denominación, tipo e información do centro.
    Inclúe ligazón ás materias avaliadas de cada titulación.
    Ao acceder con anchor (#titulo-ID), a tarxeta correspondente desprégase automaticamente.
    """
    from gestion.models import Titulos
    titulos = Titulos.objects.select_related('centro', 'centro__codigo_localizador').all()
    return render(request, 'gestion/titulos.html', {'titulos': titulos})


def responsables_publicos(request):
    """
    Lista todos os roles responsables do seguimento de indicadores, ordenados alfabeticamente.
    """
    from gestion.models import Responsables
    responsables = Responsables.objects.all().order_by('denominacion')
    return render(request, 'gestion/responsables.html', {'responsables': responsables})


# ============================================================
# VISTAS DE SEGUIMENTOS DE CENTROS
# ============================================================

def seguimentos_centros_publicos(request):
    """
    Lista todos os centros para consultar os seus seguimentos.
    
    Cada centro é clickable e abre un modal para seleccionar o curso académico.
    Despois redirixe á vista de detalle do seguimento.
    Inclúe filtros por campus e por código/denominación do centro.
    """
    from gestion.models import Centros, Localizadores
    centros = Centros.objects.select_related('codigo_localizador').all().order_by(
        'codigo_localizador__codigo', 'codigo'
    )
    localizadores = Localizadores.objects.all().order_by('campus')
    return render(request, 'gestion/seguimentos_centros.html', {
        'centros': centros,
        'localizadores': localizadores
    })


def seguimentos_centro_detalle_publicos(request, centro_id, orixe_datos):
    """
    Mostra os seguimentos dun centro concreto nun curso académico.
    
    Os seguimentos móstranse en tarxetas expandibles agrupables por tipo de indicador
    (calidade, institucional, estratéxico).
    
    Args:
        centro_id: ID do centro na base de datos
        orixe_datos: curso en formato '23-24' (convértese a '23/24' internamente)
    """
    from gestion.models import Centros, Seguimentos
    orixe_datos = orixe_datos.replace('-', '/')  # Converter formato URL a formato BD
    centro = get_object_or_404(Centros, id=centro_id)
    seguimentos = Seguimentos.objects.filter(
        centro=centro,
        orixe_datos=orixe_datos
    ).select_related('indicador', 'indicador__irpd').order_by(
        'indicador__tipo_indicador', 'indicador__codigo'
    )
    return render(request, 'gestion/seguimentos_centro_detalle.html', {
        'centro': centro,
        'orixe_datos': orixe_datos,
        'seguimentos': seguimentos
    })


# ============================================================
# VISTAS DE SEGUIMENTOS DE TÍTULOS
# ============================================================

def seguimentos_titulos_publicos(request):
    """
    Lista todas as titulacións para consultar os seus seguimentos.
    
    Inclúe filtros para agrupar por campus ou por centro.
    Cada titulación é clickable e abre un modal para seleccionar o curso.
    """
    from gestion.models import Titulos, Localizadores, Centros
    titulos = Titulos.objects.select_related(
        'centro', 'centro__codigo_localizador'
    ).all().order_by('centro__codigo_localizador__campus', 'centro__codigo', 'denominacion')
    localizadores = Localizadores.objects.all().order_by('campus')
    centros = Centros.objects.all().order_by('codigo')
    return render(request, 'gestion/seguimentos_titulos.html', {
        'titulos': titulos,
        'localizadores': localizadores,
        'centros': centros
    })


def seguimentos_titulo_detalle_publicos(request, titulo_id, orixe_datos):
    """
    Mostra os seguimentos dunha titulación concreta nun curso académico.
    
    Args:
        titulo_id: ID da titulación na base de datos
        orixe_datos: curso en formato '23-24' (convértese a '23/24' internamente)
    """
    from gestion.models import Titulos, SeguimentosTitulos
    orixe_datos = orixe_datos.replace('-', '/')
    titulo = get_object_or_404(Titulos, id=titulo_id)
    seguimentos = SeguimentosTitulos.objects.filter(
        titulo=titulo,
        orixe_datos=orixe_datos
    ).select_related('indicador', 'indicador__irpd').order_by('indicador__codigo')
    return render(request, 'gestion/seguimentos_titulo_detalle.html', {
        'titulo': titulo,
        'orixe_datos': orixe_datos,
        'seguimentos': seguimentos
    })


# ============================================================
# VISTAS DE AVALIACIÓNS DO PDI
# ============================================================

def avaliacionspdis_publicas(request):
    """
    Lista todos os centros para consultar as avaliacións do PDI.
    
    Mostra tarxetas de centros expandibles. Ao expandir, aparecen as titulacións
    do centro como ligazóns. Ao pinchar nunha titulación, vai directamente á
    páxina de detalle con todos os cursos dispoñibles.
    """
    from gestion.models import Centros
    centros = Centros.objects.select_related('codigo_localizador').prefetch_related(
        'titulos'
    ).all().order_by('codigo_localizador__codigo', 'codigo')
    return render(request, 'gestion/avaliacionspdis.html', {'centros': centros})


def avaliacionspdis_detalle(request, titulo_id):
    """
    Mostra as avaliacións do PDI dunha titulación para todos os cursos dispoñibles.
    
    A diferenza dos seguimentos (que filtran por curso), aquí móstranse todos
    os cursos nunha soa táboa horizontal para facilitar a comparación.
    
    Args:
        titulo_id: ID da titulación na base de datos
    """
    from gestion.models import Titulos, AvaliacionsPdis
    titulo = get_object_or_404(Titulos, id=titulo_id)
    avaliacions = AvaliacionsPdis.objects.filter(titulo=titulo).order_by('orixe_datos')
    return render(request, 'gestion/avaliacionspdis_detalle.html', {
        'titulo': titulo,
        'avaliacions': avaliacions,
    })


# ============================================================
# VISTAS DE MATERIAS
# ============================================================

def materias_publicas(request, titulo_id):
    """
    Lista as materias (asignaturas) dunha titulación concreta.
    
    Mostra código e nome de cada materia en táboa con filtro de busca
    e ordenamento por código ou nome.
    
    Args:
        titulo_id: ID da titulación na base de datos
    """
    from gestion.models import Titulos, MateriasAvaliadas
    titulo = get_object_or_404(Titulos, id=titulo_id)
    materias = MateriasAvaliadas.objects.filter(titulo=titulo).order_by('materia')
    return render(request, 'gestion/materias.html', {
        'titulo': titulo,
        'materias': materias,
    })


def todas_materias(request):
    """
    Lista todas as materias de todas as titulacións.
    
    Inclúe o nome da titulación como ligazón que leva á vista de títulos
    coa tarxeta da titulación correspondente xa despregada (mediante anchor #titulo-ID).
    """
    from gestion.models import MateriasAvaliadas
    materias = MateriasAvaliadas.objects.select_related('titulo').all().order_by('materia')
    return render(request, 'gestion/todas_materias.html', {'materias': materias})


# ============================================================
# VISTAS DE SEGUIMENTOS DE MATERIAS
# ============================================================

def seguimentos_materias_publicos(request):
    """
    Lista todas as materias para consultar os seus seguimentos de indicadores.
    
    Inclúe filtro por centro. Cada materia é clickable e abre un modal
    para seleccionar o curso académico.
    """
    from gestion.models import MateriasAvaliadas, Centros
    materias = MateriasAvaliadas.objects.select_related(
        'titulo', 'titulo__centro', 'titulo__centro__codigo_localizador'
    ).all().order_by('titulo__centro__codigo', 'titulo__denominacion', 'materia')
    centros = Centros.objects.all().order_by('denominacion')
    return render(request, 'gestion/seguimentos_materias.html', {
        'materias': materias,
        'centros': centros,
    })


def seguimentos_materia_detalle(request, materia_id, orixe_datos):
    """
    Mostra os seguimentos de indicadores dunha materia concreta nun curso académico.
    
    Para cada indicador mostra: meta (%), taxa (%), resultado (%) e valoración
    (conseguida / parcialmente conseguida / non conseguida / sen meta).
    
    Args:
        materia_id: ID da materia na base de datos
        orixe_datos: curso en formato '23-24' (convértese a '23/24' internamente)
    """
    from gestion.models import MateriasAvaliadas, SeguementoMaterias
    orixe_datos = orixe_datos.replace('-', '/')
    materia = get_object_or_404(MateriasAvaliadas, id=materia_id)
    seguimentos = SeguementoMaterias.objects.filter(
        materia=materia,
        orixe_datos=orixe_datos
    ).select_related('indicador')
    return render(request, 'gestion/seguimentos_materia_detalle.html', {
        'materia': materia,
        'orixe_datos': orixe_datos,
        'seguimentos': seguimentos,
    })