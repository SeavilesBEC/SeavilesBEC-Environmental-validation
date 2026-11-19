"""
lector_excel.py
Responsable de validar archivos Excel, leer hojas del modelo Minerva y estandarizar columnas.
"""
from pathlib import Path
import pandas as pd

HOJA_DATOS = "Datos completos"
HOJA_EMISIONES = "Emisiones"

def validar_excel(ruta_excel):
    ruta_excel = Path(ruta_excel)
    if not ruta_excel.exists():
        raise FileNotFoundError(f"No existe: {ruta_excel}")
    try:
        libro = pd.ExcelFile(ruta_excel)
        hojas = libro.sheet_names
        faltantes = []
        if HOJA_DATOS not in hojas:
            faltantes.append(HOJA_DATOS)
        if HOJA_EMISIONES not in hojas:
            faltantes.append(HOJA_EMISIONES)
        if faltantes:
            raise ValueError(f"Faltan hojas: {faltantes}")
        return True
    except Exception as e:
        raise ValueError(f"Error validando {ruta_excel.name}: {e}")

def leer_archivo_completo(ruta_excel):
    validar_excel(ruta_excel)
    df_datos = pd.read_excel(ruta_excel, sheet_name=HOJA_DATOS)
    df_datos["ArchivoOrigen"] = Path(ruta_excel).name
    df_datos["HojaOrigen"] = HOJA_DATOS

    df_emisiones = pd.read_excel(ruta_excel, sheet_name=HOJA_EMISIONES)
    df_emisiones["ArchivoOrigen"] = Path(ruta_excel).name
    df_emisiones["HojaOrigen"] = HOJA_EMISIONES

    return df_datos, df_emisiones