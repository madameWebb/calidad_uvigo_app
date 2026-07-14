import os
import django
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import openpyxl
from gestion.models import Codigos, Titulos, Centros

def main():
    archivo = input("Ruta do arquivo Excel: ").strip()
    archivo_path = Path(archivo)
    
    if not archivo_path.exists():
        print("Arquivo non encontrado")
        return

    # Leer Excel
    wb = openpyxl.load_workbook(str(archivo_path), data_only=True)
    ws = wb.active
    
    plan_sigma_excel = {}
    for fila_num, fila in enumerate(ws.iter_rows(min_row=2), start=2):
        plan_sigma = fila[0].value
        if plan_sigma:
            plan_sigma_excel[str(plan_sigma).strip()] = (fila_num, fila)

    # Leer BD
    plan_sigma_bd = set(Codigos.objects.values_list('plan_sigma', flat=True))

    # Comparar
    en_excel_no_bd = set(plan_sigma_excel.keys()) - plan_sigma_bd
    en_bd_no_excel = plan_sigma_bd - set(plan_sigma_excel.keys())

    # Títulos sin código plan_sigma
    titulos_con_codigo = set(Codigos.objects.values_list('titulo_id', flat=True))
    titulos_sin_codigo = Titulos.objects.exclude(id__in=titulos_con_codigo).order_by('denominacion')
    codigo_centro = Centros.objects.order_by('denominacion')

    # Gardar resultado
    salida = Path('comparar_codigos.txt')
    with open(salida, 'w', encoding='utf-8') as f:
        f.write("COMPARACIÓN DE CÓDIGOS PLAN SIGMA\n")
        f.write("=" * 100 + "\n\n")
        
        f.write(f"EN EXCEL: {len(plan_sigma_excel)}\n")
        f.write(f"EN BD: {len(plan_sigma_bd)}\n\n")
        
        f.write("EN EXCEL PERO NO EN BD (falta importar):\n")
        f.write("-" * 100 + "\n")
        for codigo in sorted(en_excel_no_bd):
            fila_num, fila = plan_sigma_excel[codigo]
            f.write(f"Fila {fila_num}:\n")
            f.write(f"  : {fila[0].value}, ")
            f.write(f" {fila[1].value}, ")
            f.write(f" {fila[5].value}, ")
            f.write(f" {fila[7].value}\n\n")
            f.write(f" {fila[6].value}, ")
        f.write(f"Total: {len(en_excel_no_bd)}\n\n")
        
        f.write("EN BD PERO NO EN EXCEL (sobrante):\n")
        f.write("-" * 100 + "\n")
        for codigo in sorted(en_bd_no_excel):
            f.write(f"  {codigo}\n")
        f.write(f"\nTotal: {len(en_bd_no_excel)}\n\n")

        f.write("TÍTULOS EN BD SIN CÓDIGO PLAN SIGMA:\n")
        f.write("-" * 100 + "\n")
        for titulo in titulos_sin_codigo:
            for i in codigo_centro:
                if titulo.centro == i:
                    f.write(f"  ID {titulo.id}: {titulo.denominacion}; código del centro: {i.codigo_localizador}{i.codigo}\n")
        f.write(f"\nTotal: {titulos_sin_codigo.count()}\n")

    print(f"Resultado en: {salida}")

if __name__ == '__main__':
    main()