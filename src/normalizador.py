"""
normalizador.py
Estandarización de datasets ambientales y limpieza de textos/numéricos.
"""
import pandas as pd
import numpy as np

MAPA_MESES = {
    "Ene": 1, "Feb": 2, "Mar": 3, "Abr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Ago": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dic": 12
}

COLUMNAS_NUMERICAS_DATOS = ["Cantidad", "Cantidad_Consolidada", "PorcentajeIntegracion", "idKPI"]
COLUMNAS_NUMERICAS_EMISIONES = ["Gross_Resource_Amount_Unit", "Consolidated_Resource_Amount_Unit", "Gross_tCO2e", "Consolidated_tCO2e"]

def normalizar_columnas(df):
    df = df.copy()
    df.columns = [
        str(col).strip().replace(" ", "_").replace("(", "").replace(")", "").replace("/", "_").replace("-", "_").replace("__", "_")
        for col in df.columns
    ]
    return df

def limpiar_textos(df):
    df = df.copy()
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].astype(str).str.strip()
    return df

def crear_fecha(df):
    df = df.copy()
    if "Periodo" not in df.columns:
        return df
    def convertir(periodo):
        try:
            partes = str(periodo).split()
            return pd.Timestamp(year=int(partes[0]), month=MAPA_MESES[partes[1]], day=1)
        except Exception:
            return pd.NaT
    df["Fecha"] = df["Periodo"].apply(convertir)
    if "Fecha" in df.columns:
        df["Mes"] = df["Fecha"].dt.month
        df["Anio"] = df["Fecha"].dt.year
    return df

def convertir_numericos(df, columnas):
    df = df.copy()
    for col in columnas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

def crear_campos_auxiliares(df):
    df = df.copy()
    if "CodigoNegocio" in df.columns and "Periodo" in df.columns:
        df["ClavePeriodo"] = df["CodigoNegocio"].astype(str) + "_" + df["Periodo"].astype(str)
    if "CodigoNegocio" in df.columns and "idKPI" in df.columns:
        df["ClaveKPI"] = df["CodigoNegocio"].astype(str) + "_" + df["idKPI"].astype(str)
    return df

def normalizar_datos_completos(df):
    df = normalizar_columnas(df)
    df = limpiar_textos(df)
    df = crear_fecha(df)
    df = convertir_numericos(df, COLUMNAS_NUMERICAS_DATOS)
    df = crear_campos_auxiliares(df)
    return df

def normalizar_emisiones(df):
    df = normalizar_columnas(df)
    df = limpiar_textos(df)
    df = crear_fecha(df)
    df = convertir_numericos(df, COLUMNAS_NUMERICAS_EMISIONES)
    df = crear_campos_auxiliares(df)
    return df