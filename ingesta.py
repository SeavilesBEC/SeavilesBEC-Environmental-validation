from pathlib import Path

import pandas as pd

from config import (
    MINERVA,
    DATOS_HISTORICOS
)

from lectorExcel import (
    leer_archivo_completo
)

from normalizador import (
    normalizar_datos_completos,
    normalizar_emisiones
)


print(f"MINERVA: {MINERVA}")
print(f"EXISTE: {MINERVA.exists()}")


# ======================================
# CLAVES DE DUPLICADOS
# ======================================

COLUMNAS_CLAVE_DATOS = [
    "IdCentro",
    "CodigoNegocio",
    "Periodo",
    "Tipo_Dato",
    "idKPI",
    "Cantidad"
]


COLUMNAS_CLAVE_EMISIONES = [
    "IdCentro",
    "CodigoNegocio",
    "Periodo",
    "Alcance",
    "Recurso",
    "Gross_Resource_Amount_Unit"
]


# ======================================
# ARCHIVOS MINERVA
# ======================================

def obtener_archivos_minerva():

    return list(
        MINERVA.rglob("*.xlsx")
    )


# ======================================
# CARGA DE DATOS
# ======================================

def cargar_datos():

    datos_completos = []

    emisiones = []

    archivos = obtener_archivos_minerva()

    print(
        f"Archivos encontrados: {len(archivos)}"
    )

    for archivo in archivos:

        print(
            f"Leyendo {archivo.name}"
        )

        try:

            (
                df_datos,
                df_emisiones
            ) = leer_archivo_completo(
                archivo
            )

            df_datos = (
                normalizar_datos_completos(
                    df_datos
                )
            )

            df_emisiones = (
                normalizar_emisiones(
                    df_emisiones
                )
            )

            datos_completos.append(
                df_datos
            )

            emisiones.append(
                df_emisiones
            )

        except Exception as e:

            print(
                f"ERROR {archivo.name}: {e}"
            )

    if not datos_completos:

        return (
            pd.DataFrame(),
            pd.DataFrame()
        )

    return (

        pd.concat(
            datos_completos,
            ignore_index=True
        ),

        pd.concat(
            emisiones,
            ignore_index=True
        )
    )


# ======================================
# ESTRUCTURA
# ======================================

def crear_carpeta_proyecto(
    anio,
    proyecto
):

    carpeta = (
        DATOS_HISTORICOS
        / str(anio)
        / str(proyecto)
    )

    carpeta.mkdir(
        parents=True,
        exist_ok=True
    )

    return carpeta


# ======================================
# ACUMULACIÓN HISTÓRICA
# ======================================

def actualizar_fichero_historico(
    df_nuevo,
    fichero_salida,
    columnas_clave
):

    if fichero_salida.exists():

        df_existente = pd.read_excel(
            fichero_salida
        )

        df_final = pd.concat(
            [
                df_existente,
                df_nuevo
            ],
            ignore_index=True
        )

        columnas_validas = [

            c

            for c in columnas_clave

            if c in df_final.columns
        ]

        if columnas_validas:

            df_final = (
                df_final
                .drop_duplicates(
                    subset=columnas_validas
                )
            )

    else:

        df_final = (
            df_nuevo.copy()
        )

    df_final.to_excel(
        fichero_salida,
        index=False
    )

    return len(df_final)


# ======================================
# DATOS COMPLETOS
# ======================================

def procesar_datos_completos(df):

    agrupado = df.groupby(
        [
            "Año",
            "IdCentro",
            "CodigoNegocio"
        ]
    )

    for (
        anio,
        id_centro,
        proyecto
    ), datos in agrupado:

        nombre_carpeta = (
            f"{id_centro}_{proyecto}"
        )

        carpeta = crear_carpeta_proyecto(
            anio,
            nombre_carpeta
        )

        salida = (
            carpeta /
            "datos_completos.xlsx"
        )

        total = actualizar_fichero_historico(
            datos,
            salida,
            COLUMNAS_CLAVE_DATOS
        )

        print(
            f"[DATOS] "
            f"{nombre_carpeta} "
            f"({anio}) -> "
            f"{total} registros"
        )


# ======================================
# EMISIONES
# ======================================

def procesar_emisiones(df):

    agrupado = df.groupby(
        [
            "Año",
            "IdCentro",
            "CodigoNegocio"
        ]
    )

    for (
        anio,
        id_centro,
        proyecto
    ), datos in agrupado:

        nombre_carpeta = (
            f"{id_centro}_{proyecto}"
        )

        carpeta = crear_carpeta_proyecto(
            anio,
            nombre_carpeta
        )

        salida = (
            carpeta /
            "emisiones.xlsx"
        )

        total = actualizar_fichero_historico(
            datos,
            salida,
            COLUMNAS_CLAVE_EMISIONES
        )

        print(
            f"[EMISIONES] "
            f"{nombre_carpeta} "
            f"({anio}) -> "
            f"{total} registros"
        )
