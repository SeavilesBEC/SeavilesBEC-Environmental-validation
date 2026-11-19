"""
exportadorValidacion.py
Genera el cuaderno de revisión ambiental para ACCIONA Concesiones.
Responsabilidad única: Exportar los resultados del motor de control a Excel 
sin incluir lógica de negocio ni validaciones.
"""

from datetime import datetime
from pathlib import Path
from typing import Union, Optional
import pandas as pd


def exportar_cuaderno_revision(df_revisiones: pd.DataFrame, ruta_salida: Union[str, Path] = "VALIDACION_AMBIENTAL.xlsx") -> None:
    """
    Genera el archivo Excel 'VALIDACION_AMBIENTAL.xlsx' estructurado en:
    - Hoja RESUMEN: Proyecto, Centro, Número de revisiones.
    - Hojas por Proyecto: Detalle completo de incidencias listas para revisión humana.
    
    Args:
        df_revisiones (pd.DataFrame): DataFrame con el resultado de controlDato.py
        ruta_salida (str | Path): Ruta de destino del archivo Excel generado.
    """
    if df_revisiones is None or df_revisiones.empty:
        print("ℹ️ No existen revisiones pendientes para exportar en este ciclo.")
        return

    # Columnas contractuales exigidas por el modelo de datos de revisión
    columnas_requeridas = [
        'Proyecto', 'Centro', 'Regla', 'Categoria', 'TipoDato', 
        'KPI', 'Periodo', 'Valor', 'ValorReferencia', 'Observacion', 
        'Accion', 'Estado', 'ComentarioUsuario'
    ]

    # Asegurar que todas las columnas existan en el DataFrame de entrada
    df = df_revisiones.copy()
    for col in columnas_requeridas:
        if col not in df.columns:
            if col == 'Estado':
                df[col] = 'Pendiente'
            elif col == 'ComentarioUsuario':
                df[col] = ''
            else:
                df[col] = 'N/D'

    df = df[columnas_requeridas]

    # Escritura del cuaderno de revisión Excel
    try:
        with pd.ExcelWriter(ruta_salida, engine="openpyxl") as writer:
            
            # 1. Hoja RESUMEN corporativa
            resumen = (
                df.groupby(['Proyecto', 'Centro'])
                .size()
                .reset_index(name='NumeroDeRevisiones')
                .sort_values(by=['Proyecto', 'Centro'], ascending=[True, True])
            )
            resumen.to_excel(writer, sheet_name="RESUMEN", index=False)

            # 2. Hoja por Proyecto
            proyectos = df['Proyecto'].unique()
            for proyecto in proyectos:
                # Limpiar nombre de hoja para cumplir restricciones de Excel (máx 31 caracteres, sin caracteres prohibidos)
                nombre_hoja = str(proyecto)[:31].replace('/', '_').replace('\\', '_').replace('*', '_')
                
                df_proyecto = df[df['Proyecto'] == proyecto]
                df_proyecto.to_excel(writer, sheet_name=nombre_hoja, index=False)

        print(f"✅ Cuaderno de revisión generado con éxito en: {Path(ruta_salida).resolve()}")

    except Exception as e:
        print(f"❌ Error crítico al generar el fichero Excel de validación: {e}")
        raise e
