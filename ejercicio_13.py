import anthropic
import sqlite3
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
cliente = anthropic.Anthropic()

# ─── El esquema de la BD — esto es lo que envías a Claude ────
ESQUEMA = """
Base de datos: farmacia.db (SQLite)

TABLA productos:
  - codigo      TEXT (PK) — codigo del producto
  - nombre      TEXT      — nombre completo del medicamento
  - categoria   TEXT      — Antidiabetico|Antihipertensivo|Antibiotico|Analgesico|Antilipemico
  - precio_unit REAL      — precio unitario en soles
  - stock       INTEGER   — unidades disponibles

TABLA ventas:
  - id          INTEGER (PK, autoincrement)
  - fecha       TEXT      — formato YYYY-MM-DD
  - local       TEXT      — nombre del local (Centro|Miraflores|San Isidro)
  - codigo_prod TEXT (FK → productos.codigo)
  - cantidad    INTEGER   — unidades vendidas
  - precio_unit REAL      — precio al que se vendio

TABLA locales:
  - nombre      TEXT (PK) — nombre del local
  - distrito    TEXT      — distrito de Lima
  - supervisor  TEXT      — nombre del supervisor
"""

SYSTEM = """Eres un experto en SQL para bases de datos SQLite.
Cuando recibas una pregunta en español sobre la base de datos,
responde ÚNICAMENTE con la consulta SQL correcta — sin explicaciones,
sin bloques de código markdown, sin punto y coma al final.
La consulta debe ser compatible con SQLite."""

def texto_a_sql(pregunta):
    """Convierte una pregunta en español a SQL usando Claude."""
    prompt = f"""Esquema de la base de datos:
{ESQUEMA}

Pregunta: {pregunta}

SQL:"""

    respuesta = cliente.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        temperature=0,        # SQL debe ser deterministico
        system=SYSTEM,
        messages=[{"role": "user", "content": prompt}]
    )
    
    # Limpiar el SQL por si viene con markdown
    sql = respuesta.content[0].text.strip()
    if sql.startswith("```"):
        lineas = [l for l in sql.split("\n") if not l.strip().startswith("```")]
        sql = "\n".join(lineas).strip()
    
    return sql

def ejecutar_pregunta(pregunta):
    """Convierte pregunta a SQL, lo ejecuta y muestra resultados."""
    print(f"\n{'='*60}")
    print(f"PREGUNTA: {pregunta}")
    
    # Generar SQL
    sql = texto_a_sql(pregunta)
    print(f"SQL GENERADO:\n{sql}")
    
    # Ejecutar contra la BD
    conn = sqlite3.connect('farmacia.db')
    df = pd.read_sql_query(sql, conn)
    conn.close()
    
    print(f"\nRESULTADO ({len(df)} filas):")
    print(df.to_string(index=False))

# ─── Preguntas de prueba ─────────────────────────────────────
preguntas = [
    "¿Cuáles son los 3 productos más vendidos por cantidad total?",
    "¿Cuánto ingresó cada local en total?",
    "¿Qué productos tienen stock menor a 150 unidades?",
    "¿Cuál es el ingreso total por categoría de producto?",
    "¿Qué local vendió más unidades de Metformina?",
]

for pregunta in preguntas:
    ejecutar_pregunta(pregunta)
