"""
config/__init__.py

Exportaciones públicas del paquete de configuración.
"""

from .config import (

    # Rutas principales
    BASE_DIR,
    CONFIG_DIR,
    SRC_DIR,
    DATA_DIR,

    # Datos
    INPUT_DIR,
    OUTPUT_DIR,
    HISTORICO_DIR,
    VALIDACION_DIR,
    LOGS_DIR,

    # Compatibilidad legacy
    ROOT_DIR,
    DATOS_INPUT,
    DATOS_SALIDA,
    DATOS_HISTORICOS,
    MINERVA,
    crear_estructura,

    # Parámetros
    PARAMETROS,
    PARAMETROS_FILE,

    # Umbrales
    RATIO_ERROR_ESCALA,
    RATIO_HISTORICO,
    MESES_CONSTANTE,
    RATIO_CAMBIO_BRUSCO,
    RATIO_AGUA_VERTIDOS,

    # Reglas
    REGLAS,

    # Excel
    NOMBRE_EXCEL_VALIDACION,

    # Streamlit
    APP_TITLE,
    APP_SUBTITLE,

)

__all__ = [

    # Rutas
    "BASE_DIR",
    "CONFIG_DIR",
    "SRC_DIR",
    "DATA_DIR",

    # Carpetas de datos
    "INPUT_DIR",
    "OUTPUT_DIR",
    "HISTORICO_DIR",
    "VALIDACION_DIR",
    "LOGS_DIR",

    # Compatibilidad legacy
    "ROOT_DIR",
    "DATOS_INPUT",
    "DATOS_SALIDA",
    "DATOS_HISTORICOS",
    "MINERVA",
    "crear_estructura",

    # Configuración
    "PARAMETROS",
    "PARAMETROS_FILE",

    # Umbrales
    "RATIO_ERROR_ESCALA",
    "RATIO_HISTORICO",
    "MESES_CONSTANTE",
    "RATIO_CAMBIO_BRUSCO",
    "RATIO_AGUA_VERTIDOS",

    # Reglas
    "REGLAS",

    # Excel
    "NOMBRE_EXCEL_VALIDACION",

    # Streamlit
    "APP_TITLE",
    "APP_SUBTITLE",

]