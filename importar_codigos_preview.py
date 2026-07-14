"""
importar_codigos_preview.py — Preview da importación de códigos SIGMA

USO:
    python importar_codigos_preview.py

DESCRICIÓN:
    Script standalone (non é un comando Django) para previsualizar que códigos
    SIGMA se importarían desde un arquivo Excel ANTES de facer a importación real.
    
    Garda o resultado en 'importar_codigos_preview.txt' con:
    - Títulos que recibirían código novo (✓)
    - Títulos que xa teñen código asignado (✗)
    - Títulos non encontrados na BD (?)
    - Resumo con totais

WORKFLOW RECOMENDADO:
    1. Executar este script para verificar que todo é correcto
    2. Revisar 'importar_codigos_preview.txt'
    3. Se todo está ben, executar: python manage.py importar_codigos "ruta/arquivo.xlsx"

ARQUIVO EXCEL ESPERADO:
    O Excel de listado de titulacións con columnas:
    - Col 1 (fila[0]): Plan SIGMA
    - Col 2 (fila[1]): Estudio SIGMA  
    - Col 4 (fila[3]): Código do centro (localizador)
    - Col 6 (fila[5]): Código Xescampus
    - Col 7 (fila[6]): Nome da titulación (en castelán)
    - Col 8 (fila[7]): Código RUCT

BUSCA DE TÍTULOS:
    Como os nomes no Excel están en castelán e na BD están en galego,
    o script traduce os termos máis comúns antes de buscar por palabras clave.
    A busca filtra primeiro polo centro (localizador) para evitar asignar
    códigos a titulacións do mesmo nome pero doutro centro.

Autor: Virginia García Álvarez
Proxecto: Prácticas DAW — Área de Calidade UVIGO
"""

import os
import django
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import openpyxl
from gestion.models import Titulos, Codigos, Centros

# Dicionario de traducións castelán → galego para buscar títulos na BD
TRADUCCIONS = {
    'Ambientales': 'Ambientais',
    'Ingeniería': 'Enxeñaría',
    'Enfermería': 'Enfermaría',
    'Tecnología': 'Tecnoloxía',
    'Arqueología': 'Arqueoloxía',
    'Ciudades': 'Cidades',
    'Inteligencia': 'Intelixencia',
    'Bachillerato': 'Bacharelato',
    'Biotecnología': 'Biotecnoloxía',
    'Biología': 'Bioloxía',
    'Abordaje': 'Abordaxe',
    'Genética': 'Xenética',
    'Energía': 'Enerxía',
    'Industriales': 'Industriáis',
    'Extranjera': 'Extranxeira',
    'Realidad': 'Realidade',
    'Geoespacial': 'Xeoespacial',
    'Gestión': 'Xestión',
    'Desarrollo': 'Desenvolvemento',
    'Sostenible': 'Sostible',
    'Nanotecnología': 'Nanotecnoloxía',
    'Derecho': 'Dereito',
    'Diseño': 'Deseño',
    'Extranjeras': 'Extranxeiras',
    'Tecnologías': 'Tecnoloxías',
}


def traducir_a_gallego(nombre):
    """
    Traduce os termos en castelán máis comúns ao galego.
    
    Necesario porque os nomes dos títulos no Excel están en castelán
    pero na BD están en galego (importados desde os Excel do cadro de mando).
    
    Args:
        nombre: nome da titulación en castelán
        
    Returns:
        Nome traducido ao galego (en minúsculas)
    """
    nombre_traducido = nombre.lower()
    for castellano, gallego in TRADUCCIONS.items():
        nombre_traducido = nombre_traducido.replace(castellano.lower(), gallego.lower())
    return nombre_traducido


def buscar_titulo(nombre, localizador):
    """
    Busca un título na BD por palabras clave, filtrando primeiro polo centro.
    
    O localizador (código do centro no Excel) úsase para filtrar os títulos
    do centro correcto, evitando asignar códigos a titulacións con nome similar
    pero impartidas noutro centro.
    
    Palabras xenéricas excluídas da busca (non son discriminativas):
    'en', 'de', 'y', 'e', 'grado', 'grao', 'máster', 'universitario'
    
    Args:
        nombre: nome da titulación en castelán (do Excel)
        localizador: código do centro (do Excel, columna 4)
        
    Returns:
        Obxecto Titulos se se encontra con >= 1 coincidencia, None en caso contrario
    """
    nombre_traducido = traducir_a_gallego(nombre)
    palabras_genericas = {'en', 'de', 'y', 'e', 'grado', 'grao', 'máster', 'universitario'}
    palabras_clave = [p for p in nombre_traducido.lower().split()
                      if len(p) > 3 and p not in palabras_genericas]

    # Filtrar por centro se o localizador está dispoñible
    centro = Centros.objects.filter(codigo__icontains=localizador).first() if localizador else None

    if centro:
        titulos = Titulos.objects.filter(centro=centro)
    else:
        titulos = Titulos.objects.all()

    mejor_match = None
    mejor_coincidencias = 0

    for titulo in titulos:
        denominacion = titulo.denominacion.lower()
        coincidencias = sum(1 for palabra in palabras_clave if palabra in denominacion)

        if coincidencias > mejor_coincidencias:
            mejor_coincidencias = coincidencias
            mejor_match = titulo

    return mejor_match if mejor_coincidencias >= 1 else None


def main():
    archivo = input("Ruta do arquivo Excel: ").strip()
    archivo_path = Path(archivo)

    if not archivo_path.exists():
        print("Arquivo non encontrado")
        return

    # Títulos que xa teñen código asignado (para non duplicar)
    titulos_con_codigo = set(Codigos.objects.values_list('titulo_id', flat=True))

    wb = openpyxl.load_workbook(str(archivo_path), data_only=True)
    ws = wb.active

    salida = Path('importar_codigos_preview.txt')
    with open(salida, 'w', encoding='utf-8') as f:
        f.write("VISTA PREVIA: TÍTULOS SIN CÓDIGO\n")
        f.write("=" * 80 + "\n\n")

        n_nuevos = 0
        n_saltados = 0
        n_no_encontrados = 0

        for fila_num, fila in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
            try:
                plan_sigma = fila[0]
                estudio_sigma = fila[1]
                localizador = fila[3]   # Código do centro
                xescampus = fila[5]
                nombre = fila[6]        # Nome en castelán
                ruct = fila[7]

                if not plan_sigma or not nombre:
                    continue

                titulo = buscar_titulo(nombre, localizador)

                if not titulo:
                    f.write(f"? Fila {fila_num}: Título '{nombre}' NON ENCONTRADO (localizador: {localizador})\n\n")
                    n_no_encontrados += 1
                    continue

                if titulo.id in titulos_con_codigo:
                    f.write(f"✗ Fila {fila_num}: Título ID {titulo.id} XA TEN CÓDIGO\n\n")
                    n_saltados += 1
                    continue

                # Título novo que se importaría
                f.write(f"✓ Fila {fila_num}:\n")
                f.write(f"  Plan SIGMA: {plan_sigma}\n")
                f.write(f"  Estudio SIGMA: {estudio_sigma}\n")
                f.write(f"  Nome: {nombre}\n")
                f.write(f"  Título: {titulo.denominacion} (ID: {titulo.id})\n")
                f.write(f"  Localizador: {localizador}\n")
                f.write(f"  Xescampus: {xescampus}\n")
                f.write(f"  RUCT: {ruct}\n\n")
                n_nuevos += 1

            except Exception as e:
                f.write(f"✗ Fila {fila_num}: Erro - {e}\n\n")

        f.write("=" * 80 + "\n")
        f.write(f"RESUMO: {n_nuevos} novos, {n_saltados} xa existentes, {n_no_encontrados} non encontrados\n")

    print(f"Resultado en: {salida}")


if __name__ == '__main__':
    main()