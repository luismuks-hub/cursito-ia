import anthropic
import pandas as pd
import json
from dotenv import load_dotenv

load_dotenv()
cliente = anthropic.Anthropic()

# ─── Tickets de soporte de ejemplo ──────────────────────────
tickets = [
    {"id": 1, "texto": "No puedo acceder a mi cuenta, olvidé mi contraseña y el link de recuperación no llega a mi email"},
    {"id": 2, "texto": "El sistema está muy lento desde ayer, tarda 5 minutos en cargar cada página"},
    {"id": 3, "texto": "Necesito que me facturen el mes de mayo por separado, tenemos dos centros de costo"},
    {"id": 4, "texto": "Se cayó la integración con el ERP, los pedidos no están sincronizando desde las 8am"},
    {"id": 5, "texto": "Quiero agregar 3 usuarios nuevos a mi cuenta del plan Enterprise"},
    {"id": 6, "texto": "El reporte de ventas del mes pasado tiene números incorrectos, no cuadra con mi Excel"},
]

SYSTEM = """Eres un clasificador de tickets de soporte técnico.
Para cada ticket debes responder ÚNICAMENTE con un JSON en este formato exacto,
sin texto adicional, sin bloques de código, sin comillas triples:
{"categoria": "Acceso|Rendimiento|Facturación|Integración|Cuenta|Reporte|Otro",
 "prioridad": "Alta|Media|Baja",
 "resumen": "máximo 15 palabras"}"""

def limpiar_json(texto):
    """Limpia el texto de markdown antes de parsear como JSON."""
    texto = texto.strip()
    # Elimina bloques ```json ... ```
    if "```" in texto:
        lineas = texto.split("\n")
        lineas = [l for l in lineas if not l.strip().startswith("```")]
        texto = "\n".join(lineas)
    # Busca el primer { y el ultimo } para extraer solo el JSON
    inicio = texto.find("{")
    fin = texto.rfind("}") + 1
    if inicio >= 0 and fin > inicio:
        texto = texto[inicio:fin]
    return texto.strip()

def clasificar_ticket(texto):
    respuesta = cliente.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=200,
        temperature=0,
        system=SYSTEM,
        messages=[{"role": "user", "content": texto}]
    )
    raw = respuesta.content[0].text
    print(f"  [DEBUG] Raw response: {raw[:80]}...")  # Ver que devuelve Claude
    limpio = limpiar_json(raw)
    return json.loads(limpio)

# ─── Procesar todos los tickets ─────────────────────────────
print("Clasificando tickets...\n")
resultados = []

for ticket in tickets:
    print(f"Procesando ticket {ticket['id']}...")
    clasificacion = clasificar_ticket(ticket["texto"])
    resultados.append({
        "id": ticket["id"],
        "categoria": clasificacion["categoria"],
        "prioridad": clasificacion["prioridad"],
        "resumen": clasificacion["resumen"],
        "texto_original": ticket["texto"]
    })
    print(f"  → {clasificacion['categoria']} | {clasificacion['prioridad']}")

# Guardar en Excel
df = pd.DataFrame(resultados)
df.to_excel("tickets_clasificados.xlsx", index=False)
print(f"\n✓ {len(resultados)} tickets clasificados → tickets_clasificados.xlsx")

# Resumen por categoría
print("\n=== RESUMEN POR CATEGORÍA ===")
print(df.groupby("categoria")["prioridad"].value_counts().to_string())