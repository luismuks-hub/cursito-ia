# ─── EJERCICIO 9 ─── Farmacia Universal ───
# Simula una tabla de productos con 4 registros
# y calcula el valor total del inventario

productos = [
    {'codigo': 'MET850', 'nombre': 'Metformina 850mg',
     'precio': 12.50, 'stock': 240},
    {'codigo': 'ENA10',  'nombre': 'Enalapril 10mg',
     'precio': 8.90,  'stock': 85},
    {'codigo': 'ATO20',  'nombre': 'Atorvastatina 20mg',
     'precio': 15.30, 'stock': 120},
    {'codigo': 'AMO500', 'nombre': 'Amoxicilina 500mg',
     'precio': 6.80,  'stock': 310},
]

# Calcula valor de inventario por producto
print("=== INVENTARIO FARMACIA UNIVERSAL ===")
print(f"{'Producto':<25} {'Stock':>8} {'Precio':>10} {'Valor':>12}")
print("-" * 58)

total_inventario = 0

for p in productos:
    valor = p['precio'] * p['stock']
    total_inventario += valor
    print(f"{p['nombre']:<25} {p['stock']:>8} "
          f"S/.{p['precio']:>8.2f} S/.{valor:>10.2f}")

print("-" * 58)
print(f"{'TOTAL INVENTARIO':>44} S/.{total_inventario:>10.2f}")

# Identifica productos con stock crítico
print("\n=== ALERTAS DE STOCK ===")
for p in productos:
    if p['stock'] < 100:
        print(f"⚠ STOCK BAJO: {p['nombre']} — {p['stock']} unidades")