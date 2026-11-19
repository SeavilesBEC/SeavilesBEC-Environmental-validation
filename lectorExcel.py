"""
lector_excel.py

Responsable únicamente de:

- Validar archivos Excel
- Leer hojas del modelo MINERVA
- Estandarizar columnas
- Añadir metadatos de origen
"""

from pathlib import Path

import pandas as pd


# =====================================
# HOJAS OBLIGATORIAS
# =====================================

HOJA_DATOS = "Datos completos"

HOJA_EMISIONES = "Emisiones"


# =====================================
# VALIDACIÓN
# =====================================

def validar_excel(ruta_excel):

    ruta_excel = Path(ruta_excel)

    if not ruta_excel.exists():

        raise FileNotFoundError(
            f"No existe: {ruta_excel}"
        )

    try:

        libro = pd.ExcelFile(
            ruta_excel
        )

        hojas = libro.sheet_names

        faltantes = []

        if HOJA_DATOS not in hojas:
            faltantes.append(HOJA_DATOS)

        if HOJA_EMISIONES not in hojas:
            faltantes.append(HOJA_EMISIONES)

        if faltantes:

            raise ValueError(
                f"Faltan hojas: {faltantes}"
            )

        return True

    except Exception as e:

        raise ValueError(
            f"Error validando "
            f"{ruta_excel.name}: {e}"
        )


# =====================================
# LECTURA INDIVIDUAL
# =====================================

def leer_datos_completos(
        ruta_excel
):

    df = pd.read_excel(
        ruta_excel,
        sheet_name=HOJA_DATOS
    )

    df["ArchivoOrigen"] = (
        Path(ruta_excel).name
    )

    df["HojaOrigen"] = (
        HOJA_DATOS
    )

    return df


def leer_emisiones(
        ruta_excel
):

    df = pd.read_excel(
        ruta_excel,
        sheet_name=HOJA_EMISIONES
    )

    df["ArchivoOrigen"] = (
        Path(ruta_excel).name
    )

    df["HojaOrigen"] = (
        HOJA_EMISIONES
    )

    return df


# =====================================
# LECTURA COMPLETA
# =====================================

def leer_archivo_completo(
        ruta_excel
):

    validar_excel(
        ruta_excel
    )

    df_datos = (
        leer_datos_completos(
            ruta_excel
        )
    )

    df_emisiones = (
        leer_emisiones(
            ruta_excel
        )
    )

    return (
        df_datos,
        df_emisiones
    )


# =====================================
# OBTENER COLUMNAS
# =====================================

def obtener_columnas(
        ruta_excel
):

    validar_excel(
        ruta_excel
    )

    datos = pd.read_excel(
        ruta_excel,
        sheet_name=HOJA_DATOS,
        nrows=0
    )

    emisiones = pd.read_excel(
        ruta_excel,
        sheet_name=HOJA_EMISIONES,
        nrows=0
    )

    return {
        "datos_completos":
            datos.columns.tolist(),

        "emisiones":
            emisiones.columns.tolist()
    }


# =====================================
# LECTURA DE MÚLTIPLES ARCHIVOS
# =====================================

def leer_varios_archivos(
        lista_archivos
):

    datos_total = []

    emisiones_total = []

    for archivo in lista_archivos:

        try:

            df_datos, df_emisiones = (
                leer_archivo_completo(
                    archivo
                )
            )

            datos_total.append(
                df_datos
            )

            emisiones_total.append(
                df_emisiones
            )

        except Exception as e:

            print(
                f"ERROR: "
                f"{Path(archivo).name}"
            )

            print(e)

    if datos_total:

        datos_total = pd.concat(
            datos_total,
            ignore_index=True
        )

    else:

        datos_total = pd.DataFrame()

    if emisiones_total:

        emisiones_total = pd.concat(
            emisiones_total,
            ignore_index=True
        )

    else:

        emisiones_total = pd.DataFrame()

    return (
        datos_total,
        emisiones_total
    )




