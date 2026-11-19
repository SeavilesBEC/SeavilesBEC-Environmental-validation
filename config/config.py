from pathlib import Path

# Directorio raíz del proyecto OASIS
ROOT_DIR = Path(__file__).resolve().parent

# Rutas de directorios principales
CONFIG_DIR = ROOT_DIR / "config"
SRC_DIR = ROOT_DIR / "src"
DATOS_INPUT = ROOT_DIR / "data" / "input"
DATOS_SALIDA = ROOT_DIR / "data" / "output"
DATOS_HISTORICOS = ROOT_DIR / "data" / "historico"
MINERVA = DATOS_INPUT / "Minerva"

def crear_estructura():
    """Crea los directorios necesarios si no existen."""
    DATOS_INPUT.mkdir(parents=True, exist_ok=True)
    DATOS_SALIDA.mkdir(parents=True, exist_ok=True)
    DATOS_HISTORICOS.mkdir(parents=True, exist_ok=True)