import streamlit as st
import pandas as pd
import anthropic
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Dashboard de Ventas — Farmacia Universal",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Dashboard de Ventas con IA")
st.caption("Farmacia Universal · Análisis inteligente powered by Claude")

# ─── Datos de ventas ─────────────────────────────────────────
@st.cache_data
def cargar_datos():
    datos = [
        {'fecha':'2026-06-01','local':'Centro',    'producto':'Metformina 850mg',  'cantidad':5, 'venta':62.50},
        {'fecha':'2026-06-01','local':'Centro',    'producto':'Enalapril 10mg',    'cantidad':3, 'venta':26.70},
        {'fecha':'2026-06-01','local':'Miraflores','producto':'Atorvastatina 20mg','cantidad':8, 'venta':122.40},
        {'fecha':'2026-06-02','local':'Centro',    'producto':'Amoxicilina 500mg', 'cantidad':12,'venta':81.60},
        {'fecha':'2026-06-02','local':'Miraflores','producto':'Metformina 850mg',  'cantidad':6, 'venta':75.00},
        {'fecha':'2026-06-02','local':'Miraflores','producto':'Enalapril 10mg',    'cantidad':4, 'venta':35.60},
        {'fecha':'2026-06-03','local':'San Isidro','producto':'Atorvastatina 20mg','cantidad':10,'venta':153.00},
        {'fecha':'2026-06-03','local':'San Isidro','producto':'Amoxicilina 500mg', 'cantidad':7, 'venta':47.60},
    ]
    return pd.DataFrame(datos)

df = cargar_datos()

# ─── KPIs principales ────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Ventas", f"S/. {df['venta'].sum():.2f}", "+12%")
col2.metric("Unidades", int(df['cantidad'].sum()), "+8%")
col3.metric("Locales", df['local'].nunique())
col4.metric("Productos", df['producto'].nunique())

st.divider()

# ─── Gráficos ────────────────────────────────────────────────
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Ventas por local")
    por_local = df.groupby('local')['venta'].sum().reset_index()
    st.bar_chart(por_local.set_index('local'))

with col_right:
    st.subheader("Ventas por producto")
    por_producto = df.groupby('producto')['venta'].sum().reset_index()
    st.bar_chart(por_producto.set_index('producto'))

# ─── Tabla de datos ──────────────────────────────────────────
st.subheader("Detalle de ventas")
local_filtro = st.multiselect(
    "Filtrar por local:",
    options=df['local'].unique(),
    default=df['local'].unique()
)
df_filtrado = df[df['local'].isin(local_filtro)]
st.dataframe(df_filtrado, use_container_width=True)

# ─── Análisis con IA ─────────────────────────────────────────
st.divider()
st.subheader("🤖 Análisis con Claude")

if st.button("Generar análisis ejecutivo", type="primary"):
    resumen = df.groupby('local').agg(
        unidades=('cantidad','sum'),
        ingresos=('venta','sum')
    ).to_string()

    cliente = anthropic.Anthropic()
    with st.spinner("Claude analizando los datos..."):
        resp = cliente.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=512,
            temperature=0.2,
            system="Eres analista comercial de Farmacia Universal. Genera reportes ejecutivos concisos en español.",
            messages=[{"role":"user","content":f"Analiza estas ventas y dame 3 insights clave:\n{resumen}"}]
        )
    st.success(resp.content[0].text)