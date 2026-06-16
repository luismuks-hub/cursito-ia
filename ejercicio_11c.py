import anthropic
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
cliente = anthropic.Anthropic()

# ─── Datos base ──────────────────────────────────────────────
datos = [
    {'local':'Centro',     'producto':'Metformina 850mg',   'cantidad':5,  'venta':62.50},
    {'local':'Centro',     'producto':'Enalapril 10mg',     'cantidad':3,  'venta':26.70},
    {'local':'Centro',     'producto':'Amoxicilina 500mg',  'cantidad':12, 'venta':81.60},
    {'local':'Miraflores', 'producto':'Atorvastatina 20mg', 'cantidad':8,  'venta':122.40},
    {'local':'Miraflores', 'producto':'Metformina 850mg',   'cantidad':6,  'venta':75.00},
    {'local':'Miraflores', 'producto':'Enalapril 10mg',     'cantidad':4,  'venta':35.60},
    {'local':'San Isidro', 'producto':'Atorvastatina 20mg', 'cantidad':10, 'venta':153.00},
    {'local':'San Isidro', 'producto':'Amoxicilina 500mg',  'cantidad':7,  'venta':47.60},
]

df = pd.DataFrame(datos)
resumen = df.groupby('local').agg(
    unidades=('cantidad','sum'),
    ingresos=('venta','sum')
).to_string()

SYSTEM = """Eres un analista comercial senior de Farmacia Universal.
Tienes acceso a los datos de ventas del 1 al 3 de junio 2026.
Responde en español, de forma concisa y ejecutiva.
Cuando te hagan preguntas de seguimiento, recuerda el contexto
de la conversacion anterior."""

# ─── Contexto inicial — los datos ───────────────────────────
contexto_inicial = f"""Aqui estan los datos de ventas para que los analices:

VENTAS POR LOCAL:
{resumen}

Confirma que recibiste los datos y estate listo para responder preguntas."""

# ─── Historial de conversacion ───────────────────────────────
# Esto es lo que hace posible el multi-turno:
# cada mensaje previo se incluye en la siguiente llamada
historial = []

def preguntar(pregunta):
    """Envia una pregunta a Claude manteniendo el historial."""
    historial.append({"role": "user", "content": pregunta})

    respuesta = cliente.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        temperature=0.2,
        system=SYSTEM,
        messages=historial
    )

    texto = respuesta.content[0].text
    historial.append({"role": "assistant", "content": texto})
    return texto

# ─── Conversacion de 3 turnos ────────────────────────────────
print("=== ANALISTA IA — FARMACIA UNIVERSAL ===\n")

# Turno 1: establecer contexto
r1 = preguntar(contexto_inicial)
print(f"[Turno 1]\n{r1}\n")

# Turno 2: pregunta de seguimiento
r2 = preguntar("¿Cual es el local con mayor ticket promedio por unidad?")
print(f"[Turno 2]\n{r2}\n")

# Turno 3: otra pregunta de seguimiento
r3 = preguntar("Si tuvieras que cerrar un local por bajo rendimiento, cual seria y por que?")
print(f"[Turno 3]\n{r3}\n")

print(f"Mensajes en historial: {len(historial)}")