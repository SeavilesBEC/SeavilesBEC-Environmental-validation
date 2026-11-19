"""
config.py

Configuración central del proyecto.
No deben existir rutas hardcodeadas en ningún otro módulo.
"""

from pathlib import Path
import json

# =========================
# RUTA RAÍZ DEL PROYECTO
# =========================

ROOT_DIR = Path(__file__).resolve().parent.parent
SHAREPOINT_ROOT = ROOT_DIR.parent

# =========================
# CARPETAS
# =========================

MINERVA = ROOT_DIR.parent / "Datos_MINERVA"

DATOS_HISTORICOS = ROOT_DIR / "HISTORICO_AMBIENTAL"

DATOS_SALIDA = ROOT_DIR / "DATASET_VALIDADO"

LOGS = ROOT_DIR / "logs"

POWERBI = ROOT_DIR / "powerbi"

EXCEL = ROOT_DIR / "excel"

ALERTAS = ROOT_DIR / "alertas"

CONFIG = ROOT_DIR / "config"
PROYECTO = "Validacion_Ambiental"
VERSION = "0.1.0"

# =========================
# ARCHIVOS DE SALIDA
# =========================

ARCHIVO_VALIDADO = (
    DATOS_SALIDA / "historico_ambiental_validado.xlsx"
)

ARCHIVO_ALERTAS = (
    DATOS_SALIDA / "alertas_detectadas.xlsx"
)

CATALOGO_ARCHIVOS = (
    DATOS_HISTORICOS / "catalogo_archivos.csv"
)
ARCHIVO_ALERTAS_DETALLADAS = (
    ALERTAS / "alertas_detalladas.xlsx"
)

ARCHIVO_RESUMEN_ALERTAS = (
    ALERTAS / "resumen_alertas.xlsx"
)

ARCHIVO_DASHBOARD_ALERTAS = (
    ALERTAS / "dashboard_alertas.csv"
)

ARCHIVO_HISTORICO_ALERTAS = (
    ALERTAS / "historico_alertas.csv"
)

def crear_estructura():

    carpetas = [
        MINERVA,
        DATOS_HISTORICOS,
        DATOS_SALIDA,
        LOGS,
        POWERBI,
        EXCEL,
        CONFIG
    ]

    for carpeta in carpetas:
        carpeta.mkdir(
            parents=True,
            exist_ok=True
        )


def cargar_parametros():

    archivo = CONFIG / "parametros.json"

    if not archivo.exists():
        return {}

    with open(
        archivo,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)