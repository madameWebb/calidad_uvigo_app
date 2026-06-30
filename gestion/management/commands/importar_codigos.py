import openpyxl
from pathlib import Path
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from gestion.models import Codigos, Titulos

User = get_user_model()


class Command(BaseCommand):
    help = 'Importa códigos desde el Excel de titulaciones'

    def add_arguments(self, parser):
        parser.add_argument('archivo', type=str, help='Ruta del archivo Excel')

    def traducir_a_gallego(self, nombre):
        """Traduce términos castellanos comunes a gallego"""
        traducciones = {
            'Grado': 'Grao',
            'Ambientales': 'Ambientais',
            'Ingeniería': 'Enxeñaría',
            'Enfermería': 'Enfermaría',
            'Tecnología': 'Tecnoloxía',
        }
        
        nombre_traducido = nombre.lower()
        for castellano, gallego in traducciones.items():
            nombre_traducido = nombre_traducido.replace(castellano, gallego)
        
        return nombre_traducido

    def buscar_titulo(self, nombre):
        """Busca un título por palabras clave (4+ coincidencias)"""
        # Si es PCEO, devuelve None
        if 'pceo' in nombre.lower():
            return None
        
        nombre_traducido = self.traducir_a_gallego(nombre)
        palabras_genéricas = {'máster', 'universitario', 'en', 'de', 'y', 'e', 'grao', 'programa'}
        palabras_clave = [p for p in nombre_traducido.lower().split() 
                          if len(p) > 3 and p not in palabras_genéricas]
        
        titulos = Titulos.objects.all()
        mejor_match = None
        mejor_coincidencias = 0
        
        for titulo in titulos:
            denominacion = titulo.denominacion.lower()
            coincidencias = sum(1 for palabra in palabras_clave if palabra in denominacion)
            
            if coincidencias > mejor_coincidencias:
                mejor_coincidencias = coincidencias
                mejor_match = titulo
        
        # Solo devuelve si hay 4+ coincidencias
        if mejor_coincidencias >= 4:
            return mejor_match
        
        return None

    def handle(self, *args, **options):
        archivo = Path(options['archivo'])
        
        if not archivo.exists():
            self.stderr.write(f'Archivo no encontrado: {archivo}')
            return

        usuario = User.objects.filter(is_superuser=True).first()
        if not usuario:
            self.stderr.write('No hay superusuario.')
            return

        wb = openpyxl.load_workbook(str(archivo), data_only=True)
        ws = wb.active
        
        n_codigos = 0
        n_errores = 0
        n_no_encontrados = 0

        # Leer datos desde fila 2
        for fila_num, fila in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
            try:
                # Mapeo de columnas (indices 0-based)
                plan_sigma = fila[0]           # Col 1
                estudio_sigma = fila[1]        # Col 2
                xescampus = fila[5]            # Col 6
                nombre = fila[6]               # Col 7
                ruct = fila[7]                 # Col 8

                # Validar datos
                if not plan_sigma or not nombre:
                    continue

                # Buscar título
                titulo = self.buscar_titulo(nombre)
                if not titulo:
                    self.stdout.write(self.style.WARNING(f'Fila {fila_num}: "{nombre}" no encontrado'))
                    n_no_encontrados += 1
                    continue

                # Crear código
                codigo, creado = Codigos.objects.get_or_create(
                    plan_sigma=str(plan_sigma).strip() if plan_sigma else '',
                    defaults={
                        'titulo': titulo,
                        'estudio_sigma': str(estudio_sigma).strip() if estudio_sigma else '',
                        'xescampus': str(xescampus).strip() if xescampus else '',
                        'ruct': str(ruct).strip() if ruct else '',
                        'creado_por': usuario,
                    }
                )

                if creado:
                    n_codigos += 1

            except Exception as e:
                self.stderr.write(f'Fila {fila_num}: Error - {e}')
                n_errores += 1

        self.stdout.write(self.style.SUCCESS(
            f'{n_codigos} códigos importados, {n_no_encontrados} no encontrados, {n_errores} errores'
        ))