# main.py

import pandas as pd

from OASIS.config import (
    crear_estructura,
    DATOS_SALIDA
)

from src.ingesta import (
    cargar_datos,
    procesar_datos_completos,
    procesar_emisiones
)

from src.validadorAmbiental import (
    ejecutar_validacion_historico
)

from src.exportadorValidacion import (
    exportar_cuaderno_revision
)


def ejecutar_pipeline() -> pd.DataFrame:

    crear_estructura()

    df_datos, df_emisiones = cargar_datos()

    if not df_datos.empty:

        procesar_datos_completos(
            df_datos
        )

    if not df_emisiones.empty:

        procesar_emisiones(
            df_emisiones
        )

    df_revisiones = (
        ejecutar_validacion_historico()
    )

    ruta_excel = (
        DATOS_SALIDA
        /
        "VALIDACION_AMBIENTAL.xlsx"
    )

    exportar_cuaderno_revision(
        df_revisiones,
        ruta_excel
    )

    return df_revisiones


if __name__ == "__main__":

    resultado = ejecutar_pipeline()

    print(
        f"Revisiones generadas: "
        f"{len(resultado)}"
    )