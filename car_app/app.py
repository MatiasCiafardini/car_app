import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Configuración de la página
st.set_page_config(page_title="Car App", page_icon="🚗", layout="wide")

# Encabezado
st.header("🚗 Análisis de anuncios de coches")

# Cargar datos
@st.cache_data
def load_data():
    return pd.read_csv("vehicles_us.csv")

try:
    car_data = load_data()
    st.success(f"Datos cargados: {len(car_data):,} filas")
except FileNotFoundError:
    st.error("⚠️ No se encontró el archivo `vehicles_us.csv`. Asegúrate de colocarlo en la carpeta raíz del proyecto.")
    st.stop()

# Controles
col1, col2 = st.columns(2)
with col1:
    hist_button = st.button("Construir histograma")
with col2:
    scatter_button = st.button("Construir gráfico de dispersión")

# Histograma
if hist_button:
    st.write("### Histograma de la columna `odometer`")
    fig_hist = go.Figure(data=[go.Histogram(x=car_data["odometer"])])
    fig_hist.update_layout(
        title_text="Distribución del Odómetro",
        xaxis_title="Odómetro",
        yaxis_title="Frecuencia",
        bargap=0.05,
    )
    st.plotly_chart(fig_hist, use_container_width=True)

# Scatter
if scatter_button:
    st.write("### Scatter: `odometer` vs `price`")
    df_scatter = car_data[["odometer", "price"]].dropna()
    fig_scatter = go.Figure(
        data=[go.Scatter(
            x=df_scatter["odometer"], 
            y=df_scatter["price"], 
            mode="markers",
            opacity=0.6
        )]
    )
    fig_scatter.update_layout(
        title_text="Relación entre Odómetro y Precio",
        xaxis_title="Odómetro",
        yaxis_title="Precio"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

# Mostrar primeras filas como referencia
with st.expander("Ver primeras filas del dataset"):
    st.dataframe(car_data.head())
