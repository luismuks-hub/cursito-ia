import sqlite3

# Crear la base de datos (crea el archivo si no existe)
conn = sqlite3.connect('farmacia.db')
cursor = conn.cursor()

# ─── Crear tablas ────────────────────────────────────────────
cursor.executescript("""
CREATE TABLE IF NOT EXISTS productos (
    codigo      TEXT PRIMARY KEY,
    nombre      TEXT NOT NULL,
    categoria   TEXT NOT NULL,
    precio_unit REAL NOT NULL,
    stock       INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS ventas (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha       TEXT NOT NULL,
    local       TEXT NOT NULL,
    codigo_prod TEXT NOT NULL,
    cantidad    INTEGER NOT NULL,
    precio_unit REAL NOT NULL,
    FOREIGN KEY (codigo_prod) REFERENCES productos(codigo)
);

CREATE TABLE IF NOT EXISTS locales (
    nombre      TEXT PRIMARY KEY,
    distrito    TEXT NOT NULL,
    supervisor  TEXT NOT NULL
);
""")

# ─── Insertar datos ──────────────────────────────────────────
cursor.executemany("INSERT OR IGNORE INTO productos VALUES (?,?,?,?,?)", [
    ('MET850', 'Metformina 850mg',   'Antidiabetico', 12.50, 240),
    ('ENA10',  'Enalapril 10mg',     'Antihipertensivo', 8.90, 85),
    ('ATO20',  'Atorvastatina 20mg', 'Antilipemico',  15.30, 120),
    ('AMO500', 'Amoxicilina 500mg',  'Antibiotico',    6.80, 310),
    ('IBU400', 'Ibuprofeno 400mg',   'Analgesico',     4.50, 450),
    ('LOS50',  'Losartan 50mg',      'Antihipertensivo', 9.20, 200),
])

cursor.executemany("INSERT OR IGNORE INTO locales VALUES (?,?,?)", [
    ('Centro',     'Cercado de Lima', 'Ana Torres'),
    ('Miraflores', 'Miraflores',      'Carlos Rios'),
    ('San Isidro', 'San Isidro',      'Maria Vega'),
])

cursor.executemany("INSERT OR IGNORE INTO ventas (fecha,local,codigo_prod,cantidad,precio_unit) VALUES (?,?,?,?,?)", [
    ('2026-06-01', 'Centro',     'MET850', 5,  12.50),
    ('2026-06-01', 'Centro',     'ENA10',  3,   8.90),
    ('2026-06-01', 'Miraflores', 'ATO20',  8,  15.30),
    ('2026-06-02', 'Centro',     'AMO500', 12,  6.80),
    ('2026-06-02', 'Miraflores', 'MET850', 6,  12.50),
    ('2026-06-02', 'Miraflores', 'ENA10',  4,   8.90),
    ('2026-06-03', 'San Isidro', 'ATO20',  10, 15.30),
    ('2026-06-03', 'San Isidro', 'AMO500', 7,   6.80),
    ('2026-06-04', 'Centro',     'IBU400', 15,  4.50),
    ('2026-06-04', 'Miraflores', 'LOS50',  9,   9.20),
    ('2026-06-05', 'San Isidro', 'MET850', 11, 12.50),
    ('2026-06-05', 'Centro',     'ATO20',  6,  15.30),
])

conn.commit()
conn.close()
print("✓ Base de datos farmacia.db creada con 3 tablas y datos de prueba")