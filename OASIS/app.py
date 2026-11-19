"""
app.py

Interfaz Streamlit de OASIS.
Toda la lógica de negocio se ejecuta desde main.py.
"""

import io

import pandas as pd
import streamlit as st

from config import (
    APP_TITLE,
    APP_SUBTITLE,
    DATOS_SALIDA
)

from main import ejecutar_pipeline


# ==================================================
# CONFIGURACIÓN STREAMLIT
# ==================================================

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==================================================
# CABECERA
# ==================================================

st.title("🌿 OASIS")

st.markdown(
    f"**{APP_SUBTITLE}**"
)

st.caption(
    "Sistema corporativo de validación ambiental para ACCIONA Concesiones"
)

st.divider()


# ==================================================
# SESSION STATE
# ==================================================

if "df_revisiones" not in st.session_state:

    ruta_excel = (
        DATOS_SALIDA
        / "VALIDACION_AMBIENTAL.xlsx"
    )

    if ruta_excel.exists():

        try:

            st.session_state.df_revisiones = (
                pd.read_excel(ruta_excel)
            )

        except Exception:

            st.session_state.df_revisiones = (
                pd.DataFrame()
            )

    else:

        st.session_state.df_revisiones = (
            pd.DataFrame()
        )


# ==================================================
# SIDEBAR
# ==================================================

st.sidebar.title("⚙️ OASIS")

st.sidebar.markdown(
    """
    Ejecuta el pipeline completo:

    - Ingesta Minerva
    - Actualización histórico
    - Motor de reglas CR
    - Exportación del cuaderno
    """
)

ejecutar = st.sidebar.button(
    "🚀 Ejecutar validación",
    use_container_width=True,
    type="primary"
)


# ==================================================
# EJECUCIÓN DEL PIPELINE
# ==================================================

if ejecutar:

    try:

        with st.spinner(
            "Ejecutando pipeline OASIS..."
        ):

            df_revisiones = (
                ejecutar_pipeline()
            )

            st.session_state.df_revisiones = (
                df_revisiones
            )

        st.success(
            f"✅ Validación completada. "
            f"{len(df_revisiones)} revisiones generadas."
        )

        st.rerun()

    except Exception as e:

        st.error(
            f"❌ Error durante la ejecución:\n{e}"
        )


# ==================================================
# RESULTADOS
# ==================================================

df = st.session_state.df_revisiones


if df.empty:

    st.info(
        """
        No existen revisiones cargadas.

        Pulsa **🚀 Ejecutar validación**
        para procesar los datos.
        """
    )

else:

    # ==================================================
    # FILTROS
    # ==================================================

    st.sidebar.divider()

    st.sidebar.subheader(
        "🔎 Filtros"
    )

    df_filtrado = df.copy()

    if "Proyecto" in df.columns:

        proyectos = sorted(
            df["Proyecto"]
            .dropna()
            .unique()
            .tolist()
        )

        proyectos_sel = (
            st.sidebar.multiselect(
                "Proyecto",
                proyectos,
                default=proyectos
            )
        )

        df_filtrado = (
            df_filtrado[
                df_filtrado["Proyecto"]
                .isin(proyectos_sel)
            ]
        )

    if "Regla" in df.columns:

        reglas = sorted(
            df_filtrado["Regla"]
            .dropna()
            .unique()
            .tolist()
        )

        reglas_sel = st.sidebar.multiselect(
            "Regla",
            reglas,
            default=reglas
        )

        df_filtrado = (
            df_filtrado[
                df_filtrado["Regla"]
                .isin(reglas_sel)
            ]
        )

    # ==================================================
    # MÉTRICAS
    # ==================================================

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Revisiones",
        len(df_filtrado)
    )

    if "Proyecto" in df_filtrado.columns:

        c2.metric(
            "Proyectos",
            df_filtrado["Proyecto"]
            .nunique()
        )

    if "Regla" in df_filtrado.columns:

        c3.metric(
            "Reglas",
            df_filtrado["Regla"]
            .nunique()
        )

    st.divider()

    # ==================================================
    # COLUMNAS DE REVISIÓN HUMANA
    # ==================================================

    if "Estado_Revision" not in df_filtrado.columns:

        df_filtrado[
            "Estado_Revision"
        ] = "Pendiente"

    if "Comentarios_Gestor" not in df_filtrado.columns:

        df_filtrado[
            "Comentarios_Gestor"
        ] = ""

    # ==================================================
    # TABLA PRINCIPAL
    # ==================================================

    st.subheader(
        "📋 Cuaderno de Revisión Ambiental"
    )

    df_editado = st.data_editor(

        df_filtrado,

        use_container_width=True,

        num_rows="fixed",

        column_config={

            "Estado_Revision":

            st.column_config.SelectboxColumn(

                "Estado",

                options=[

                    "Pendiente",

                    "Validado",

                    "Descartado",

                    "Corregir en Minerva"

                ]
            ),

            "Comentarios_Gestor":

            st.column_config.TextColumn(
                "Comentarios"
            )

        }

    )

    # ==================================================
    # DESCARGA
    # ==================================================

    st.divider()

    buffer = io.BytesIO()

    with pd.ExcelWriter(
        buffer,
        engine="openpyxl"
    ) as writer:

        df_editado.to_excel(
            writer,
            index=False,
            sheet_name="Revision"
        )

    st.download_button(

        label=
        "📥 Descargar revisión",

        data=
        buffer.getvalue(),

        file_name=
        "OASIS_VALIDACION.xlsx",

        mime=
        (
            "application/vnd.openxmlformats-"
            "officedocument.spreadsheetml.sheet"
        ),

        use_container_width=True
    )