import re
from decimal import Decimal, InvalidOperation
from pathlib import Path

import openpyxl
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from gestion.models import IRPD, Centros, Titulos, Indicadores, Localizadores

User = get_user_model()

REGEX_URL = re.compile(r'https?://\S+')
SHEETS_EXCLUIDAS = {'Portada', 'Centro', 'Anexos 1', 'Anexos 2', 'Anexos 3', 'Resumo', 'Procedementos'}


def extraer_url(texto):
    if not texto:
        return None
    match = REGEX_URL.search(texto)
    return match.group(0) if match else None


def limpiar_valor(valor):
    """Convierte '----', None, '' en None."""
    if valor is None:
        return None
    if isinstance(valor, str) and valor.strip() in ('----', '', '-'):
        return None
    return valor


def celda_segura(fila, indice):
    """Devuelve fila[indice] o None si esa columna no existe en la fila."""
    if indice < len(fila):
        return fila[indice]
    return None


def extraer_titulo_de_hoja(ws, nombre_hoja):
    """Extrae el nombre del título buscando 'Cadro de mando do/da ...'"""
    for fila in ws.iter_rows(max_row=5, values_only=True):
        for celda in fila:
            if celda and isinstance(celda, str) and 'Cadro de mando' in celda:
                match = re.search(r'Cadro de mando\s+d[oa]s?\s+(.+)', celda)
                if match:
                    denominacion = match.group(1).strip()
                    tipo = 'master' if denominacion.startswith('M.') or 'Máster' in denominacion or 'M. Univ' in denominacion else 'grado'
                    return denominacion, tipo
    return None, None


class Command(BaseCommand):
    help = 'Importa indicadores desde los Excel del cadro de mando (sin seguimentos)'

    def add_arguments(self, parser):
        parser.add_argument('carpeta', type=str, help='Carpeta con los Excel')

    def handle(self, *args, **options):
        carpeta = Path(options['carpeta'])
        
        usuario = User.objects.filter(is_superuser=True).first()
        if usuario is None:
            self.stderr.write('No hay superusuario...')
            return

        archivos = list(carpeta.glob('*.xlsx'))
        if not archivos:
            self.stderr.write(f'No hay archivos .xlsx en {carpeta}')
            return

        for ruta in archivos:
            self.procesar_archivo(ruta, usuario)

    def procesar_archivo(self, ruta, usuario):
        nombre_archivo = ruta.name
        match = re.match(r'^(\d)(\d+)', nombre_archivo)
        if not match:
            self.stdout.write(self.style.WARNING(f'No puedo extraer código de {nombre_archivo}'))
            return
        
        codigo_localizador = match.group(1)
        codigo_centro = match.group(2)
        localizador = Localizadores.objects.filter(codigo=codigo_localizador).first()
        
        if localizador is None:
            self.stderr.write(f'Localizador {codigo_localizador} no existe.')
            return

        centro = Centros.objects.filter(codigo=codigo_centro, codigo_localizador=localizador).first()
        if centro is None:
            self.stdout.write(self.style.WARNING(f'Centro {codigo_centro} no existe. Salto {nombre_archivo}'))
            return

        wb = openpyxl.load_workbook(str(ruta), data_only=True)
        total_indicadores = 0

        # --- Hoja "Centro" ---
        if 'Centro' in wb.sheetnames:
            n_ind = self.procesar_hoja(
                wb['Centro'], centro=centro, titulo=None, usuario=usuario
            )
            total_indicadores += n_ind

        # --- Hojas de título ---
        for nombre_hoja in wb.sheetnames:
            if nombre_hoja in SHEETS_EXCLUIDAS:
                continue

            denominacion_titulo, tipo = extraer_titulo_de_hoja(wb[nombre_hoja], nombre_hoja)
            if not denominacion_titulo:
                continue

            titulo = Titulos.objects.filter(
                centro=centro, denominacion=denominacion_titulo
            ).first()
            if titulo is None:
                continue

            n_ind = self.procesar_hoja(
                wb[nombre_hoja], centro=centro, titulo=titulo, usuario=usuario
            )
            total_indicadores += n_ind

        self.stdout.write(self.style.SUCCESS(
            f'{nombre_archivo}: {total_indicadores} indicadores'
        ))

    def procesar_hoja(self, ws, centro, titulo, usuario):
        n_indicadores = 0

        for fila in ws.iter_rows(min_row=6, values_only=True):
            if celda_segura(fila, 0) is None:
                continue

            codigo = str(celda_segura(fila, 0)).strip()
            denominacion_indicador = (celda_segura(fila, 1) or '').strip()
            denominacion = (celda_segura(fila, 2) or '').strip()
            descricion = (celda_segura(fila, 3) or '').strip()
            irpd_celda = celda_segura(fila, 4)
            fonte = extraer_url(descricion)

            if self.es_fila_categoria(fila):
                continue

            criterios = self.obtener_criterios(irpd_celda)

            for criterio in criterios:
                indicador = self.obtener_o_crear_indicador(
                    codigo, denominacion_indicador, denominacion,
                    descricion, fonte, criterio, usuario
                )

                # Asegurar el vínculo N:M
                indicador.centros.add(centro)
                if titulo:
                    indicador.titulos.add(titulo)

                n_indicadores += 1

        return n_indicadores

    def es_fila_categoria(self, fila):
        """Las filas de categoría solo tienen texto en la primera columna."""
        return (celda_segura(fila, 0) is not None and
                all(celda_segura(fila, i) is None for i in range(1, 5)))

    def obtener_criterios(self, irpd_celda):
        """Convierte '1 e 7' en [1, 7]. Si vacío, devuelve [None]."""
        if irpd_celda is None:
            return [None]
        texto = str(irpd_celda)
        numeros = re.findall(r'\d+', texto)
        if not numeros:
            return [None]
        return [int(n) for n in numeros]

    def obtener_o_crear_indicador(self, codigo, denominacion_indicador, denominacion,
                                    descricion, fonte, criterio, usuario):
        irpd_obj = None
        if criterio is not None:
            irpd_obj, _ = IRPD.objects.get_or_create(
                criterio=str(criterio),
                defaults={'denominacion': f'Criterio {criterio}', 'creado_por': usuario}
            )
        else:
            irpd_obj, _ = IRPD.objects.get_or_create(
                criterio='8',
                defaults={'denominacion': 'Sin clasificar', 'creado_por': usuario}
            )

        codigo_final = codigo
        if criterio is not None:
            existentes = Indicadores.objects.filter(codigo=codigo).exclude(irpd=irpd_obj)
            if existentes.exists():
                codigo_final = f"{codigo}-{criterio}"

        indicador, creado = Indicadores.objects.get_or_create(
            codigo=codigo_final,
            defaults={
                'denominacion_indicador': denominacion_indicador,
                'denominacion': denominacion,
                'descricion': descricion,
                'fonte': fonte,
                'irpd': irpd_obj,
                'sentido': 'positivo',
                'creado_por': usuario,
            }
        )
        return indicador