import pandas as pd

# ─── PARTE 1: Crear el Excel de ventas ──────────────────────
datos_ventas = [
    {'fecha':'2026-06-01','local':'Centro',     'producto':'Metformina 850mg',   'cantidad':5,  'precio_unit':12.50},
    {'fecha':'2026-06-01','local':'Centro',     'producto':'Enalapril 10mg',     'cantidad':3,  'precio_unit': 8.90},
    {'fecha':'2026-06-01','local':'Miraflores', 'producto':'Atorvastatina 20mg', 'cantidad':8,  'precio_unit':15.30},
    {'fecha':'2026-06-02','local':'Centro',     'producto':'Amoxicilina 500mg',  'cantidad':12, 'precio_unit': 6.80},
    {'fecha':'2026-06-02','local':'Miraflores', 'producto':'Metformina 850mg',   'cantidad':6,  'precio_unit':12.50},
    {'fecha':'2026-06-02','local':'Miraflores', 'producto':'Enalapril 10mg',     'cantidad':4,  'precio_unit': 8.90},
    {'fecha':'2026-06-03','local':'San Isidro', 'producto':'Atorvastatina 20mg', 'cantidad':10, 'precio_unit':15.30},
    {'fecha':'2026-06-03','local':'San Isidro', 'producto':'Amoxicilina 500mg',  'cantidad':7,  'precio_unit': 6.80},
]

df = pd.DataFrame(datos_ventas)
df.to_excel('ventas.xlsx', index=False)
print("✓ ventas.xlsx creado")

# ─── PARTE 2: Análisis ───────────────────────────────────────
df = pd.read_excel('ventas.xlsx')

# Columna calculada: venta total por fila
df['venta_total'] = df['cantidad'] * df['precio_unit']

print("\n=== VENTAS POR LOCAL ===")
por_local = df.groupby('local')['venta_total'].sum().sort_values(ascending=False)
print(por_local)

print("\n=== VENTAS POR PRODUCTO ===")
por_producto = df.groupby('producto').agg(
    unidades=('cantidad', 'sum'),
    ingresos=('venta_total', 'sum')
).sort_values('ingresos', ascending=False)
print(por_producto)

print("\n=== PRODUCTOS CON MENOS DE 10 UNIDADES VENDIDAS ===")
poco_movimiento = df.groupby('producto')['cantidad'].sum()
print(poco_movimiento[poco_movimiento < 10])

# Guardar reporte en Excel
reporte = df.groupby('local')['venta_total'].sum().reset_index()
reporte.columns = ['Local', 'Venta Total']
reporte.to_excel('reporte_ventas.xlsx', index=False)
print("\n✓ reporte_ventas.xlsx generado")