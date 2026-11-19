"""
config/config.py

Configuración global del proyecto OASIS.
"""

from pathlib import Path
import json


# ==========================================================
# RUTAS
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

CONFIG_DIR = BASE_DIR / "config"

SRC_DIR = BASE_DIR / "src"

DATA_DIR = BASE_DIR / "data"

INPUT_DIR = DATA_DIR / "input"

OUTPUT_DIR = DATA_DIR / "output"

HISTORICO_DIR = DATA_DIR / "historico"

VALIDACION_DIR = OUTPUT_DIR / "validacion"

LOGS_DIR = BASE_DIR / "logs"


# ==========================================================
# CREACIÓN DE CARPETAS
# ==========================================================

for carpeta in [

    DATA_DIR,

    INPUT_DIR,

    OUTPUT_DIR,

    HISTORICO_DIR,

    VALIDACION_DIR,

    LOGS_DIR

]:

    carpeta.mkdir(
        parents=True,
        exist_ok=True
    )


# ==========================================================
# FICHERO DE PARÁMETROS
# ==========================================================

PARAMETROS_FILE = (
    CONFIG_DIR
    / "parametros.json"
)

if PARAMETROS_FILE.exists():

    with open(
        PARAMETROS_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        PARAMETROS = json.load(f)

else:

    PARAMETROS = {}


# ==========================================================
# PARÁMETROS CONTROL DATO
# ==========================================================

RATIO_ERROR_ESCALA = PARAMETROS.get(
    "ratio_error_escala",
    100
)

RATIO_HISTORICO = PARAMETROS.get(
    "ratio_historico",
    20
)

MESES_CONSTANTE = PARAMETROS.get(
    "meses_constante",
    6
)

RATIO_CAMBIO_BRUSCO = PARAMETROS.get(
    "ratio_cambio_brusco",
    5
)

RATIO_AGUA_VERTIDOS = PARAMETROS.get(
    "ratio_agua_vertidos",
    2
)


# ==========================================================
# EXCEL VALIDACIÓN
# ==========================================================

NOMBRE_EXCEL_VALIDACION = (
    "VALIDACION_AMBIENTAL.xlsx"
)

# ==========================================================
# REGLAS
# ==========================================================

REGLAS = {

    "CR001":
        "Revisar posible error de unidad o decimal",

    "CR002":
        "Revisar dato muy diferente al histórico",

    "CR003":
        "Revisar valor repetido durante varios meses",

    "CR004":
        "Revisar KPI esperado no reportado",

    "CR005":
        "Revisar coherencia entre agua consumida y vertidos",

    "CR006":
        "Revisar cambio brusco respecto al periodo anterior"

}


# ==========================================================
# STREAMLIT
# ==========================================================

APP_TITLE = "OASIS"

APP_SUBTITLE = (
    "Sistema de Validación Ambiental"
)

# ==========================================
# COMPATIBILIDAD LEGACY
# ==========================================

ROOT_DIR = BASE_DIR

DATOS_INPUT = INPUT_DIR

DATOS_SALIDA = OUTPUT_DIR

DATOS_HISTORICOS = HISTORICO_DIR

MINERVA = INPUT_DIR / "MINERVA.xlsx"


def crear_estructura():
    """
    Mantiene compatibilidad con versiones anteriores.
    """

    for carpeta in [

        DATA_DIR,
        INPUT_DIR,
        OUTPUT_DIR,
        HISTORICO_DIR,
        VALIDACION_DIR,
        LOGS_DIR

    ]:

        carpeta.mkdir(
            parents=True,
            exist_ok=True
        )