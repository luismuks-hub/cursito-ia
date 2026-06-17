import streamlit as st
import anthropic
import pandas as pd
import sqlite3
import json
import os
import hashlib
from dotenv import load_dotenv

load_dotenv()

# ─── Configuracion global ────────────────────────────────────
st.set_page_config(
    page_title="Sistema de IA — Farmacia Universal",
    page_icon="💊",
    layout="wide"
)

@st.cache_resource
def get_cliente():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        st.error("API key no configurada.")
        st.stop()
    return anthropic.Anthropic(api_key=api_key)

# ─── Header principal ────────────────────────────────────────
st.title("💊 Sistema de IA — Farmacia Universal")
st.caption("Powered by Claude · Curso IA 2026 · Luis Coronel Aliaga")
st.divider()

# ─── 4 modulos en tabs ───────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📋 Asistente de Productos",
    "🎫 Clasificador de Tickets",
    "📊 Análisis de Ventas",
    "🔍 Consultor SQL"
])

# ════════════════════════════════════════════════════════════
# MODULO 1 — ASISTENTE DE PRODUCTOS (RAG simplificado)
# ════════════════════════════════════════════════════════════
with tab1:
    st.subheader("📋 Asistente de Productos Farmacéuticos")
    st.caption("Responde basándose en las fichas técnicas de Farmacia Universal")

    # Base de conocimiento embebida directamente
    FICHAS = {
        "metformina": """FICHA TECNICA — METFORMINA 850mg
Codigo: MET850 | Categoria: Antidiabetico | Precio: S/. 12.50
INDICACIONES: Diabetes mellitus tipo 2. Primera linea segun guias ADA y OMS.
POSOLOGIA: Inicial 500-850mg/dia con comidas. Mantenimiento 1500-2000mg/dia. Maximo 3000mg/dia.
CONTRAINDICACIONES: Insuficiencia renal (TFG<30), hepatica severa, alcoholismo, embarazo.
Suspender 48h antes de contrastes yodados.
EFECTOS ADVERSOS: Frecuentes: nauseas, diarrea. Grave: acidosis lactica (suspender de inmediato).
INTERACCIONES: Alcohol (acidosis lactica), contrastes yodados, furosemida.
ALMACENAMIENTO: 15-30 grados C. Vida util 24 meses.""",

        "enalapril": """FICHA TECNICA — ENALAPRIL 10mg
Codigo: ENA10 | Categoria: Antihipertensivo IECA | Precio: S/. 8.90
INDICACIONES: Hipertension arterial, insuficiencia cardiaca, nefroproteccion en diabetes.
POSOLOGIA: Hipertension: inicio 5mg/dia, mantenimiento 10-20mg/dia. Maximo 40mg/dia.
CONTRAINDICACIONES: Angioedema previo por IECA, embarazo (teratogenico categoria D).
EFECTOS ADVERSOS: Tos seca persistente 10-15%. Hipotension en primera dosis. Angioedema (raro, fatal).
INTERACCIONES: AINEs reducen efecto antihipertensivo. Diureticos ahorradores de K riesgo hiperpotasemia.
ALMACENAMIENTO: 15-25 grados C. Proteger de luz. Vida util 36 meses.""",

        "atorvastatina": """FICHA TECNICA — ATORVASTATINA 20mg
Codigo: ATO20 | Categoria: Antilipemico Estatina | Precio: S/. 15.30
INDICACIONES: Hipercolesterolemia, prevencion cardiovascular primaria y secundaria.
POSOLOGIA: Inicial 10-20mg/dia (noche preferentemente). Maximo 80mg/dia. Con o sin alimentos.
CONTRAINDICACIONES: Enfermedad hepatica activa, embarazo, inhibidores potentes CYP3A4.
EFECTOS ADVERSOS: Miopatia y mialgia. Rabdomiolisis (raro, grave). Elevacion transaminasas.
INTERACCIONES: Ciclosporina, claritromicina aumentan niveles. Gemfibrozilo riesgo rabdomiolisis.
ALMACENAMIENTO: 20-25 grados C. Proteger de luz. Vida util 24 meses."""
    }

    def buscar_ficha(pregunta):
        """RAG simplificado — busca por palabra clave en las fichas."""
        pregunta_lower = pregunta.lower()
        fichas_relevantes = []
        for nombre, contenido in FICHAS.items():
            if nombre in pregunta_lower or any(
                palabra in pregunta_lower
                for palabra in contenido.lower().split()
                if len(palabra) > 5
            )[:3]:
                fichas_relevantes.append(f"[Fuente: {nombre}.txt]\n{contenido}")
        if not fichas_relevantes:
            fichas_relevantes = list(FICHAS.values())[:2]
        return "\n\n---\n\n".join(fichas_relevantes)

    pregunta_prod = st.text_input(
        "Escribe tu pregunta sobre un medicamento:",
        placeholder="Ej: ¿Cuál es la dosis máxima de Metformina?"
    )

    if st.button("🔍 Consultar", key="btn_rag", type="primary"):
        if pregunta_prod:
            with st.spinner("Consultando fichas técnicas..."):
                contexto = buscar_ficha(pregunta_prod)
                cliente = get_cliente()
                resp = cliente.messages.create(
                    model="claude-sonnet-4-6",
                    max_tokens=512,
                    temperature=0.1,
                    system="""Eres el asistente farmaceutico de Farmacia Universal.
Responde UNICAMENTE basandote en las fichas tecnicas proporcionadas.
Si la informacion no esta en las fichas, indicalo explicitamente.
Cita siempre el nombre del medicamento fuente. Responde en espanol.""",
                    messages=[{"role":"user","content":
                        f"Fichas tecnicas:\n\n{contexto}\n\nPregunta: {pregunta_prod}"}]
                )
            st.success(resp.content[0].text)
        else:
            st.warning("Escribe una pregunta primero.")

# ════════════════════════════════════════════════════════════
# MODULO 2 — CLASIFICADOR DE TICKETS
# ════════════════════════════════════════════════════════════
with tab2:
    st.subheader("🎫 Clasificador de Tickets de Soporte")

    def limpiar_json(texto):
        texto = texto.strip()
        if "```" in texto:
            lineas = [l for l in texto.split("\n") if not l.strip().startswith("```")]
            texto = "\n".join(lineas)
        inicio = texto.find("{")
        fin = texto.rfind("}") + 1
        if inicio >= 0 and fin > inicio:
            texto = texto[inicio:fin]
        return texto.strip()

    SYSTEM_TICKET = """Eres un clasificador de tickets de soporte tecnico.
Responde UNICAMENTE con JSON sin texto adicional:
{"categoria": "Acceso|Rendimiento|Facturacion|Integracion|Cuenta|Reporte|Otro",
 "prioridad": "Alta|Media|Baja",
 "resumen": "maximo 15 palabras"}"""

    col_izq, col_der = st.columns([3, 2])
    with col_izq:
        ticket_texto = st.text_area(
            "Describe el problema:",
            placeholder="Ej: No puedo acceder a mi cuenta desde ayer...",
            height=150
        )
        if st.button("🎯 Clasificar ticket", key="btn_ticket", type="primary"):
            if ticket_texto:
                with st.spinner("Clasificando..."):
                    cliente = get_cliente()
                    resp = cliente.messages.create(
                        model="claude-sonnet-4-6",
                        max_tokens=200,
                        temperature=0,
                        system=SYSTEM_TICKET,
                        messages=[{"role":"user","content":ticket_texto}]
                    )
                    resultado = json.loads(limpiar_json(resp.content[0].text))

                with col_der:
                    st.subheader("Resultado")
                    colores = {"Alta":"🔴","Media":"🟡","Baja":"🟢"}
                    st.metric("Categoría", resultado["categoria"])
                    st.metric("Prioridad",
                        f"{colores.get(resultado['prioridad'],'⚪')} {resultado['prioridad']}")
                    st.info(f"**Resumen:** {resultado['resumen']}")
            else:
                st.warning("Escribe el texto del ticket.")

# ════════════════════════════════════════════════════════════
# MODULO 3 — ANALISIS DE VENTAS
# ════════════════════════════════════════════════════════════
with tab3:
    st.subheader("📊 Análisis de Ventas con IA")

    # Datos de ejemplo siempre disponibles
    @st.cache_data
    def datos_ejemplo():
        return pd.DataFrame([
            {'local':'Centro',    'producto':'Metformina 850mg',  'cantidad':5, 'venta':62.50},
            {'local':'Centro',    'producto':'Enalapril 10mg',    'cantidad':3, 'venta':26.70},
            {'local':'Miraflores','producto':'Atorvastatina 20mg','cantidad':8, 'venta':122.40},
            {'local':'Centro',    'producto':'Amoxicilina 500mg', 'cantidad':12,'venta':81.60},
            {'local':'Miraflores','producto':'Metformina 850mg',  'cantidad':6, 'venta':75.00},
            {'local':'San Isidro','producto':'Atorvastatina 20mg','cantidad':10,'venta':153.00},
            {'local':'San Isidro','producto':'Amoxicilina 500mg', 'cantidad':7, 'venta':47.60},
        ])

    opcion = st.radio("Fuente de datos:", ["Usar datos de ejemplo", "Subir Excel propio"],
                      horizontal=True)

    if opcion == "Subir Excel propio":
        archivo = st.file_uploader("Sube tu Excel de ventas:", type=["xlsx","xls"])
        df = pd.read_excel(archivo) if archivo else None
    else:
        df = datos_ejemplo()

    if df is not None:
        # KPIs
        col1, col2, col3 = st.columns(3)
        col1.metric("Total ventas", f"S/. {df['venta'].sum():.2f}")
        col2.metric("Unidades", int(df['cantidad'].sum()))
        col3.metric("Locales", df['local'].nunique())

        # Grafico
        por_local = df.groupby('local')['venta'].sum().reset_index()
        st.bar_chart(por_local.set_index('local'))

        # Analisis con IA
        if st.button("🤖 Generar análisis ejecutivo", key="btn_ventas", type="primary"):
            resumen = df.groupby('local').agg(
                unidades=('cantidad','sum'),
                ingresos=('venta','sum')
            ).to_string()

            with st.spinner("Claude analizando..."):
                cliente = get_cliente()
                resp = cliente.messages.create(
                    model="claude-sonnet-4-6",
                    max_tokens=512,
                    temperature=0.2,
                    system="Eres analista comercial de Farmacia Universal. Reportes ejecutivos concisos en espanol.",
                    messages=[{"role":"user","content":
                        f"Analiza estas ventas y dame 3 insights clave:\n{resumen}"}]
                )
            st.success(resp.content[0].text)

# ════════════════════════════════════════════════════════════
# MODULO 4 — CONSULTOR SQL
# ════════════════════════════════════════════════════════════
with tab4:
    st.subheader("🔍 Consultor SQL en Lenguaje Natural")
    st.caption("Escribe una pregunta en español y el sistema genera el SQL y ejecuta la consulta")

    ESQUEMA = """
Base de datos: farmacia.db (SQLite)
TABLA productos: codigo (PK), nombre, categoria, precio_unit, stock
TABLA ventas: id (PK), fecha, local, codigo_prod (FK→productos.codigo), cantidad, precio_unit
TABLA locales: nombre (PK), distrito, supervisor
"""

    SYSTEM_SQL = """Eres un experto en SQL para SQLite.
Responde UNICAMENTE con la consulta SQL — sin explicaciones, sin markdown, sin punto y coma."""

    @st.cache_resource
    def get_conexion():
        if not os.path.exists('farmacia.db'):
            return None
        return sqlite3.connect('farmacia.db', check_same_thread=False)

    pregunta_sql = st.text_input(
        "¿Qué quieres saber de la base de datos?",
        placeholder="Ej: ¿Cuáles son los 3 productos más vendidos?"
    )

    if st.button("🔍 Consultar BD", key="btn_sql", type="primary"):
        if pregunta_sql:
            with st.spinner("Generando SQL..."):
                cliente = get_cliente()
                resp = cliente.messages.create(
                    model="claude-sonnet-4-6",
                    max_tokens=300,
                    temperature=0,
                    system=SYSTEM_SQL,
                    messages=[{"role":"user","content":
                        f"Esquema:\n{ESQUEMA}\n\nPregunta: {pregunta_sql}\n\nSQL:"}]
                )
                sql = resp.content[0].text.strip()
                if "```" in sql:
                    sql = "\n".join([l for l in sql.split("\n")
                                     if not l.strip().startswith("```")]).strip()

            st.code(sql, language="sql")

            # Validar que sea SELECT
            if not sql.strip().upper().startswith("SELECT"):
                st.error("Solo se permiten consultas SELECT.")
            else:
                conn = get_conexion()
                if conn is None:
                    st.warning("Base de datos no disponible. Ejecuta setup_db.py primero.")
                else:
                    try:
                        resultado = pd.read_sql_query(sql, conn)
                        st.dataframe(resultado, use_container_width=True)
                        st.caption(f"{len(resultado)} filas retornadas")
                    except Exception as e:
                        st.error(f"Error al ejecutar: {e}")
        else:
            st.warning("Escribe una pregunta primero.")

# Footer
st.divider()
st.caption("Sistema de IA · Farmacia Universal SAC · 2026 · Proyecto 2 — Curso IA")