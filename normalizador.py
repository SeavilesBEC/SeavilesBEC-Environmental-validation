"""
normalizador.py

Estandarización de datasets ambientales.

Responsabilidades:

- Limpieza de nombres de columnas
- Conversión de tipos
- Generación de fecha
- Campos auxiliares
- Homogeneización de textos
"""

import pandas as pd
import numpy as np


# ==================================================
# MESES
# ==================================================

MAPA_MESES = {
    "Ene": 1,
    "Feb": 2,
    "Mar": 3,
    "Abr": 4,
    "May": 5,
    "Jun": 6,
    "Jul": 7,
    "Ago": 8,
    "Sep": 9,
    "Oct": 10,
    "Nov": 11,
    "Dic": 12
}


# ==================================================
# COLUMNAS NUMÉRICAS
# ==================================================

COLUMNAS_NUMERICAS_DATOS = [
    "Cantidad",
    "Cantidad_Consolidada",
    "PorcentajeIntegracion",
    "idKPI"
]

COLUMNAS_NUMERICAS_EMISIONES = [
    "Gross_Resource_Amount_Unit",
    "Consolidated_Resource_Amount_Unit",
    "Gross_tCO2e",
    "Consolidated_tCO2e"
]


# ==================================================
# LIMPIAR COLUMNAS
# ==================================================

def normalizar_columnas(df):

    df = df.copy()

    columnas = []

    for col in df.columns:

        nueva = (
            str(col)
            .strip()
            .replace(" ", "_")
            .replace("(", "")
            .replace(")", "")
            .replace("/", "_")
            .replace("-", "_")
            .replace("__", "_")
        )

        columnas.append(nueva)

    df.columns = columnas

    return df


# ==================================================
# LIMPIAR TEXTOS
# ==================================================

def limpiar_textos(df):

    df = df.copy()

    columnas_texto = df.select_dtypes(
        include=["object"]
    ).columns

    for col in columnas_texto:

        df[col] = (
            df[col]
            .astype(str)
            .str.strip()
        )

    return df


# ==================================================
# FECHA
# ==================================================

def crear_fecha(df):

    df = df.copy()

    if "Periodo" not in df.columns:

        return df

    def convertir(periodo):

        try:

            partes = str(periodo).split()

            anio = int(partes[0])

            mes = MAPA_MESES[
                partes[1]
            ]

            return pd.Timestamp(
                year=anio,
                month=mes,
                day=1
            )

        except Exception:

            return pd.NaT

    df["Fecha"] = (
        df["Periodo"]
        .apply(convertir)
    )

    if "Fecha" in df.columns:

        df["Mes"] = (
            df["Fecha"]
            .dt.month
        )

        df["Anio"] = (
            df["Fecha"]
            .dt.year
        )

    return df


# ==================================================
# NUMÉRICOS
# ==================================================

def convertir_numericos(
        df,
        columnas
):

    df = df.copy()

    for col in columnas:

        if col in df.columns:

            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            )

    return df


# ==================================================
# CAMPOS AUXILIARES
# ==================================================

def crear_campos_auxiliares(df):

    df = df.copy()

    if (
        "CodigoNegocio" in df.columns
        and
        "Periodo" in df.columns
    ):

        df["ClavePeriodo"] = (
            df["CodigoNegocio"]
            .astype(str)
            + "_"
            + df["Periodo"]
            .astype(str)
        )

    if (
        "CodigoNegocio" in df.columns
        and
        "idKPI" in df.columns
    ):

        df["ClaveKPI"] = (
            df["CodigoNegocio"]
            .astype(str)
            + "_"
            + df["idKPI"]
            .astype(str)
        )

    return df


# ==================================================
# REGLAS DE CALIDAD
# ==================================================

def crear_flags_calidad(df):

    df = df.copy()

    if "Cantidad" in df.columns:

        df["FlagCantidadNegativa"] = (
            df["Cantidad"] < 0
        )

        df["FlagCantidadNula"] = (
            df["Cantidad"].isna()
        )

        df["FlagCantidadCero"] = (
            df["Cantidad"] == 0
        )

    return df


# ==================================================
# NORMALIZAR DATOS COMPLETOS
# ==================================================

def normalizar_datos_completos(df):

    df = normalizar_columnas(df)

    df = limpiar_textos(df)

    df = crear_fecha(df)

    df = convertir_numericos(
        df,
        COLUMNAS_NUMERICAS_DATOS
    )

    df = crear_campos_auxiliares(df)

    df = crear_flags_calidad(df)

    return df


# ==================================================
# NORMALIZAR EMISIONES
# ==================================================

def normalizar_emisiones(df):

    df = normalizar_columnas(df)

    df = limpiar_textos(df)

    df = crear_fecha(df)

    df = convertir_numericos(
        df,
        COLUMNAS_NUMERICAS_EMISIONES
    )

    df = crear_campos_auxiliares(df)

    return df


# ==================================================
# INTERFAZ ÚNICA
# ==================================================

def normalizar_dataset(
        df,
        tipo
):

    tipo = tipo.lower()

    if tipo == "datos":

        return normalizar_datos_completos(
            df
        )

    elif tipo == "emisiones":

        return normalizar_emisiones(
            df
        )

    else:

        raise ValueError(
            f"Tipo no soportado: {tipo}"
        )

