import openpyxl
from pathlib import Path
from django.core.management.base import BaseCommand
from gestion.models import Codigos

class Command(BaseCommand):
    help = 'Compara códigos plan_sigma del Excel con los ya importados'

    def add_arguments(self, parser):
        parser.add_argument('archivo', type=str, help='Ruta del archivo Excel')

    def handle(self, *args, **options):
        archivo = Path(options['archivo'])
        
        if not archivo.exists():
            self.stderr.write(f'Archivo no encontrado: {archivo}')
            return

        # Leer Excel
        wb = openpyxl.load_workbook(str(archivo), data_only=True)
        ws = wb.active
        
        plan_sigma_excel = set()
        for fila in ws.iter_rows(min_row=2, values_only=True):
            plan_sigma = fila[0]
            if plan_sigma:
                plan_sigma_excel.add(str(plan_sigma).strip())

        # Leer BD
        plan_sigma_bd = set(Codigos.objects.values_list('plan_sigma', flat=True))

        # Comparar
        en_excel_no_bd = plan_sigma_excel - plan_sigma_bd
        en_bd_no_excel = plan_sigma_bd - plan_sigma_excel

        # Guardar resultado
        salida = Path('comparar_codigos.txt')
        with open(salida, 'w', encoding='utf-8') as f:
            f.write("COMPARACIÓN DE CÓDIGOS PLAN SIGMA\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"EN EXCEL: {len(plan_sigma_excel)}\n")
            f.write(f"EN BD: {len(plan_sigma_bd)}\n\n")
            
            f.write("EN EXCEL PERO NO EN BD (falta importar):\n")
            f.write("-" * 80 + "\n")
            for codigo in sorted(en_excel_no_bd):
                f.write(f"  {codigo}\n")
            f.write(f"\nTotal: {len(en_excel_no_bd)}\n\n")
            
            f.write("EN BD PERO NO EN EXCEL (sobrante):\n")
            f.write("-" * 80 + "\n")
            for codigo in sorted(en_bd_no_excel):
                f.write(f"  {codigo}\n")
            f.write(f"\nTotal: {len(en_bd_no_excel)}\n")

        self.stdout.write(self.style.SUCCESS(f'Resultado en: {salida}'))