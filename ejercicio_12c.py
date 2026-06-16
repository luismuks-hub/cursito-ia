import anthropic
import json
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
cliente = anthropic.Anthropic()

emails_pedidos = [
    """De: clinica.miraflores@gmail.com
    Necesitamos con urgencia: 200 cajas de Metformina 850mg,
    50 frascos de Enalapril 10mg y 30 cajas de Atorvastatina 20mg.
    Entregar en Jr. Las Flores 234, Miraflores. Contacto: Dr. Ramirez, cel 987654321.
    Necesitamos para el viernes 14 de junio.""",

    """Hola buenos días, somos Botica San José de la Av. Arequipa 1500.
    Por favor enviarnos 100 unidades de Amoxicilina 500mg y
    80 unidades de Ibuprofeno 400mg. El pago es contra entrega.
    Llamar a Carmen al 01-4567890 para coordinar.""",

    """Pedido urgente de Farmacia Los Andes - Huancayo.
    Requerimos: Metformina 500mg x 150 cajas, Losartan 50mg x 200 cajas.
    Despacho a Jr. Real 456 Huancayo. RUC: 20456789012.
    Pago: transferencia previa. Sr. Mendoza 064-234567.""",
]

SYSTEM = """Eres un extractor de datos de pedidos farmacéuticos.
Responde ÚNICAMENTE con JSON válido, sin texto adicional ni bloques de código."""

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

def extraer_pedido(email_texto):
    prompt = f"""Extrae los datos de este email en JSON exacto:
{{
  "cliente": "nombre del negocio",
  "direccion": "dirección de entrega",
  "contacto": {{"nombre": "nombre", "telefono": "número"}},
  "ruc": "RUC o null",
  "fecha_entrega": "fecha o null",
  "forma_pago": "forma de pago o null",
  "productos": [{{"nombre": "producto", "cantidad": numero, "unidad": "cajas/frascos/unidades"}}],
  "urgente": true o false
}}

EMAIL:
{email_texto}"""

    respuesta = cliente.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        temperature=0,
        system=SYSTEM,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = respuesta.content[0].text
    return json.loads(limpiar_json(raw))

# ─── Procesar todos los emails ───────────────────────────────
print("Extrayendo datos de pedidos...\n")
pedidos = []

for i, email in enumerate(emails_pedidos, 1):
    datos = extraer_pedido(email)
    pedidos.append(datos)
    print(f"Pedido {i}: {datos['cliente']} — {len(datos['productos'])} productos")
    for p in datos['productos']:
        print(f"  └ {p['cantidad']} {p['unidad']} de {p['nombre']}")
    print()

# Guardar JSON completo
with open("pedidos_extraidos.json", "w", encoding="utf-8") as f:
    json.dump(pedidos, f, ensure_ascii=False, indent=2)

# Tabla para Excel
filas = []
for pedido in pedidos:
    for producto in pedido['productos']:
        filas.append({
            'Cliente': pedido['cliente'],
            'Producto': producto['nombre'],
            'Cantidad': producto['cantidad'],
            'Unidad': producto['unidad'],
            'Urgente': pedido['urgente'],
            'Contacto': pedido['contacto']['telefono']
        })

df = pd.DataFrame(filas)
df.to_excel("pedidos_para_despacho.xlsx", index=False)
print(f"✓ {len(pedidos)} pedidos procesados")
print(f"✓ pedidos_extraidos.json guardado")
print(f"✓ pedidos_para_despacho.xlsx generado")