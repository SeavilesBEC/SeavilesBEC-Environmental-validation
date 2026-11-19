"""
validadorAmbiental.py
Responsable de orquestar la validación ambiental para ACCIONA Concesiones.
- Recorre los activos (proyectos) del histórico.
- Lee y normaliza los datos completos y de emisiones.
- Invoca al motor de control de datos (ControlDato).
- Agrega los resultados consolidados de revisiones.
"""

from pathlib import Path
import pandas as pd

from config import DATOS_HISTORICOS
from normalizador import normalizar_datos_completos, normalizar_emisiones
from controlDato import ControlDato


# =====================================
# BÚSQUEDA DE ACTIVOS
# =====================================

def obtener_activos() -> list:
    """Busca y lista todas las carpetas de proyectos dentro del histórico."""
    activos = []

    if not DATOS_HISTORICOS.exists():
        print(f"⚠️ No existe la ruta de histórico: {DATOS_HISTORICOS}")
        return activos

    for carpeta_anio in DATOS_HISTORICOS.iterdir():
        if not carpeta_anio.is_dir():
            continue
        for carpeta_proyecto in carpeta_anio.iterdir():
            if carpeta_proyecto.is_dir():
                activos.append(carpeta_proyecto)

    return activos


# =====================================
# VALIDACIÓN POR ACTIVO Y ORIGEN
# =====================================

def validar_datos_completos(carpeta_proyecto: Path, historico_descargas: list = None) -> pd.DataFrame:
    fichero = carpeta_proyecto / "datos_completos.xlsx"
    if not fichero.exists():
        return pd.DataFrame()

    try:
        df = pd.read_excel(fichero)
        if df.empty:
            return pd.DataFrame()

        df_norm = normalizar_datos_completos(df)
        if 'CodigoNegocio' not in df_norm.columns:
            df_norm['CodigoNegocio'] = carpeta_proyecto.name

        motor = ControlDato(df_norm, historico_descargas=historico_descargas)
        return motor.ejecutar_revisiones()
    except Exception as e:
        print(f"❌ Error en datos_completos de {carpeta_proyecto.name}: {e}")
        return pd.DataFrame()


def validar_emisiones(carpeta_proyecto: Path, historico_descargas: list = None) -> pd.DataFrame:
    fichero = carpeta_proyecto / "emisiones.xlsx"
    if not fichero.exists():
        return pd.DataFrame()

    try:
        df = pd.read_excel(fichero)
        if df.empty:
            return pd.DataFrame()

        df_val = df.copy()
        if "Gross_tCO2e" in df_val.columns and "Cantidad" not in df_val.columns:
            df_val["Cantidad"] = df_val["Gross_tCO2e"]
        if "Recurso" in df_val.columns and "KPI" not in df_val.columns:
            df_val["KPI"] = df_val["Recurso"]

        df_norm = normalizar_emisiones(df_val)
        if 'CodigoNegocio' not in df_norm.columns:
            df_norm['CodigoNegocio'] = carpeta_proyecto.name

        motor = ControlDato(df_norm, historico_descargas=historico_descargas)
        return motor.ejecutar_revisiones()
    except Exception as e:
        print(f"❌ Error en emisiones de {carpeta_proyecto.name}: {e}")
        return pd.DataFrame()


def validar_activo(carpeta_proyecto: Path, historico_descargas: list = None) -> pd.DataFrame:
    """
    Carga, normaliza y ejecuta el motor de control sobre los datos ambientales 
    y de emisiones de un activo específico.
    """
    resultados = []

    df_rev_datos = validar_datos_completos(carpeta_proyecto, historico_descargas)
    if not df_rev_datos.empty:
        resultados.append(df_rev_datos)

    df_rev_emis = validar_emisiones(carpeta_proyecto, historico_descargas)
    if not df_rev_emis.empty:
        resultados.append(df_rev_emis)

    if not resultados:
        return pd.DataFrame()

    return pd.concat(resultados, ignore_index=True)


# =====================================
# RESUMEN EN CONSOLA
# =====================================

def imprimir_resumen_validacion(activos_totales: int, activos_con_revisiones: int, total_revisiones: int):
    """Muestra un resumen limpio y orientado a negocio en consola."""
    print()
    print("=" * 60)
    print("RESUMEN DE VALIDACIÓN AMBIENTAL")
    print("=" * 60)
    print(f"Activos revisados: {activos_totales}")
    print(f"Activos con incidencias a revisar: {activos_con_revisiones}")
    print(f"Total de revisiones generadas: {total_revisiones}")
    print("=" * 60)
    print()


# =====================================
# VALIDACIÓN GLOBAL (ORQUESTADOR)
# =====================================

def ejecutar_validacion_historico(historico_descargas: list = None) -> pd.DataFrame:
    """Orquesta la validación de todos los activos encontrados en el histórico."""
    activos = obtener_activos()
    print(f"\n📁 Activos encontrados en el histórico: {len(activos)}")

    if not activos:
        return pd.DataFrame()

    resultados = []
    activos_con_incidencias = 0

    for activo in activos:
        print(f"   -> Validando activo: {activo.name}...")
        
        df_rev = validar_activo(activo, historico_descargas=historico_descargas)

        if not df_rev.empty:
            activos_con_incidencias += 1
            resultados.append(df_rev)
            print(f"      [!] {len(df_rev)} revisiones recomendadas.")
        else:
            print("      [OK] Sin incidencias detectadas.")

    if not resultados:
        imprimir_resumen_validacion(len(activos), 0, 0)
        return pd.DataFrame()

    df_revisiones_final = pd.concat(resultados, ignore_index=True)
    
    imprimir_resumen_validacion(
        len(activos),
        activos_con_incidencias,
        len(df_revisiones_final)
    )

    return df_revisiones_final


# =====================================
# TEST LOCAL
# =====================================

if __name__ == "__main__":
    print("🧪 Ejecutando test local de validadorAmbiental.py...")
    df_resultado = ejecutar_validacion_historico()
    print(f"🏁 Proceso finalizado. Total revisiones obtenidas: {len(df_resultado)}")