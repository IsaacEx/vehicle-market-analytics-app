import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from pathlib import Path

# Configuracion de la pagina
st.set_page_config(page_title="Vehicle Market Analytics", layout="wide")


# Funcion de carga de datos optimizada
@st.cache_data
def load_data():
    # Leer Parquet preprocesado con engine='pyarrow'
    parquet_path = Path("data") / "vehicles_clean.parquet"
    if not parquet_path.exists():
        st.error(f"No se encontro el archivo: {parquet_path}")
        st.stop()
    return pd.read_parquet(parquet_path, engine="pyarrow")


df = load_data()

# --- Aplicacion Web con Streamlit ---
st.title("ANALISIS ESTRATEGICO DEL MERCADO DE VEHICULOS USADOS")
st.markdown(
    "Aplicacion interactiva para explorar tendencias de precios, "
    "depreciacion por kilometraje y composicion del inventario."
)

# --- KPIs principales ---
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total anuncios", f"{len(df):,}")
k2.metric("Precio mediano", f"${df['price'].median():,.0f}")
k3.metric("Kilometraje mediano", f"{df['odometer'].median():,.0f} mi")
k4.metric("Correlacion precio/mi", f"{df['price'].corr(df['odometer']):.2f}")

# --- Filtros ---
with st.expander("FILTROS DE DATOS", expanded=True):
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        y_min, y_max = int(df["model_year"].min()), int(df["model_year"].max())
        sel_year = st.slider("Rango de años del modelo", y_min, y_max, (y_min, y_max))
    with fc2:
        p_min, p_max = int(df["price"].min()), int(df["price"].max())
        sel_price = st.slider("Rango de precios ($)", p_min, p_max, (p_min, p_max))
    with fc3:
        conditions = ["Todas"] + sorted(df["condition"].unique().tolist())
        sel_cond = st.selectbox("Condicion", conditions)

df_f = df[(df["model_year"].between(*sel_year)) & (df["price"].between(*sel_price))]
if sel_cond != "Todas":
    df_f = df_f[df_f["condition"] == sel_cond]

st.caption(f"Mostrando **{len(df_f):,}** vehiculos del total de {len(df):,}")

# --- Seccion 2.1: Precios y condicion ---
st.header("DISTRIBUCION DE PRECIOS POR CONDICION")

p97 = df_f["price"].quantile(0.97)
df_plot = df_f[df_f["price"] <= p97]

fig_hist = px.histogram(
    df_plot,
    x="price",
    color="condition",
    nbins=100,
    barmode="overlay",
    title="Distribucion de precios (hasta P97)",
    labels={"price": "Precio ($)", "condition": "Condicion"},
    template="plotly_white",
)
fig_hist.update_layout(
    xaxis_title="Precio ($)",
    yaxis_title="Frecuencia",
    legend_title="Condicion",
    height=420,
)
st.plotly_chart(fig_hist, use_container_width=True)

col_a, col_b = st.columns(2)
with col_a:
    fig_box = px.box(
        df_plot,
        x="price",
        color="condition",
        title="Boxplot de precios por condicion",
        labels={"price": "Precio ($)", "condition": "Condicion"},
        template="plotly_white",
    )
    fig_box.update_layout(height=380, xaxis_title="Precio ($)")
    st.plotly_chart(fig_box, use_container_width=True)

with col_b:
    median_cond = (
        df_f.groupby("condition", observed=True)["price"]
        .median()
        .sort_values(ascending=True)
        .reset_index()
    )
    median_cond.columns = ["condition", "precio_mediano"]
    fig_med_cond = px.bar(
        median_cond,
        x="precio_mediano",
        y="condition",
        orientation="h",
        title="Precio mediano por condicion",
        labels={"precio_mediano": "Precio mediano ($)", "condition": "Condicion"},
        template="plotly_white",
        color="precio_mediano",
        color_continuous_scale=[[0, "#3B82F6"], [1, "#1E40AF"]],
    )
    fig_med_cond.update_layout(height=380, coloraxis_showscale=False)
    st.plotly_chart(fig_med_cond, use_container_width=True)

# --- Seccion 2.2: Depreciacion ---
st.header("DEPRECIACION: PRECIO VS KILOMETRAJE")

max_miles = min(int(df_plot["odometer"].max()), 300_000)
bin_edges = np.arange(0, max_miles + 1, 20_000)
df_binned = df_plot.copy()
df_binned["odometer_bin"] = pd.cut(
    df_plot["odometer"], bins=bin_edges, include_lowest=True
)

depre = (
    df_binned.groupby(["odometer_bin", "condition"], observed=True)["price"]
    .median()
    .reset_index()
)
depre["odometer_mid"] = depre["odometer_bin"].apply(lambda b: b.mid)

color_map = {
    "excellent": "#2F6ECE",
    "good": "#F1A139",
    "like new": "#32A852",
    "fair": "#A83232",
    "new": "#6B2FCE",
    "salvage": "#333333",
}

fig_depre = px.line(
    depre,
    x="odometer_mid",
    y="price",
    color="condition",
    markers=True,
    title="Curva de depreciacion: precio mediano por kilometraje y condicion",
    labels={
        "odometer_mid": "Kilometraje (millas)",
        "price": "Precio mediano ($)",
        "condition": "Condicion",
    },
    template="plotly_white",
    color_discrete_map=color_map,
)
fig_depre.update_layout(
    height=480,
    xaxis_range=[0, 300_000],
    xaxis_dtick=20_000,
    legend_title="Condicion",
)
st.plotly_chart(fig_depre, use_container_width=True)

bin_edges_dens = np.arange(0, max_miles + 1, 10_000)
df_dens = df_plot.copy()
df_dens["odo_bin"] = pd.cut(
    df_plot["odometer"], bins=bin_edges_dens, include_lowest=True
)
count_bin = (
    df_dens.groupby("odo_bin", observed=True).size().reset_index(name="anuncios")
)
count_bin["odometer_mid"] = count_bin["odo_bin"].apply(lambda b: b.mid)

fig_dens = px.bar(
    count_bin,
    x="odometer_mid",
    y="anuncios",
    title="Concentracion de oferta por kilometraje",
    labels={"odometer_mid": "Kilometraje (millas)", "anuncios": "N de anuncios"},
    template="plotly_white",
    color_discrete_sequence=["#2F6ECE"],
)
fig_dens.update_layout(height=360, xaxis_dtick=20_000, showlegend=False)
st.plotly_chart(fig_dens, use_container_width=True)

# --- Seccion 2.3: Nichos de inventario ---
st.header("COMPOSICION DEL INVENTARIO Y VALOR POR SEGMENTO")

col_1, col_2 = st.columns(2)

with col_1:
    count_type = df_f["type"].value_counts().reset_index()
    count_type.columns = ["type", "anuncios"]
    count_type = count_type.sort_values("anuncios", ascending=True)
    fig_top = px.bar(
        count_type,
        x="anuncios",
        y="type",
        orientation="h",
        title="Tipos de vehiculos mas anunciados",
        labels={"anuncios": "N de anuncios", "type": "Tipo"},
        template="plotly_white",
        color="anuncios",
        color_continuous_scale=[[0, "#3B82F6"], [1, "#1E40AF"]],
    )
    fig_top.update_layout(height=400, coloraxis_showscale=False)
    st.plotly_chart(fig_top, use_container_width=True)

with col_2:
    med_type = (
        df_f.groupby("type", observed=True)["price"]
        .median()
        .sort_values(ascending=True)
        .reset_index()
    )
    med_type.columns = ["type", "precio_mediano"]
    fig_med = px.bar(
        med_type,
        x="precio_mediano",
        y="type",
        orientation="h",
        title="Precio mediano por tipo de vehiculo",
        labels={"precio_mediano": "Precio mediano ($)", "type": "Tipo"},
        template="plotly_white",
        color="precio_mediano",
        color_continuous_scale=[[0, "#3B82F6"], [1, "#1E40AF"]],
    )
    fig_med.update_layout(height=400, coloraxis_showscale=False)
    st.plotly_chart(fig_med, use_container_width=True)

top5 = df_f["type"].value_counts().nlargest(5).index.tolist()
df_top5 = df_f[df_f["type"].isin(top5)]
pct_4wd = (
    df_top5.groupby("type", observed=True)
    .agg(total=("is_4wd", "count"), con_4wd=("is_4wd", "sum"))
    .assign(pct_4wd=lambda x: (x["con_4wd"] / x["total"] * 100).round(1))
    .reset_index()
    .sort_values("pct_4wd", ascending=True)
)
fig_4wd = px.bar(
    pct_4wd,
    x="pct_4wd",
    y="type",
    orientation="h",
    title="Porcentaje de vehiculos con traccion 4WD (top 5 tipos)",
    labels={"pct_4wd": "% con 4WD", "type": "Tipo"},
    template="plotly_white",
    text="pct_4wd",
    color="pct_4wd",
    color_continuous_scale=[[0, "#3B82F6"], [1, "#1E40AF"]],
)
fig_4wd.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
fig_4wd.update_layout(height=350, showlegend=False, coloraxis_showscale=False)
st.plotly_chart(fig_4wd, use_container_width=True)
