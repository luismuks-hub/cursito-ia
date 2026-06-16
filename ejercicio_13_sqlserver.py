import anthropic
import pyodbc
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
cliente = anthropic.Anthropic()

# ─── CONFIGURACION DE CONEXION SQL SERVER ────────────────────
# Ajusta estos valores con los datos reales de tu servidor
SERVIDOR   = "NOMBRE_SERVIDOR"        # ej: "192.168.1.100" o "LOLFAR-SRV\SQLEXPRESS"
BASE_DATOS = "NOMBRE_BASE_DATOS"      # ej: "FarmaciaUniversal" o "LOLFAR_PROD"
USUARIO    = "tu_usuario"             # ej: "sa" o "lcoronel"
PASSWORD   = "tu_password"            # ej: "MiPassword123"

# Dos formas de conectar — elige la que aplique a tu entorno:

# Opcion A: Usuario y password SQL Server (SQL Authentication)
def conectar_sql_auth():
    return pyodbc.connect(
        f"DRIVER={{SQL Server}};"
        f"SERVER={SERVIDOR};"
        f"DATABASE={BASE_DATOS};"
        f"UID={USUARIO};"
        f"PWD={PASSWORD};"
    )

# Opcion B: Windows Authentication (sin usuario/password)
# Usa las credenciales de Windows con las que estas logueado
def conectar_windows_auth():
    return pyodbc.connect(
        f"DRIVER={{SQL Server}};"
        f"SERVER={SERVIDOR};"
        f"DATABASE={BASE_DATOS};"
        f"Trusted_Connection=yes;"
    )

# ─── FUNCION PARA EXTRAER EL ESQUEMA AUTOMATICAMENTE ─────────
# En lugar de escribir el esquema a mano, lo leemos de la BD
def obtener_esquema(conn, tablas_de_interes):
    """
    Lee la estructura de las tablas desde SQL Server y genera
    el texto de esquema para enviar a Claude.
    Solo incluye las tablas que especificas — no toda la BD.
    """
    esquema = f"Base de datos: {BASE_DATOS} (SQL Server)\n\n"
    
    for tabla in tablas_de_interes:
        # Consulta el information schema de SQL Server
        sql_cols = f"""
            SELECT 
                COLUMN_NAME,
                DATA_TYPE,
                CHARACTER_MAXIMUM_LENGTH,
                IS_NULLABLE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = '{tabla}'
            ORDER BY ORDINAL_POSITION
        """
        df_cols = pd.read_sql_query(sql_cols, conn)
        
        esquema += f"TABLA {tabla}:\n"
        for _, col in df_cols.iterrows():
            tipo = col['DATA_TYPE']
            if col['CHARACTER_MAXIMUM_LENGTH']:
                tipo += f"({int(col['CHARACTER_MAXIMUM_LENGTH'])})"
            nulo = "NULL" if col['IS_NULLABLE'] == 'YES' else "NOT NULL"
            esquema += f"  - {col['COLUMN_NAME']:30} {tipo:20} {nulo}\n"
        esquema += "\n"
    
    return esquema

# ─── SYSTEM PROMPT PARA SQL SERVER ───────────────────────────
# Diferencias clave vs SQLite:
# - TOP N en lugar de LIMIT N
# - GETDATE() en lugar de date()
# - CONVERT() en lugar de CAST() para fechas
SYSTEM = """Eres un experto en SQL para SQL Server (T-SQL).
Cuando recibas una pregunta en español sobre la base de datos,
responde ÚNICAMENTE con la consulta SQL correcta en T-SQL.
Sin explicaciones, sin bloques markdown, sin punto y coma al final.
Usa TOP en lugar de LIMIT. Usa GETDATE() para fecha actual.
Usa comillas simples para strings, corchetes para nombres con espacios."""

def limpiar_sql(texto):
    """Limpia el SQL por si Claude agrega markdown."""
    texto = texto.strip()
    if "```" in texto:
        lineas = [l for l in texto.split("\n") if not l.strip().startswith("```")]
        texto = "\n".join(lineas).strip()
    return texto

def texto_a_sql(pregunta, esquema):
    """Convierte pregunta en español a T-SQL usando Claude."""
    prompt = f"""Esquema de la base de datos:
{esquema}

Pregunta: {pregunta}

SQL:"""
    
    respuesta = cliente.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=400,
        temperature=0,
        system=SYSTEM,
        messages=[{"role": "user", "content": prompt}]
    )
    return limpiar_sql(respuesta.content[0].text)

def ejecutar_pregunta(pregunta, conn, esquema):
    """Convierte pregunta a SQL, valida, ejecuta y muestra resultados."""
    print(f"\n{'='*60}")
    print(f"PREGUNTA: {pregunta}")
    
    # Generar SQL
    sql = texto_a_sql(pregunta, esquema)
    print(f"\nSQL GENERADO:\n{sql}")
    
    # ─── SEGURIDAD: solo permitir SELECT ─────────────────────
    # En una BD de produccion NUNCA ejecutar DELETE/UPDATE/DROP
    primera_palabra = sql.strip().upper().split()[0]
    if primera_palabra != "SELECT":
        print("⚠ BLOQUEADO: solo se permiten consultas SELECT")
        return None
    
    # Ejecutar
    try:
        df = pd.read_sql_query(sql, conn)
        print(f"\nRESULTADO ({len(df)} filas):")
        print(df.to_string(index=False))
        return df
    except Exception as e:
        print(f"✗ Error al ejecutar: {e}")
        return None

# ─── EJECUCION PRINCIPAL ─────────────────────────────────────
if __name__ == "__main__":

    # ── Paso 1: Conectar ─────────────────────────────────────
    print("Conectando a SQL Server...")
    try:
        # Cambia a conectar_sql_auth() si usas usuario/password
        conn = conectar_windows_auth()
        print(f"✓ Conectado a {BASE_DATOS} en {SERVIDOR}")
    except Exception as e:
        print(f"✗ Error de conexion: {e}")
        print("\nVerifica:")
        print("  1. Que el servidor este activo y accesible")
        print("  2. Que el nombre del servidor sea correcto")
        print("  3. Que el usuario tenga permisos de lectura")
        print("  4. Que pyodbc este instalado: pip install pyodbc")
        exit()

    # ── Paso 2: Definir las tablas de interes ────────────────
    # Solo las tablas relevantes para las preguntas de negocio
    # No incluir tablas de configuracion, logs, etc.
    TABLAS = [
        "Ventas",           # Ajusta con los nombres reales del LOLFAR
        "Productos",
        "Locales",
    ]

    # ── Paso 3: Leer el esquema automaticamente ───────────────
    print("\nLeyendo esquema de la base de datos...")
    esquema = obtener_esquema(conn, TABLAS)
    print("✓ Esquema leido:")
    print(esquema)

    # ── Paso 4: Preguntas de negocio ─────────────────────────
    # Estas son las preguntas que el gerente o supervisor haria
    preguntas = [
        "¿Cuáles son los 5 productos más vendidos este mes?",
        "¿Cuánto ingresó cada local en la última semana?",
        "¿Qué productos tienen stock por debajo de 100 unidades?",
        "¿Cuál es el ticket promedio de venta por local?",
        "¿Qué categoría de medicamento genera más ingresos?",
    ]

    for pregunta in preguntas:
        ejecutar_pregunta(pregunta, conn, esquema)

    conn.close()
    print("\n✓ Conexion cerrada")