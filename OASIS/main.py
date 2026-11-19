"""
main.py
Pipeline completo de Validación Ambiental para ACCIONA Concesiones.

FASES:
1. Ingesta y Procesamiento de datos procedentes de Minerva.
2. Ejecución del motor de control y reglas ambientales sobre el histórico.
3. Exportación del Cuaderno de Revisión (VALIDACION_AMBIENTAL.xlsx).
"""

from datetime import datetime
import pandas as pd

from config.config import crear_estructura, DATOS_SALIDA
from src.ingesta import cargar_datos, procesar_datos_completos, procesar_emisiones
from src.validadorAmbiental import ejecutar_validacion_historico
from src.exportadorValidacion import exportar_cuaderno_revision


def mostrar_cabecera():
    print()
    print("=" * 80)
    print("SISTEMA CORPORATIVO DE VALIDACIÓN AMBIENTAL - ACCIONA CONCESIONES")
    print(f"Fecha y hora de ejecución: {datetime.now():%Y-%m-%d %H:%M:%S}")
    print("=" * 80)
    print()


def ejecutar_pipeline() -> pd.DataFrame:
    """Orquesta las fases del pipeline de validación ambiental."""
    
    # Asegurar estructura de directorios
    crear_estructura()

    # -------------------------------------------------------------
    # FASE 1: INGESTA Y PROCESAMIENTO HISTÓRICO
    # -------------------------------------------------------------
    print("[1/3] INGESTA Y PROCESAMIENTO DE DATOS MINERVA")
    print("-" * 80)
    
    df_datos, df_emisiones = cargar_datos()
    
    if df_datos.empty and df_emisiones.empty:
        raise ValueError("❌ No se encontraron datos válidos en la ingesta de Minerva.")
    
    if not df_datos.empty:
        procesar_datos_completos(df_datos)
    if not df_emisiones.empty:
        procesar_emisiones(df_emisiones)
    
    print("✅ Ingesta y almacenamiento histórico completados.")

    # -------------------------------------------------------------
    # FASE 2: MOTOR DE REVISIONES AMBIENTALES
    # -------------------------------------------------------------
    print()
    print("[2/3] EJECUCIÓN DE REGLAS DE CONTROL AMBIENTAL")
    print("-" * 80)
    
    df_revisiones = ejecutar_validacion_historico()
    print(f"✅ Motor ejecutado. Revisiones detectadas que merecen análisis: {len(df_revisiones)}")

    # -------------------------------------------------------------
    # FASE 3: EXPORTACIÓN DEL CUADERNO DE REVISIÓN
    # -------------------------------------------------------------
    print()
    print("[3/3] EXPORTACIÓN DEL CUADERNO DE REVISIÓN")
    print("-" * 80)
    
    ruta_salida_excel = DATOS_SALIDA / "VALIDACION_AMBIENTAL.xlsx"
    exportar_cuaderno_revision(df_revisiones, ruta_salida=ruta_salida_excel)
    print("✅ Exportación completada con éxito.")

    return df_revisiones


def mostrar_resumen_final(df_revisiones: pd.DataFrame):
    """Muestra un resumen en consola estructurado para el equipo técnico."""
    print()
    print("=" * 80)
    print("RESUMEN DE EJECUCIÓN DEL PIPELINE")
    print("=" * 80)
    print(f"Total de revisiones generadas para los activos: {len(df_revisiones)}")
    
    if not df_revisiones.empty and 'Regla' in df_revisiones.columns:
        print("\nDesglose de incidencias por Regla:")
        print(df_revisiones['Regla'].value_counts().to_string())
        
    print()
    print(f"Proceso finalizado correctamente. Cuaderno disponible en: {DATOS_SALIDA / 'VALIDACION_AMBIENTAL.xlsx'}")
    print("=" * 80)
    print()


def main():
    try:
        mostrar_cabecera()
        df_revisiones = ejecutar_pipeline()
        mostrar_resumen_final(df_revisiones)

    except Exception as e:
        print()
        print("=" * 80)
        print("❌ ERROR CRÍTICO EN EL PIPELINE DE VALIDACIÓN AMBIENTAL")
        print("=" * 80)
        print(f"Detalle del error: {e}")
        print("=" * 80)
        raise


if __name__ == "__main__":
    main()