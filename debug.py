import openpyxl
from pathlib import Path

archivo = Path("D:\\movido\\206 DE-02 Cadro de mando 25-26 Deseño Modificado.xlsx")

wb = openpyxl.load_workbook(str(archivo), data_only=True)
ws = wb['Centro']

print("Fila 4 completa:")
for col, celda in enumerate(ws[4], 1):
    if celda.value:
        print(f"  Col {col}: '{celda.value}'")

        