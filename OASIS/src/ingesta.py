"""
ingesta.py
Gestión de carga y procesamiento de ficheros Minerva.
"""
from pathlib import Path
import pandas as pd

from config import MINERVA, DATOS_HISTORICOS
from .lectorExcel import leer_archivo_completo
from .normalizador import normalizar_datos_completos, normalizar_emisiones

COLUMNAS_CLAVE_DATOS = ["IdCentro", "CodigoNegocio", "Periodo", "Tipo_Dato", "idKPI", "Cantidad"]
COLUMNAS_CLAVE_EMISIONES = ["IdCentro", "CodigoNegocio", "Periodo", "Alcance", "Recurso", "Gross_Resource_Amount_Unit"]

def obtener_archivos_minerva():
    return list(MINERVA.rglob("*.xlsx")) if MINERVA.exists() else []

def cargar_datos():
    datos_completos, emisiones = [], []
    archivos = obtener_archivos_minerva()
    for archivo in archivos:
        try:
            df_d, df_e = leer_archivo_completo(archivo)
            datos_completos.append(normalizar_datos_completos(df_d))
            emisiones.append(normalizar_emisiones(df_e))
        except Exception as e:
            print(f"ERROR {archivo.name}: {e}")

    return (
        pd.concat(datos_completos, ignore_index=True) if datos_completos else pd.DataFrame(),
        pd.concat(emisiones, ignore_index=True) if emisiones else pd.DataFrame()
    )

def crear_carpeta_proyecto(anio, proyecto):
    carpeta = DATOS_HISTORICOS / str(anio) / str(proyecto)
    carpeta.mkdir(parents=True, exist_ok=True)
    return carpeta

def actualizar_fichero_historico(df_nuevo, fichero_salida, columnas_clave):
    if fichero_salida.exists():
        df_existente = pd.read_excel(fichero_salida)
        df_final = pd.concat([df_existente, df_nuevo], ignore_index=True)
        cols_validas = [c for c in columnas_clave if c in df_final.columns]
        if cols_validas:
            df_final = df_final.drop_duplicates(subset=cols_validas)
    else:
        df_final = df_nuevo.copy()
    df_final.to_excel(fichero_salida, index=False)
    return len(df_final)

def procesar_datos_completos(df):
    for (anio, id_centro, proyecto), datos in df.groupby(["Año", "IdCentro", "CodigoNegocio"]):
        nombre_carpeta = f"{id_centro}_{proyecto}"
        carpeta = crear_carpeta_proyecto(anio, nombre_carpeta)
        actualizar_fichero_historico(datos, carpeta / "datos_completos.xlsx", COLUMNAS_CLAVE_DATOS)

def procesar_emisiones(df):
    for (anio, id_centro, proyecto), datos in df.groupby(["Año", "IdCentro", "CodigoNegocio"]):
        nombre_carpeta = f"{id_centro}_{proyecto}"
        carpeta = crear_carpeta_proyecto(anio, nombre_carpeta)
        actualizar_fichero_historico(datos, carpeta / "emisiones.xlsx", COLUMNAS_CLAVE_EMISIONES)