import openpyxl
from pathlib import Path
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from gestion.models import Titulos

User = get_user_model()


class Command(BaseCommand):
    help = 'Simula la importación de códigos (sin guardar)'
    def traducir_a_gallego(self, nombre):
        """Traduce términos castellanos comunes a gallego"""
        traducciones = {
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
            'PCEO': 'PCEO',
            'Energía': 'Enerxía',
            'Industriales': 'Industriais',
            'Extranjera': 'Extranxeira',
            'Realidad': 'Realidade',
            'Geoespacial': 'Xeoespacial',
            'Literatura': 'Literatura',
            'Música': 'Música',
            'Gestión': 'Xestión',
            'Desarrollo': 'Desenvolvemento',
            'Sostenible': 'Sostible',
            'Grado': 'Grao',
            'Máster': 'Máster',
            'Universitario': 'Universitario',
            'Nanotecnología': 'Nanotecnoloxía',
            'Institucional': 'Institucional',
        }
        
        nombre_traducido = nombre.lower()
        for castellano, gallego in traducciones.items():
            nombre_traducido = nombre_traducido.replace(castellano, gallego)
        
        return nombre_traducido


    def buscar_titulo(self, nombre):
        """Busca un título por palabras clave"""
        from gestion.models import Titulos
        
        # Si es PCEO, devuelve None por ahora
        # if 'pceo' in nombre.lower():
        #     return None
        
        nombre_traducido = self.traducir_a_gallego(nombre)
        palabras_genéricas = {'en', 'de', 'y', 'e'}
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
        if mejor_coincidencias >= 2:
            return mejor_match
        
        return None
    
    def add_arguments(self, parser):
        parser.add_argument('archivo', type=str, help='Ruta del archivo Excel')



    def handle(self, *args, **options):
        archivo = Path(options['archivo'])
        
        if not archivo.exists():
            self.stderr.write(f'Archivo no encontrado: {archivo}')
            return

        wb = openpyxl.load_workbook(str(archivo), data_only=True)
        ws = wb.active
        
        # Archivo de salida
        salida = Path('importar_codigos_preview.txt')
        with open(salida, 'w', encoding='utf-8') as f:
            f.write("VISTA PREVIA DE IMPORTACIÓN DE CÓDIGOS\n")
            f.write("=" * 80 + "\n\n")
            
            n_codigos = 0
            n_errores = 0

            # Leer datos desde fila 2
            for fila_num, fila in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                try:
                    plan_sigma = fila[0]
                    estudio_sigma = fila[1]
                    xescampus = fila[5]
                    nombre = fila[6]
                    ruct = fila[7]

                    if not plan_sigma or not nombre:
                        continue

                    # Buscar título
                    titulo = self.buscar_titulo(nombre)
                    
                    if titulo:
                        f.write(f"✓ Fila {fila_num}:\n")
                        f.write(f"  Plan SIGMA: {plan_sigma}\n")
                        f.write(f"  Estudio SIGMA: {estudio_sigma}\n")
                        f.write(f"  Nombre: {nombre}\n")
                        f.write(f"  Título encontrado: {titulo.denominacion} (ID: {titulo.id})\n")
                        f.write(f"  Xescampus: {xescampus}\n")
                        f.write(f"  RUCT: {ruct}\n")
                        f.write("\n")
                        n_codigos += 1
                    else:
                        f.write(f"✗ Fila {fila_num}: Título '{nombre}' NO ENCONTRADO\n\n")
                        n_errores += 1

                except Exception as e:
                    f.write(f"✗ Fila {fila_num}: Error - {e}\n\n")
                    n_errores += 1

            f.write("=" * 80 + "\n")
            f.write(f"RESUMEN: {n_codigos} códigos OK, {n_errores} errores\n")

        self.stdout.write(self.style.SUCCESS(f'Resultado guardado en: {salida}'))
