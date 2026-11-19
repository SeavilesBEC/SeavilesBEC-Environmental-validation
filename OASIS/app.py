"""
app.py
Interfaz gráfica de usuario de OASIS usando Streamlit.
"""
import sys
from pathlib import Path
import io
import pandas as pd
import streamlit as st

# ==========================================
# GESTIÓN DE RUTAS Y CONFIGURACIÓN
# ==========================================
RUTA_ACTUAL = Path(__file__).resolve().parent
SRC_PATH = RUTA_ACTUAL / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.append(str(SRC_PATH))

# Importación limpia y directa (asumiendo que config.py está en la carpeta config con __init__.py)
try:
    from config import DATOS_SALIDA
except ImportError:
    from config.config import DATOS_SALIDA

from src.ingesta import cargar_datos, procesar_datos_completos, procesar_emisiones
from src.validadorAmbiental import ejecutar_validacion_historico
from src.exportadorValidacion import exportar_cuaderno_revision

# ==========================================
# CONFIGURACIÓN DE PÁGINA (OASIS)
# ==========================================
st.set_page_config(
    page_title="OASIS | Auditoría Rápida Ambiental",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cabecera corporativa
st.title("🌿 OASIS — Auditoría Rápida Ambiental")
st.markdown("**ACCIONA Concesiones** | Sistema de Pre-validación y Trazabilidad ESG antes de consolidación en Enablon")
st.divider()

# ==========================================
# INICIALIZACIÓN DE ESTADO
# ==========================================
if 'df_revisiones' not in st.session_state:
    ruta_excel_previo = DATOS_SALIDA / "VALIDACION_AMBIENTAL.xlsx"
    if ruta_excel_previo.exists():
        try:
            st.session_state['df_revisiones'] = pd.read_excel(ruta_excel_previo)
        except Exception:
            st.session_state['df_revisiones'] = pd.DataFrame()
    else:
        st.session_state['df_revisiones'] = pd.DataFrame()

# ==========================================
# PANEL LATERAL: ORQUESTADOR DE PROCESOS
# ==========================================
st.sidebar.header("⚙️ Panel de Control OASIS")
st.sidebar.markdown("Ejecuta el flujo completo de ingesta desde Minerva, actualización de histórico y control de calidad.")

if st.sidebar.button("🚀 Ejecutar Nueva Validación", type="primary", use_container_width=True):
    with st.spinner("Ejecutando pipeline completo en OASIS (Ingesta, Histórico y Motor de Reglas)..."):
        try:
            print("[OASIS] Iniciando proceso de ingesta...")
            # 1. Ingesta y normalización desde Minerva
            df_datos, df_emisiones = cargar_datos()
            
            if not df_datos.empty:
                print(f"[OASIS] Procesando {len(df_datos)} registros de datos completos...")
                procesar_datos_completos(df_datos)
            if not df_emisiones.empty:
                print(f"[OASIS] Procesando {len(df_emisiones)} registros de emisiones...")
                procesar_emisiones(df_emisiones)
            
            print("[OASIS] Ejecutando motor de control y reglas...")
            # 2. Ejecución del motor de control (CR001 - CR006)
            df_revisiones = ejecutar_validacion_historico()
            
            print(f"[OASIS] Revisiones generadas: {len(df_revisiones)}")
            # 3. Exportación automática del cuaderno Excel corporativo
            if not df_revisiones.empty:
                DATOS_SALIDA.mkdir(parents=True, exist_ok=True)
                ruta_excel = DATOS_SALIDA / "VALIDACION_AMBIENTAL.xlsx"
                exportar_cuaderno_revision(df_revisiones, ruta_salida=ruta_excel)
            
            # Guardar estado en memoria para interacción inmediata
            st.session_state['df_revisiones'] = df_revisiones
            st.sidebar.success("✅ Validación completada con éxito.")
            st.rerun()  # Forzar actualización visual inmediata en Streamlit
            
        except Exception as e:
            print(f"[OASIS ERROR] {e}")
            st.sidebar.error(f"❌ Error crítico en el flujo: {e}")

df_actual = st.session_state['df_revisiones']

# ==========================================
# INTERFAZ PRINCIPAL Y REVISIÓN HUMANA
# ==========================================
if df_actual.empty:
    st.info("👋 Bienvenido a **OASIS**. No hay hallazgos pendientes de revisión o aún no has ejecutado el análisis. Pulsa **'🚀 Ejecutar Nueva Validación'** en el menú lateral para procesar los datos de Minerva.")
else:
    # --- Filtros dinámicos en barra lateral ---
    st.sidebar.divider()
    st.sidebar.subheader("🔍 Filtros de Revisión")
    
    # Filtro por Centro / Concesión
    col_centro = next((c for c in df_actual.columns if 'centro' in c.lower() or 'concesion' in c.lower()), None)
    if col_centro:
        opciones_centro = sorted(df_actual[col_centro].dropna().unique().tolist())
        sel_centro = st.sidebar.multiselect("Activo / Centro", opciones_centro, default=opciones_centro)
        df_filtrado = df_actual[df_actual[col_centro].isin(sel_centro)]
    else:
        df_filtrado = df_actual.copy()

    # Filtro por Regla (CR001 - CR006)
    col_regla = next((c for c in df_actual.columns if 'regla' in c.lower() or 'codigo' in c.lower()), None)
    if col_regla:
        opciones_regla = sorted(df_filtrado[col_regla].dropna().unique().tolist())
        sel_regla = st.sidebar.multiselect("Regla de Control", opciones_regla, default=opciones_regla)
        df_filtrado = df_filtrado[df_filtrado[col_regla].isin(sel_regla)]

    # --- KPIs Resumen ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Hallazgos Detectados", len(df_filtrado))
    
    if col_centro:
        col2.metric("Activos con Incidencias", df_filtrado[col_centro].nunique())
    if col_regla:
        col3.metric("Reglas Activadas", df_filtrado[col_regla].nunique())

    st.subheader("📋 Cuaderno de Revisión Ambiental")
    st.caption("Puedes editar directamente las columnas de validación o comentarios en la tabla antes de exportar el reporte final.")

    # Añadimos columnas de trazabilidad humana si no existen
    if "Estado_Revision" not in df_filtrado.columns:
        df_filtrado["Estado_Revision"] = "Pendiente"
    if "Comentarios_Gestor" not in df_filtrado.columns:
        df_filtrado["Comentarios_Gestor"] = ""

    # Tabla interactiva editable
    df_editado = st.data_editor(
        df_filtrado,
        use_container_width=True,
        num_rows="fixed",
        column_config={
            "Estado_Revision": st.column_config.SelectboxColumn(
                "Estado de Revisión",
                help="Selecciona el dictamen tras revisar el dato",
                options=["Pendiente", "Validado (OK)", "Falso Positivo", "Corregir en Minerva"],
                required=True,
            ),
            "Comentarios_Gestor": st.column_config.TextColumn(
                "Comentarios / Justificación ESG",
                help="Añade trazabilidad para auditoría interna"
            )
        }
    )

    # --- Botón de Descarga del Excel Revisado ---
    st.divider()
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_editado.to_excel(writer, index=False, sheet_name='Validacion_OASIS')
    
    st.download_button(
        label="📥 Descargar Cuaderno Validado (.xlsx)",
        data=buffer.getvalue(),
        file_name="OASIS_Validacion_ESG_Consolidada.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary"
    )