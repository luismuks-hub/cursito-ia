import streamlit as st
import anthropic
import json
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Clasificador de Tickets — Farmacia Universal",
    page_icon="💊",
    layout="wide"
)

st.title("💊 Clasificador de Tickets de Soporte")
st.caption("Farmacia Universal · Powered by Claude AI")

# ─── Configuración en sidebar ────────────────────────────────
with st.sidebar:
    st.header("⚙️ Configuración")
    temperatura = st.slider("Temperatura", 0.0, 1.0, 0.0, 0.1)
    max_tokens = st.slider("Max tokens", 100, 500, 200, 50)
    st.divider()
    st.info("Temperatura 0 = clasificación consistente")

# ─── Función de clasificación ────────────────────────────────
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

@st.cache_resource
def get_cliente():
    return anthropic.Anthropic()

SYSTEM = """Eres un clasificador de tickets de soporte técnico.
Responde ÚNICAMENTE con JSON sin texto adicional:
{"categoria": "Acceso|Rendimiento|Facturación|Integración|Cuenta|Reporte|Otro",
 "prioridad": "Alta|Media|Baja",
 "resumen": "máximo 15 palabras"}"""

def clasificar(texto, temp, tokens):
    cliente = get_cliente()
    resp = cliente.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=tokens,
        temperature=temp,
        system=SYSTEM,
        messages=[{"role": "user", "content": texto}]
    )
    return json.loads(limpiar_json(resp.content[0].text))

# ─── Interface principal ──────────────────────────────────────
tab1, tab2 = st.tabs(["📝 Clasificar ticket", "📊 Batch — múltiples tickets"])

with tab1:
    st.subheader("Clasificar un ticket")
    texto = st.text_area(
        "Describe el problema del cliente:",
        placeholder="Ej: No puedo acceder a mi cuenta, olvidé mi contraseña...",
        height=120
    )

    if st.button("🔍 Clasificar", type="primary"):
        if texto:
            with st.spinner("Clasificando con Claude..."):
                resultado = clasificar(texto, temperatura, max_tokens)

            col1, col2 = st.columns(2)
            with col1:
                color = {"Alta": "🔴", "Media": "🟡", "Baja": "🟢"}
                st.metric("Categoría", resultado["categoria"])
                st.metric("Prioridad", f"{color.get(resultado['prioridad'], '⚪')} {resultado['prioridad']}")
            with col2:
                st.info(f"**Resumen:** {resultado['resumen']}")
        else:
            st.warning("Escribe el texto del ticket primero.")

with tab2:
    st.subheader("Clasificar múltiples tickets")
    tickets_ejemplo = """No puedo acceder a mi cuenta
El sistema está muy lento
Necesito factura separada
Se cayó la integración con el ERP
Quiero agregar 3 usuarios nuevos"""

    tickets_texto = st.text_area(
        "Un ticket por línea:",
        value=tickets_ejemplo,
        height=150
    )

    if st.button("🔍 Clasificar todos", type="primary"):
        tickets = [t.strip() for t in tickets_texto.split("\n") if t.strip()]
        resultados = []

        progress = st.progress(0)
        for i, ticket in enumerate(tickets):
            resultado = clasificar(ticket, temperatura, max_tokens)
            resultados.append({
                "Ticket": ticket[:50] + "..." if len(ticket) > 50 else ticket,
                "Categoría": resultado["categoria"],
                "Prioridad": resultado["prioridad"],
                "Resumen": resultado["resumen"]
            })
            progress.progress((i + 1) / len(tickets))

        import pandas as pd
        df = pd.DataFrame(resultados)
        st.dataframe(df, use_container_width=True)

        # Descargar como Excel
        excel_buffer = df.to_excel.__module__
        import io
        buffer = io.BytesIO()
        df.to_excel(buffer, index=False)
        st.download_button(
            "📥 Descargar Excel",
            data=buffer.getvalue(),
            file_name="tickets_clasificados.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )