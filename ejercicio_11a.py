import anthropic
from dotenv import load_dotenv

# Carga la API key desde el archivo .env
load_dotenv()

# Crea el cliente de Anthropic
cliente = anthropic.Anthropic()

# ─── Primera llamada a la API ───────────────────────────────
mensaje = cliente.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": "Hola Claude. Responde en español. ¿Qué es RAG en una sola oración?"
        }
    ]
)

# Extraer el texto de la respuesta
respuesta = mensaje.content[0].text
print("Respuesta de Claude:")
print(respuesta)

# Ver también los tokens usados
print(f"\nTokens usados — entrada: {mensaje.usage.input_tokens}, salida: {mensaje.usage.output_tokens}")