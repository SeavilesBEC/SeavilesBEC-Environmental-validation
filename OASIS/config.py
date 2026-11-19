"""
config.py
Configuración global de rutas y constantes para el proyecto OASIS.
"""
from pathlib import Path

# Constantes de la interfaz
APP_TITLE = "OASIS | Auditoría Rápida Ambiental"
APP_SUBTITLE = "ACCIONA Concesiones | Sistema de Pre-validación y Trazabilidad ESG antes de consolidación en Enablon"

# Directorio raíz del proyecto OASIS
ROOT_DIR = Path(__file__).resolve().parent

# Rutas de directorios principales y de entrada
DATOS_INPUT = ROOT_DIR / "data" / "input"
DATOS_HISTORICOS = ROOT_DIR / "data" / "historico"

# Ruta real corporativa de los ficheros de Minerva (Entrada)
MINERVA = Path(r"C:\Users\seaviles_bec\ACCIONA S.A\AC BUSINESS AREAS - SUSTAIN\07_Reporting\07.13_Automatización Enablon\Datos_MINERVA")

# Ruta corporativa exacta para los ficheros descargados tras la validación (Salida)
DATOS_SALIDA = Path(r"C:\Users\seaviles_bec\ACCIONA S.A\AC BUSINESS AREAS - SUSTAIN\07_Reporting\07.13_Automatización Enablon\Reporte_AMBIENTAL\HISTORICO_AMBIENTAL")

def crear_estructura():
    """Crea los directorios necesarios si no existen."""
    DATOS_INPUT.mkdir(parents=True, exist_ok=True)
    DATOS_SALIDA.mkdir(parents=True, exist_ok=True)
    DATOS_HISTORICOS.mkdir(parents=True, exist_ok=True)