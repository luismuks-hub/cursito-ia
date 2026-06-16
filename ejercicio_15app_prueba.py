import streamlit as st

# ─── Título y descripción ────────────────────────────────────
st.title("Mi primera app de IA")
st.subheader("Farmacia Universal — Asistente Inteligente")
st.write("Esta es una aplicación construida con Python y Streamlit.")

# ─── Inputs del usuario ──────────────────────────────────────
nombre = st.text_input("¿Cómo te llamas?", placeholder="Escribe tu nombre...")
opcion = st.selectbox("¿Qué área eres?", ["Ventas", "TI", "RRHH", "Farmacia"])
nivel = st.slider("¿Cuánto sabes de IA?", min_value=0, max_value=10, value=5)
boton = st.button("Generar saludo")

# ─── Lógica y outputs ────────────────────────────────────────
if boton and nombre:
    st.success(f"¡Hola {nombre} del área de {opcion}!")
    st.info(f"Tu nivel de IA es {nivel}/10. ¡Vamos a mejorarlo!")

    # Mostrar métricas
    col1, col2, col3 = st.columns(3)
    col1.metric("Área", opcion)
    col2.metric("Nivel IA", f"{nivel}/10")
    col3.metric("Estado", "Activo")