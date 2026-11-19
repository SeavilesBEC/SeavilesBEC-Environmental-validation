"""
validadorAmbiental.py
Orquestador del motor de validación ambiental.
"""
from pathlib import Path
import pandas as pd

from config import DATOS_HISTORICOS
from .normalizador import normalizar_datos_completos, normalizar_emisiones
from .controlDato import ControlDato

def obtener_activos() -> list:
    activos = []
    if not DATOS_HISTORICOS.exists(): return activos
    for carpeta_anio in DATOS_HISTORICOS.iterdir():
        if not carpeta_anio.is_dir(): continue
        for carpeta_proyecto in carpeta_anio.iterdir():
            if carpeta_proyecto.is_dir(): activos.append(carpeta_proyecto)
    return activos

def validar_activo(carpeta_proyecto: Path, historico_descargas: list = None) -> pd.DataFrame:
    resultados = []
    
    # Datos completos
    fichero_d = carpeta_proyecto / "datos_completos.xlsx"
    if fichero_d.exists():
        df_d = pd.read_excel(fichero_d)
        if not df_d.empty:
            df_norm = normalizar_datos_completos(df_d)
            if 'CodigoNegocio' not in df_norm.columns: df_norm['CodigoNegocio'] = carpeta_proyecto.name
            resultados.append(ControlDato(df_norm, historico_descargas).ejecutar_revisiones())

    # Emisiones
    fichero_e = carpeta_proyecto / "emisiones.xlsx"
    if fichero_e.exists():
        df_e = pd.read_excel(fichero_e)
        if not df_e.empty:
            if "Gross_tCO2e" in df_e.columns and "Cantidad" not in df_e.columns: df_e["Cantidad"] = df_e["Gross_tCO2e"]
            if "Recurso" in df_e.columns and "KPI" not in df_e.columns: df_e["KPI"] = df_e["Recurso"]
            df_norm = normalizar_emisiones(df_e)
            if 'CodigoNegocio' not in df_norm.columns: df_norm['CodigoNegocio'] = carpeta_proyecto.name
            resultados.append(ControlDato(df_norm, historico_descargas).ejecutar_revisiones())

    return pd.concat(resultados, ignore_index=True) if resultados else pd.DataFrame()

def ejecutar_validacion_historico(historico_descargas: list = None) -> pd.DataFrame:
    activos = obtener_activos()
    if not activos: return pd.DataFrame()
    
    resultados = []
    for activo in activos:
        df_rev = validar_activo(activo, historico_descargas)
        if not df_rev.empty: resultados.append(df_rev)

    return pd.concat(resultados, ignore_index=True) if resultados else pd.DataFrame()