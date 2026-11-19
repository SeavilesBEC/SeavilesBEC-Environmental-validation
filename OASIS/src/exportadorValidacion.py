"""
exportadorValidacion.py
Genera el cuaderno Excel de revisión ambiental para ACCIONA Concesiones.
"""
from pathlib import Path
import pandas as pd

def exportar_cuaderno_revision(df_revisiones: pd.DataFrame, ruta_salida = "VALIDACION_AMBIENTAL.xlsx") -> None:
    if df_revisiones is None or df_revisiones.empty:
        return

    columnas_requeridas = [
        'Proyecto', 'Centro', 'Regla', 'Categoria', 'TipoDato', 
        'KPI', 'Periodo', 'Valor', 'ValorReferencia', 'Observacion', 
        'Accion', 'Estado', 'ComentarioUsuario'
    ]

    df = df_revisiones.copy()
    for col in columnas_requeridas:
        if col not in df.columns:
            df[col] = 'Pendiente' if col == 'Estado' else ('' if col == 'ComentarioUsuario' else 'N/D')

    df = df[columnas_requeridas]

    with pd.ExcelWriter(ruta_salida, engine="openpyxl") as writer:
        resumen = df.groupby(['Proyecto', 'Centro']).size().reset_index(name='NumeroDeRevisiones')
        resumen.to_excel(writer, sheet_name="RESUMEN", index=False)

        for proyecto in df['Proyecto'].unique():
            nombre_hoja = str(proyecto)[:31].replace('/', '_').replace('\\', '_').replace('*', '_')
            df[df['Proyecto'] == proyecto].to_excel(writer, sheet_name=nombre_hoja, index=False)