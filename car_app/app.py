import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

# ---------------------- Config & estilos ----------------------
st.set_page_config(page_title="Car App", layout="wide")

st.markdown(
    """
    <style>
      .big-metric {font-size: 28px; font-weight: 700;}
      .subtle {opacity:.8}
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------------- Data ----------------------
@st.cache_data
def load_data(path="vehicles_us.csv"):
    df = pd.read_csv(path)
    # normalizaciones útiles
    if "price" in df.columns:
        df = df[df["price"].ge(0)]  # fuera precios negativos
    return df

try:
    df = load_data()
except Exception as e:
    st.error("No se pudo cargar `vehicles_us.csv`. ¿Está en la raíz del proyecto?")
    st.stop()

# ---------------------- Sidebar (controles) ----------------------
st.sidebar.header("Controles")

# Filtros rápidos (si alguna columna no existe, se ignora silenciosamente)
cond_vals = sorted([c for c in df.get("condition", pd.Series(dtype=str)).dropna().unique()]) if "condition" in df else []
type_vals  = sorted([c for c in df.get("type", pd.Series(dtype=str)).dropna().unique()]) if "type" in df else []

cond_sel = st.sidebar.multiselect("Estado del vehículo", cond_vals, default=cond_vals[:3] if cond_vals else [])
type_sel = st.sidebar.multiselect("Tipo", type_vals, default=type_vals[:4] if type_vals else [])

odom_max = float(df["odometer"].max()) if "odometer" in df else 0
odom_range = st.sidebar.slider(
    "Rango de odómetro",
    min_value=0.0,
    max_value=odom_max if odom_max > 0 else 1.0,
    value=(0.0, odom_max if odom_max > 0 else 1.0),
    step=1000.0
)

bins = st.sidebar.slider("Bins del histograma", min_value=10, max_value=120, value=60, step=5)
use_log_price = st.sidebar.checkbox("Escala log en precio (scatter)", value=True)
show_table = st.sidebar.checkbox("Mostrar primeras filas", value=False)

# Aplicar filtros
f = df.copy()
if cond_sel and "condition" in f:
    f = f[f["condition"].isin(cond_sel)]
if type_sel and "type" in f:
    f = f[f["type"].isin(type_sel)]
if "odometer" in f:
    f = f[(f["odometer"] >= odom_range[0]) & (f["odometer"] <= odom_range[1])]

# ---------------------- Header ----------------------
st.header("Análisis de anuncios de coches")
st.success(f"Datos cargados: {len(df):,} filas  •  Filtrado actual: {len(f):,} filas")

# ---------------------- Métricas ----------------------
colA, colB, colC, colD = st.columns(4)
with colA:
    st.markdown("**Filas**")
    st.markdown(f"<div class='big-metric'>{len(f):,}</div>", unsafe_allow_html=True)
with colB:
    if "price" in f:
        st.markdown("**Precio mediano**")
        st.markdown(f"<div class='big-metric'>${int(f['price'].median()):,}</div>", unsafe_allow_html=True)
with colC:
    if "odometer" in f:
        st.markdown("**Odómetro mediano**")
        st.markdown(f"<div class='big-metric'>{int(f['odometer'].median()):,} mi</div>", unsafe_allow_html=True)
with colD:
    if "model_year" in f:
        st.markdown("**Año mediano**")
        st.markdown(f"<div class='big-metric'>{int(f['model_year'].median())}</div>", unsafe_allow_html=True)

st.markdown("<span class='subtle'>Usa la barra lateral para filtrar y ajustar los gráficos.</span>", unsafe_allow_html=True)

# ---------------------- Gráficos ----------------------
tab1, tab2 = st.tabs(["Histograma (odometer)", "Scatter (odometer vs price)"])

with tab1:
    if "odometer" not in f:
        st.info("No existe la columna `odometer` en el dataset.")
    else:
        fig_h = go.Figure()
        fig_h.add_trace(go.Histogram(x=f["odometer"], nbinsx=bins, marker_line_width=0))
        fig_h.update_layout(
            title="Distribución del Odómetro",
            xaxis_title="Odómetro",
            yaxis_title="Frecuencia",
            bargap=0.02
        )
        st.plotly_chart(fig_h, use_container_width=True)

with tab2:
    if not {"odometer", "price"}.issubset(f.columns):
        st.info("Se necesitan las columnas `odometer` y `price` para el scatter.")
    else:
        g = f[["odometer", "price", "condition"]].dropna(subset=["odometer", "price"]).copy()
        # Color opcional por condición si existe
        if "condition" in g:
            fig_s = px.scatter(
                g, x="odometer", y="price", color="condition",
                opacity=0.6, render_mode="webgl"
            )
        else:
            fig_s = px.scatter(g, x="odometer", y="price", opacity=0.6, render_mode="webgl")

        fig_s.update_layout(
            title="Odómetro vs Precio",
            xaxis_title="Odómetro",
            yaxis_title="Precio (log)" if use_log_price else "Precio"
        )
        if use_log_price:
            fig_s.update_yaxes(type="log")
        st.plotly_chart(fig_s, use_container_width=True)

# ---------------------- Tabla ----------------------
if show_table:
    st.subheader("Primeras filas del dataset filtrado")
    st.dataframe(f.head(50), use_container_width=True)
