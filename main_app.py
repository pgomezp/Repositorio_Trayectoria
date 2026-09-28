import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.preprocessing import LabelEncoder

# --------------------------------------------------
# CONFIGURACIÓN
# --------------------------------------------------

st.set_page_config(
    page_title="Analítica Académica",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# FUNCIONES
# --------------------------------------------------

@st.cache_data
def cargar_datos(file):
    return pd.read_csv(file)


def metricas_principales(df):

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "👨‍🎓 Estudiantes",
            len(df)
        )

    with c2:
        st.metric(
            "⭐ Promedio",
            round(df["nota_final"].mean(), 2)
        )

    with c3:
        st.metric(
            "🏆 Máxima",
            round(df["nota_final"].max(), 2)
        )

    with c4:
        st.metric(
            "⚠️ Mínima",
            round(df["nota_final"].min(), 2)
        )


# --------------------------------------------------
# TÍTULO
# --------------------------------------------------

st.title("🎓 Plataforma de Analítica Académica")

st.markdown(
    """
    Dashboard interactivo para explorar,
    filtrar y analizar información académica.
    """
)

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.title("⚙️ Navegación")

archivo = st.sidebar.file_uploader(
    "Cargar archivo CSV",
    type=["csv"]
)

if archivo is None:
    st.info("Cargue un archivo CSV para comenzar.")
    st.stop()

df = cargar_datos(archivo)

# --------------------------------------------------
# FILTROS
# --------------------------------------------------

st.sidebar.markdown("---")
st.sidebar.subheader("🔍 Filtros")

participacion = st.sidebar.multiselect(
    "Participación",
    sorted(df["participacion_clase"].unique()),
    default=sorted(df["participacion_clase"].unique())
)

horario = st.sidebar.multiselect(
    "Horario",
    sorted(df["horario_estudio"].unique()),
    default=sorted(df["horario_estudio"].unique())
)

nota_min = float(df["nota_final"].min())
nota_max = float(df["nota_final"].max())

rango = st.sidebar.slider(
    "Intervalo de notas",
    nota_min,
    nota_max,
    (nota_min, nota_max)
)

df_filtrado = df[
    (df["participacion_clase"].isin(participacion))
    &
    (df["horario_estudio"].isin(horario))
    &
    (df["nota_final"] >= rango[0])
    &
    (df["nota_final"] <= rango[1])
]

# --------------------------------------------------
# MENÚ PRINCIPAL
# --------------------------------------------------

st.sidebar.markdown("---")

pagina = st.sidebar.radio(
    "📚 Seleccione una sección",
    [
        "Dashboard",
        "Explorador de Datos",
        "Participación",
        "Horarios",
        "Distribución",
        "Correlaciones",
        "Insights"
    ]
)

# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

if pagina == "Dashboard":

    st.header("📈 Dashboard Ejecutivo")

    metricas_principales(df_filtrado)

    col1, col2 = st.columns(2)

    with col1:

        fig = px.histogram(
            df_filtrado,
            x="nota_final",
            nbins=15,
            title="Distribución de Notas"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with col2:

        promedio = (
            df_filtrado.groupby(
                "participacion_clase"
            )["nota_final"]
            .mean()
            .reset_index()
        )

        fig = px.bar(
            promedio,
            x="participacion_clase",
            y="nota_final",
            color="participacion_clase",
            title="Promedio por Participación"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

# --------------------------------------------------
# EXPLORADOR
# --------------------------------------------------

elif pagina == "Explorador de Datos":

    st.header("📋 Explorador de Datos")

    busqueda = st.text_input(
        "Buscar estudiante"
    )

    datos = df_filtrado.copy()

    if busqueda:
        datos = datos[
            datos["id_estudiante"]
            .str.contains(
                busqueda,
                case=False
            )
        ]

    st.dataframe(
        datos,
        use_container_width=True
    )

    csv = datos.to_csv(index=False)

    st.download_button(
        "📥 Descargar datos filtrados",
        csv,
        "datos_filtrados.csv",
        "text/csv"
    )

# --------------------------------------------------
# PARTICIPACIÓN
# --------------------------------------------------

elif pagina == "Participación":

    st.header("🙋 Participación en Clase")

    tabla = (
        df_filtrado
        .groupby("participacion_clase")
        ["nota_final"]
        .agg(["count", "mean", "min", "max"])
        .round(2)
    )

    st.dataframe(tabla)

    fig = px.box(
        df_filtrado,
        x="participacion_clase",
        y="nota_final",
        color="participacion_clase"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# --------------------------------------------------
# HORARIOS
# --------------------------------------------------

elif pagina == "Horarios":

    st.header("⏰ Estudio por Horarios")

    tabla = (
        df_filtrado
        .groupby("horario_estudio")
        ["nota_final"]
        .agg(["count", "mean", "min", "max"])
        .round(2)
    )

    st.dataframe(tabla)

    fig = px.bar(
        df_filtrado.groupby(
            "horario_estudio"
        )["nota_final"]
        .mean()
        .reset_index(),
        x="horario_estudio",
        y="nota_final",
        color="horario_estudio"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# --------------------------------------------------
# DISTRIBUCIÓN
# --------------------------------------------------

elif pagina == "Distribución":

    st.header("📊 Distribución de Calificaciones")

    c1, c2 = st.columns(2)

    with c1:

        fig = px.histogram(
            df_filtrado,
            x="nota_final",
            nbins=20,
            marginal="box"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with c2:

        fig = px.violin(
            df_filtrado,
            y="nota_final",
            box=True
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

# --------------------------------------------------
# CORRELACIONES
# --------------------------------------------------

elif pagina == "Correlaciones":

    st.header("🔗 Correlaciones")

    df_corr = df_filtrado.copy()

    encoder = LabelEncoder()

    for col in [
        "participacion_clase",
        "horario_estudio"
    ]:

        df_corr[col] = encoder.fit_transform(
            df_corr[col]
        )

    corr = df_corr[
        [
            "participacion_clase",
            "horario_estudio",
            "nota_final"
        ]
    ].corr()

    fig = px.imshow(
        corr,
        text_auto=True,
        color_continuous_scale="Blues"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.dataframe(corr)

# --------------------------------------------------
# INSIGHTS
# --------------------------------------------------

elif pagina == "Insights":

    st.header("🧠 Insights Automáticos")

    mejor_participacion = (
        df_filtrado
        .groupby("participacion_clase")
        ["nota_final"]
        .mean()
        .idxmax()
    )

    mejor_horario = (
        df_filtrado
        .groupby("horario_estudio")
        ["nota_final"]
        .mean()
        .idxmax()
    )

    st.success(
        f"""
        ✅ Mejor nivel de participación:
        {mejor_participacion}
        """
    )

    st.success(
        f"""
        ✅ Mejor horario de estudio:
        {mejor_horario}
        """
    )

    st.info(
        f"""
        Promedio general: {df_filtrado['nota_final'].mean():.2f}
        """
    )

    st.warning(
        f"""
        Desviación estándar:
        {df_filtrado['nota_final'].std():.2f}
        """
    )

    st.dataframe(
        df_filtrado.describe().round(2)
    )

# --------------------------------------------------
# FOOTER SIDEBAR
# --------------------------------------------------

st.sidebar.markdown("---")
st.sidebar.info(
    f"Registros filtrados: {len(df_filtrado)}"
)
