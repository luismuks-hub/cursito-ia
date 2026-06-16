import anthropic
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
cliente = anthropic.Anthropic()

# ─── Datos de ventas (del Tema 10) ──────────────────────────
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

# ─── Preparar el resumen de datos para enviar a Claude ──────
resumen_por_local = df.groupby('local').agg(
    unidades=('cantidad','sum'),
    ingresos=('venta','sum')
).to_string()

resumen_por_producto = df.groupby('producto').agg(
    unidades=('cantidad','sum'),
    ingresos=('venta','sum')
).sort_values('ingresos', ascending=False).to_string()

# ─── Llamada a la API con system prompt ─────────────────────
respuesta = cliente.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    temperature=0.2,   # Baja para analisis de datos
    system="""Eres un analista comercial senior de Farmacia Universal.
Recibes datos de ventas y generas reportes ejecutivos concisos.
Responde siempre en español, en formato de reporte ejecutivo.
Usa bullets para los puntos clave. Maximo 200 palabras.""",
    messages=[
        {
            "role": "user",
            "content": f"""Analiza estos datos de ventas del 1 al 3 de junio 2026
y genera un reporte ejecutivo con hallazgos y 2 recomendaciones.

VENTAS POR LOCAL:
{resumen_por_local}

VENTAS POR PRODUCTO:
{resumen_por_producto}"""
        }
    ]
)

print("=== REPORTE GENERADO POR CLAUDE ===\n")
print(respuesta.content[0].text)
print(f"\n[Tokens: entrada={respuesta.usage.input_tokens}, salida={respuesta.usage.output_tokens}]")