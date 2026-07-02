import openpyxl
from pathlib import Path
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from gestion.models import Titulos, Codigos

User = get_user_model()


class Command(BaseCommand):
    help = 'Simula la importación de códigos (solo títulos sin código)'
    
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
            'Industriales': 'Industriáis',
            'Extranjera': 'Extranxeira',
            'Realidad': 'Realidade',
            'Geoespacial': 'Xeoespacial',
            'Literatura': 'Literatura',
            'Música': 'Música',
            'Gestión': 'Xestión',
            'Desarrollo': 'Desenvolvemento',
            'Sostenible': 'Sostible',
            'Nanotecnología': 'Nanotecnoloxía',
            'Institucional': 'Institucional',
            'Administración': 'Administración',
            'Dirección': 'Dirección',
            'Empresas': 'Empresas',
            'Tecnologías': 'Tecnoloxías',
            'Derecho': 'Dereito',
            'Diseño': 'Deseño',
            'Extranjeras': 'Extranxeiras',
        }
        
        nombre_traducido = nombre.lower()
        for castellano, gallego in traducciones.items():
            nombre_traducido = nombre_traducido.replace(castellano.lower(), gallego.lower())
        
        return nombre_traducido

    def buscar_titulo(self, nombre, centro_nombre):
        """Busca un título por palabras clave Y centro"""
        nombre_traducido = self.traducir_a_gallego(nombre)
        palabras_genéricas = {'en', 'de', 'y', 'e''Grado', 'Grao', 'Máster', 'Universitario'}
        palabras_clave = [p for p in nombre_traducido.lower().split() 
                        if len(p) > 3 and p not in palabras_genéricas]
        
        # Filtrar por centro primero
        from gestion.models import Centros
        centro = Centros.objects.filter(denominacion__icontains=centro_nombre).first()
        
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
        
        if mejor_coincidencias >= 1:
            return mejor_match
        
        return None
    
    def add_arguments(self, parser):
        parser.add_argument('archivo', type=str, help='Ruta del archivo Excel')

    def handle(self, *args, **options):
        archivo = Path(options['archivo'])
        
        if not archivo.exists():
            self.stderr.write(f'Archivo no encontrado: {archivo}')
            return

        # Títulos que YA tienen código
        titulos_con_codigo = set(Codigos.objects.values_list('titulo_id', flat=True))

        wb = openpyxl.load_workbook(str(archivo), data_only=True)
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
                    xescampus = fila[5]
                    nombre = fila[6]
                    ruct = fila[7]

                    if not plan_sigma or not nombre:
                        continue
                    
                    centro_nombre = fila[4]  # Columna 5 (Centro)
                    titulo = self.buscar_titulo(nombre, centro_nombre)
                    
                    if not titulo:
                        f.write(f"? Fila {fila_num}: Título '{nombre}' NO ENCONTRADO\n\n")
                        n_no_encontrados += 1
                        continue
                    
                    # Comprobar si YA tiene código por ID
                    if titulo.id in titulos_con_codigo:
                        f.write(f"✗ Fila {fila_num}: Título ID {titulo.id} YA TIENE CÓDIGO\n\n")
                        n_saltados += 1
                        continue
                    
                    # Es nuevo
                    f.write(f"✓ Fila {fila_num}:\n")
                    f.write(f"  Plan SIGMA: {plan_sigma}\n")
                    f.write(f"  Estudio SIGMA: {estudio_sigma}\n")
                    f.write(f"  Nombre: {nombre}\n")
                    f.write(f"  Título: {titulo.denominacion} (ID: {titulo.id})\n")
                    f.write(f"  Xescampus: {xescampus}\n")
                    f.write(f"  RUCT: {ruct}\n")
                    f.write("\n")
                    n_nuevos += 1

                except Exception as e:
                    f.write(f"✗ Fila {fila_num}: Error - {e}\n\n")

            f.write("=" * 80 + "\n")
            f.write(f"RESUMEN: {n_nuevos} nuevos, {n_saltados} ya existentes, {n_no_encontrados} no encontrados\n")

        self.stdout.write(self.style.SUCCESS(f'Resultado guardado en: {salida}'))