import anthropic
from dotenv import load_dotenv

load_dotenv()
cliente = anthropic.Anthropic()

# Simula el texto de un contrato de proveedor
CONTRATO = """
CONTRATO DE SERVICIOS DE TECNOLOGÍA

Entre: Farmacia Universal SAC (en adelante "EL CLIENTE") con RUC 20512345678,
y TechSoft Peru SAC (en adelante "EL PROVEEDOR") con RUC 20698765432.

PRIMERA - OBJETO DEL CONTRATO:
El Proveedor se compromete a brindar servicios de mantenimiento y soporte
del sistema de gestión LOLFAR durante 12 meses, incluyendo actualizaciones,
corrección de errores y soporte telefónico en horario laboral.

SEGUNDA - VIGENCIA:
El contrato tendrá vigencia desde el 1 de enero 2026 hasta el 31 de diciembre 2026.
Se renovará automáticamente por períodos iguales salvo aviso contrario con 30 días
de anticipación.

TERCERA - PRECIO Y FORMA DE PAGO:
El precio mensual es de S/. 4,500 más IGV. El pago se realizará dentro de los
primeros 10 días de cada mes. El retraso en el pago generará intereses del 1.5%
mensual sobre el monto vencido.

CUARTA - PENALIDADES:
Si el sistema presenta una caída mayor a 4 horas en horario laboral, el Proveedor
aplicará un descuento del 20% en la factura del mes correspondiente.
Si la caída supera las 8 horas, el descuento será del 40%.

QUINTA - CONFIDENCIALIDAD:
El Proveedor se compromete a mantener confidencialidad sobre toda la información
a la que tenga acceso durante la vigencia del contrato y por 3 años posteriores.

SEXTA - RESOLUCIÓN:
Cualquiera de las partes puede resolver el contrato con 60 días de aviso previo
por escrito. Si el cliente resuelve sin causa justificada, deberá pagar 2 meses
adicionales como penalidad.
"""

SYSTEM = """Eres un analista legal especializado en contratos de tecnología.
Analiza contratos y genera fichas ejecutivas estructuradas.
Responde siempre en español."""

prompt = f"""Analiza este contrato y genera una ficha ejecutiva con estas secciones exactas:

**FICHA DE CONTRATO**
- Partes: [quiénes firman]
- Objeto: [qué se contrata en una línea]
- Vigencia: [fechas y condiciones de renovación]
- Monto: [precio y condiciones de pago]
- Penalidades: [listar todas las penalidades]
- Riesgos clave: [máximo 3 riesgos que debería evaluar el gerente]
- Cláusulas favorables: [lo que favorece al cliente]
- Cláusulas desfavorables: [lo que es riesgoso para el cliente]

CONTRATO A ANALIZAR:
{CONTRATO}"""

respuesta = cliente.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    temperature=0.1,
    system=SYSTEM,
    messages=[{"role": "user", "content": prompt}]
)

print(respuesta.content[0].text)

# Guardar la ficha
with open("ficha_contrato.txt", "w", encoding="utf-8") as f:
    f.write(respuesta.content[0].text)
print("\n✓ Ficha guardada en ficha_contrato.txt")