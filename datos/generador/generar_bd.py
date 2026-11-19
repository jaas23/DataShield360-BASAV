# -*- coding: utf-8 -*-
"""
Generador de datos ficticios - Distribuidora Andina Comercial S.A.C.
Proyecto final: Base de Datos Avanzadas y Big Data (CIIN1487R) - UPN 2026-2

Genera un script T-SQL que crea la base de datos OLTP "DistribuidoraAndina"
y la llena con datos FICTICIOS (semilla fija = reproducible).

Uso:  python3 generar_bd.py [ruta_salida.sql]
"""
import random
import sys
from datetime import date, datetime, timedelta, time
from decimal import Decimal, ROUND_HALF_UP
from itertools import accumulate

SEMILLA = 2026
rng = random.Random(SEMILLA)

FECHA_INI = date(2024, 1, 1)
FECHA_FIN = date(2026, 10, 31)          # corte de datos
VENTAS_OBJETIVO = 360000                # aprox. cabeceras de venta (pedidos de reposición semanales)
IGV = Decimal("0.18")

def d2(x):
    return Decimal(x).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

# ---------------------------------------------------------------------------
# 1. Datos maestros
# ---------------------------------------------------------------------------
SUCURSALES = [
    # id, codigo, nombre, ciudad, region, direccion, telefono, apertura, peso_ventas
    (1, "LIM", "Sede Central Lima", "Lima", "Lima", "Av. Nicolás Ayllón 4520, Ate", "01-3567890", date(2012, 3, 1), 0.50),
    (2, "AQP", "Sucursal Arequipa", "Arequipa", "Arequipa", "Av. Parra 315, Cercado", "054-281234", date(2016, 8, 15), 0.25),
    (3, "TRU", "Sucursal Trujillo", "Trujillo", "La Libertad", "Av. América Norte 1420, Trujillo", "044-294567", date(2017, 5, 2), 0.25),
]

DISTRITOS = {
    1: ["Ate", "San Juan de Lurigancho", "Comas", "Los Olivos", "San Martín de Porres", "Villa El Salvador",
        "Santiago de Surco", "La Victoria", "Chorrillos", "Independencia", "San Juan de Miraflores", "Puente Piedra",
        "Santa Anita", "El Agustino"],
    2: ["Arequipa", "Cayma", "Cerro Colorado", "Paucarpata", "José Luis Bustamante y Rivero", "Mariano Melgar",
        "Miraflores", "Socabaya", "Yanahuara", "Jacobo Hunter", "Alto Selva Alegre"],
    3: ["Trujillo", "La Esperanza", "El Porvenir", "Víctor Larco Herrera", "Florencia de Mora", "Huanchaco",
        "Moche", "Laredo"],
}

CALLES = ["Av. Los Incas", "Jr. Junín", "Av. España", "Calle Los Pinos", "Jr. Bolívar", "Av. Perú", "Calle San Martín",
          "Av. Túpac Amaru", "Jr. Ayacucho", "Av. Grau", "Calle Las Flores", "Av. Mansiche", "Jr. Unión",
          "Av. Ejército", "Calle Mercaderes", "Av. Larco", "Jr. Huáscar", "Av. Industrial", "Calle Lima", "Av. Arequipa"]

CATEGORIAS = [
    (1, "Lácteos", "Leches, yogures, quesos y derivados"),
    (2, "Bebidas", "Gaseosas, aguas, jugos y bebidas rehidratantes"),
    (3, "Abarrotes", "Arroz, azúcar, fideos, harinas y menestras"),
    (4, "Aceites y conservas", "Aceites comestibles, conservas y salsas"),
    (5, "Limpieza", "Detergentes, lejías y productos de limpieza del hogar"),
    (6, "Cuidado personal", "Higiene y cuidado personal"),
    (7, "Snacks y golosinas", "Galletas, chocolates, piqueos y golosinas"),
    (8, "Desayuno y panadería", "Café, cocoa, avena, mermeladas, pan y panetones"),
]

# categoria, nombre, marca, presentacion, unidad, precio_base_2024 (sin IGV), popularidad
PRODUCTOS = [
    (1, "Leche evaporada entera", "Gloria", "Lata 400 g", "UND", 3.20, 10),
    (1, "Leche evaporada light", "Laive", "Lata 400 g", "UND", 3.00, 5),
    (1, "Leche UHT entera", "Gloria", "Caja 1 L", "UND", 4.20, 6),
    (1, "Yogurt bebible fresa", "Gloria", "Botella 1 L", "UND", 5.90, 5),
    (1, "Yogurt bebible durazno", "Laive", "Botella 1 L", "UND", 5.50, 3),
    (1, "Queso fresco", "Bonlé", "Paquete 500 g", "UND", 12.50, 2),
    (1, "Mantequilla con sal", "Laive", "Barra 200 g", "UND", 7.80, 2),
    (1, "Leche condensada", "Nestlé", "Lata 393 g", "UND", 5.40, 3),
    (2, "Gaseosa Inca Kola", "Inca Kola", "Botella 1.5 L", "UND", 5.20, 10),
    (2, "Gaseosa Coca-Cola", "Coca-Cola", "Botella 1.5 L", "UND", 5.20, 9),
    (2, "Gaseosa Inca Kola personal", "Inca Kola", "Botella 500 ml", "UND", 2.20, 8),
    (2, "Agua sin gas", "San Luis", "Botella 625 ml", "UND", 1.30, 8),
    (2, "Agua sin gas familiar", "Cielo", "Botella 2.5 L", "UND", 2.60, 5),
    (2, "Gaseosa Guaraná", "Backus", "Botella 1.5 L", "UND", 3.80, 4),
    (2, "Néctar de durazno", "Frugos del Valle", "Caja 1 L", "UND", 3.90, 4),
    (2, "Bebida rehidratante", "Sporade", "Botella 500 ml", "UND", 2.10, 5),
    (2, "Bebida rehidratante", "Gatorade", "Botella 500 ml", "UND", 2.80, 3),
    (2, "Gaseosa Kola Real", "Kola Real", "Botella 3 L", "UND", 5.50, 5),
    (2, "Bebida energizante", "Volt", "Botella 300 ml", "UND", 1.60, 5),
    (3, "Arroz extra", "Costeño", "Bolsa 5 kg", "UND", 18.50, 9),
    (3, "Arroz superior", "Paisana", "Bolsa 5 kg", "UND", 17.20, 7),
    (3, "Azúcar rubia", "Dulfina", "Bolsa 1 kg", "UND", 3.60, 8),
    (3, "Fideo spaghetti", "Don Vittorio", "Bolsa 500 g", "UND", 2.90, 6),
    (3, "Fideo tallarín", "Molitalia", "Bolsa 500 g", "UND", 2.60, 6),
    (3, "Harina sin preparar", "Blanca Flor", "Bolsa 1 kg", "UND", 4.30, 3),
    (3, "Sal de mesa yodada", "Emsal", "Bolsa 1 kg", "UND", 1.40, 4),
    (3, "Lenteja bebé", "Costeño", "Bolsa 500 g", "UND", 4.20, 3),
    (3, "Frijol canario", "Costeño", "Bolsa 500 g", "UND", 5.30, 3),
    (4, "Aceite vegetal", "Primor", "Botella 1 L", "UND", 8.90, 8),
    (4, "Aceite vegetal", "Cocinero", "Botella 1 L", "UND", 7.80, 6),
    (4, "Aceite vegetal", "Sao", "Botella 1 L", "UND", 6.90, 4),
    (4, "Atún filete en aceite", "Florida", "Lata 140 g", "UND", 5.20, 5),
    (4, "Atún en trozos", "Campomar", "Lata 170 g", "UND", 4.40, 4),
    (4, "Durazno en almíbar", "Aconcagua", "Lata 820 g", "UND", 7.20, 2),
    (4, "Mayonesa", "Alacena", "Doypack 475 g", "UND", 8.50, 4),
    (4, "Ketchup", "Alacena", "Doypack 400 g", "UND", 5.60, 3),
    (5, "Detergente en polvo", "Ariel", "Bolsa 2 kg", "UND", 24.50, 4),
    (5, "Detergente en polvo", "Bolívar", "Bolsa 2.6 kg", "UND", 25.90, 4),
    (5, "Detergente en polvo", "Opal", "Bolsa 2.6 kg", "UND", 19.90, 3),
    (5, "Lejía tradicional", "Clorox", "Botella 1 L", "UND", 3.20, 5),
    (5, "Jabón de lavar", "Bolívar", "Barra 210 g", "UND", 2.40, 5),
    (5, "Lavavajilla en pasta", "Ayudín", "Pote 900 g", "UND", 6.80, 4),
    (5, "Limpiador multiuso", "Poett", "Botella 900 ml", "UND", 4.90, 3),
    (6, "Papel higiénico doble hoja", "Suave", "Paquete 4 rollos", "UND", 5.90, 6),
    (6, "Shampoo", "Head & Shoulders", "Frasco 375 ml", "UND", 15.90, 2),
    (6, "Pasta dental", "Colgate", "Tubo 75 ml", "UND", 4.20, 4),
    (6, "Jabón antibacterial", "Protex", "Barra 110 g", "UND", 3.10, 4),
    (6, "Desodorante aerosol", "Rexona", "Spray 150 ml", "UND", 9.90, 2),
    (6, "Pañales talla G", "Huggies", "Paquete 50 und", "UND", 49.90, 2),
    (6, "Toallas higiénicas", "Nosotras", "Paquete 10 und", "UND", 4.50, 3),
    (7, "Galleta soda", "Field", "Paquete 6 und", "UND", 3.20, 6),
    (7, "Galleta Casino", "Field", "Paquete 6 und", "UND", 3.40, 4),
    (7, "Galleta Oreo", "Oreo", "Paquete 6 und", "UND", 4.50, 4),
    (7, "Papas fritas clásicas", "Lay's", "Bolsa 42 g", "UND", 1.60, 5),
    (7, "Chizitos", "Karinto", "Bolsa 70 g", "UND", 1.80, 4),
    (7, "Chocolate Sublime", "D'Onofrio", "Barra 30 g", "UND", 1.60, 6),
    (7, "Chocolate Triángulo", "D'Onofrio", "Barra 30 g", "UND", 1.60, 3),
    (7, "Galleta Doña Pepa", "Field", "Paquete 1 und", "UND", 1.30, 4),
    (8, "Café instantáneo", "Altomayo", "Frasco 50 g", "UND", 8.90, 3),
    (8, "Café instantáneo", "Nescafé", "Frasco 50 g", "UND", 9.50, 3),
    (8, "Cocoa", "Winter's", "Bolsa 160 g", "UND", 4.80, 2),
    (8, "Avena precocida", "3 Ositos", "Bolsa 500 g", "UND", 3.90, 4),
    (8, "Mermelada de fresa", "Fanny", "Frasco 320 g", "UND", 5.60, 2),
    (8, "Pan de molde blanco", "Bimbo", "Bolsa 560 g", "UND", 7.90, 4),
    (8, "Panetón clásico", "D'Onofrio", "Caja 900 g", "UND", 24.90, 0),   # estacional
    (8, "Panetón clásico", "Todinno", "Caja 900 g", "UND", 19.90, 0),     # estacional
]
PANETONES = {i + 1 for i, p in enumerate(PRODUCTOS) if p[1].startswith("Panetón")}

NOMBRES_M = ["José", "Luis", "Carlos", "Juan", "Jorge", "Miguel", "Víctor", "César", "Pedro", "Javier", "Raúl",
             "Manuel", "Alberto", "Ricardo", "Fernando", "Óscar", "Walter", "Edwin", "Henry", "Wilmer", "Percy",
             "Hugo", "Diego", "Renzo", "Kevin", "Anthony", "Jhon", "Franco", "Sebastián", "Marco"]
NOMBRES_F = ["María", "Rosa", "Ana", "Carmen", "Juana", "Luz", "Elena", "Gladys", "Patricia", "Milagros", "Sofía",
             "Lucía", "Rocío", "Karina", "Diana", "Jessica", "Flor", "Yolanda", "Silvia", "Teresa", "Valeria",
             "Fiorella", "Katherine", "Liliana", "Mónica", "Pilar", "Nancy", "Erika", "Giuliana", "Sandra"]
APELLIDOS = ["Quispe", "Flores", "Sánchez", "Rodríguez", "García", "Rojas", "Mendoza", "Huamán", "Mamani", "Vásquez",
             "Chávez", "Ramírez", "Torres", "Díaz", "Castillo", "Gutiérrez", "Ramos", "Espinoza", "Reyes", "Vargas",
             "Cruz", "Paredes", "Salazar", "Romero", "Medina", "Gonzales", "Cárdenas", "Alvarado", "Rivera", "Silva",
             "León", "Tapia", "Ruiz", "Benites", "Carranza", "Zavaleta", "Polo", "Valderrama", "Asto", "Ccori",
             "Apaza", "Condori", "Llerena", "Zegarra", "Neyra", "Pinto", "Cabrera", "Moreno", "Aguilar", "Linares"]
FANTASIA = ["Santa Rosa", "El Sol", "San Martín", "Los Andes", "La Esperanza", "Virgen de la Puerta", "El Chalán",
            "San Judas Tadeo", "Señor de los Milagros", "La Económica", "El Ahorro", "Mi Barrio", "Don Lucho",
            "Doña Carmen", "El Paisa", "Los Ángeles", "Nueva Era", "El Triunfo", "La Fortuna", "San Pedro",
            "El Norteño", "Misti", "Chachani", "Huanchaquito", "Moche", "Chan Chan", "Pachacútec", "Inca", "Sumaq",
            "Kusi", "Ayni", "Wari", "La Familia", "Bendición", "Emanuel", "Jireh", "Dos Hermanos", "Tres Estrellas"]

def persona():
    if rng.random() < 0.5:
        n = rng.choice(NOMBRES_M)
    else:
        n = rng.choice(NOMBRES_F)
    return n, f"{rng.choice(APELLIDOS)} {rng.choice(APELLIDOS)}"

dnis_usados = set()
def nuevo_dni():
    while True:
        d = str(rng.randint(10_000_000, 79_999_999))
        if d not in dnis_usados:
            dnis_usados.add(d)
            return d

def ruc_valido(base10):
    """Calcula el dígito verificador del RUC (módulo 11, algoritmo SUNAT)."""
    pesos = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
    s = sum(int(c) * p for c, p in zip(base10, pesos))
    dv = 11 - (s % 11)
    if dv == 10:
        dv = 0
    elif dv == 11:
        dv = 1
    return base10 + str(dv)

rucs_usados = set()
def nuevo_ruc(prefijo):
    while True:
        if prefijo == "10":
            base = "10" + nuevo_dni()                       # RUC 10 = persona natural con negocio (10 + DNI)
        else:
            base = "20" + str(rng.randint(10_000_000, 99_999_999))
        r = ruc_valido(base)
        if r not in rucs_usados:
            rucs_usados.add(r)
            return r

def telefono(sucursal_id):
    return "9" + str(rng.randint(10_000_000, 99_999_999))

def placa():
    letras = "ABCDFGHJKMNPRTVWXYZ"
    return f"{rng.choice(letras)}{rng.randint(1,9)}{rng.choice(letras)}-{rng.randint(100,999)}"

# ---- Empleados ----
EMPLEADOS = []   # id, dni, nombres, apellidos, cargo, sucursal, fecha_ingreso, email
plantilla = {1: {"Vendedor": 12, "Supervisor de ventas": 2, "Almacenero": 4, "Chofer": 6, "Administrador": 1},
             2: {"Vendedor": 7, "Supervisor de ventas": 1, "Almacenero": 2, "Chofer": 4, "Administrador": 1},
             3: {"Vendedor": 7, "Supervisor de ventas": 1, "Almacenero": 2, "Chofer": 4, "Administrador": 1}}
eid = 0
emails_usados = set()
for suc, cargos in plantilla.items():
    for cargo, n in cargos.items():
        for _ in range(n):
            eid += 1
            nom, ape = persona()
            base_mail = f"{nom.split()[0].lower()}.{ape.split()[0].lower()}"
            for a, b in zip("áéíóúñ", "aeioun"):
                base_mail = base_mail.replace(a, b)
            mail = base_mail
            k = 1
            while mail in emails_usados:
                k += 1
                mail = f"{base_mail}{k}"
            emails_usados.add(mail)
            ingreso = date(2015, 1, 1) + timedelta(days=rng.randint(0, (date(2023, 12, 1) - date(2015, 1, 1)).days))
            EMPLEADOS.append((eid, nuevo_dni(), nom, ape, cargo, suc, ingreso, f"{mail}@distandina.com.pe"))

VENDEDORES = {s: [e[0] for e in EMPLEADOS if e[5] == s and e[4] == "Vendedor"] for s in (1, 2, 3)}
CHOFERES = {s: [e[0] for e in EMPLEADOS if e[5] == s and e[4] == "Chofer"] for s in (1, 2, 3)}
FLOTA = {s: [placa() for _ in range(len(CHOFERES[s]))] for s in (1, 2, 3)}

# ---- Clientes ----
TIPOS_CLIENTE = [  # tipo, prob, rango_cantidad, descuento_pct, frecuencia_relativa
    ("Bodega", 0.45, (4, 14), 0, 1.0),         # cantidades por línea de un pedido de reposición
    ("Minimarket", 0.20, (8, 24), 0, 1.6),
    ("Restaurante", 0.10, (4, 16), 0, 1.2),
    ("Persona natural", 0.15, (2, 6), 0, 0.4),
    ("Supermercado", 0.04, (12, 40), 3, 2.0),   # pedidos grandes, menos frecuentes
    ("Mayorista", 0.06, (24, 72), 5, 2.0),
]
TIPO_INFO = {t[0]: t for t in TIPOS_CLIENTE}
CLIENTES_POR_SUC = {1: 1200, 2: 600, 3: 600}

def ensuciar(texto):
    """Introduce inconsistencias de formato (para reglas de limpieza en el ETL)."""
    r = rng.random()
    if r < 0.35:
        return texto.upper()
    if r < 0.65:
        return texto.lower()
    if r < 0.85:
        return "  " + texto + " "
    return texto.upper() + "  "

CLIENTES = []  # id, tipo_doc, num_doc, razon, tipo_cliente, sucursal, distrito, direccion, tel, email, fecha_reg, peso
cid = 0
for suc, n in CLIENTES_POR_SUC.items():
    for _ in range(n):
        cid += 1
        tipo = rng.choices([t[0] for t in TIPOS_CLIENTE], [t[1] for t in TIPOS_CLIENTE])[0]
        nom, ape = persona()
        if tipo == "Persona natural":
            tdoc, ndoc, razon = "DNI", nuevo_dni(), f"{ape} {nom}".upper()
        elif tipo == "Bodega" and rng.random() < 0.7:
            tdoc, ndoc = "RUC", nuevo_ruc("10")
            razon = f"{ape} {nom}".upper()
        else:
            tdoc, ndoc = "RUC", nuevo_ruc("20")
            fant = rng.choice(FANTASIA)
            sufijo = rng.choice(["S.A.C.", "E.I.R.L.", "S.R.L.", "S.A.C."])
            pref = {"Bodega": "Bodega", "Minimarket": "Minimarket", "Restaurante": "Restaurante",
                    "Supermercado": "Supermercados", "Mayorista": rng.choice(["Distribuidora", "Comercial", "Inversiones"])}[tipo]
            razon = f"{pref} {fant} {ape.split()[0]} {sufijo}".upper()
        if rng.random() < 0.03:
            razon = razon + "   "                       # espacios sobrantes (calidad de datos)
        distrito = rng.choice(DISTRITOS[suc])
        if rng.random() < 0.06:
            distrito = ensuciar(distrito)                # formato inconsistente (calidad de datos)
        direccion = f"{rng.choice(CALLES)} {rng.randint(100, 3999)}"
        tel = telefono(suc) if rng.random() > 0.08 else None
        email = None
        if rng.random() > 0.25:
            u = razon.split()[0].lower() + str(rng.randint(10, 9999))
            for a, b in zip("áéíóúñ", "aeioun"):
                u = u.replace(a, b)
            email = f"{u}@{rng.choice(['gmail.com', 'hotmail.com', 'outlook.com', 'yahoo.es'])}"
        if rng.random() < 0.8:
            freg = date(2019, 1, 1) + timedelta(days=rng.randint(0, (date(2023, 12, 31) - date(2019, 1, 1)).days))
        else:
            freg = FECHA_INI + timedelta(days=rng.randint(0, (date(2026, 6, 30) - FECHA_INI).days))
        peso = rng.lognormvariate(0, 0.8) * TIPO_INFO[tipo][4]
        CLIENTES.append((cid, tdoc, ndoc, razon, tipo, suc, distrito, direccion, tel, email, freg, peso))

# ---------------------------------------------------------------------------
# 2. Ventas, detalle y despachos
# ---------------------------------------------------------------------------
ESTACION_MES = {1: 0.95, 2: 0.85, 3: 0.92, 4: 0.95, 5: 1.00, 6: 1.00, 7: 1.15, 8: 1.00, 9: 0.97, 10: 1.02, 11: 1.12, 12: 1.40}
FACTOR_DIA = {0: 1.05, 1: 1.0, 2: 1.0, 3: 1.0, 4: 1.1, 5: 0.9, 6: 0.12}   # lunes..domingo
FACTOR_ANIO = {2024: 1.00, 2025: 1.12, 2026: 1.22}                        # crecimiento
PRECIO_ANIO = {2024: Decimal("1.000"), 2025: Decimal("1.035"), 2026: Decimal("1.070")}  # inflación

def factor_categoria(cat, mes):
    if cat == 2 and mes in (1, 2, 3, 12):        # bebidas: verano
        return 1.6
    if cat == 7 and mes == 12:                   # snacks/golosinas: Navidad
        return 1.4
    if cat == 1 and mes in (6, 7, 8):            # lácteos: invierno
        return 1.2
    return 1.0

def peso_producto(pid, mes):
    p = PRODUCTOS[pid - 1]
    if pid in PANETONES:
        return {11: 6.0, 12: 14.0, 1: 0.4}.get(mes, 0.05)
    return p[6] * factor_categoria(p[0], mes)

PRODUCTO_IDS = list(range(1, len(PRODUCTOS) + 1))
_cache_prod = {}
def cum_prod(mes):
    if mes not in _cache_prod:
        _cache_prod[mes] = list(accumulate(peso_producto(p, mes) for p in PRODUCTO_IDS))
    return _cache_prod[mes]

# total de "intensidad" para calibrar el volumen diario
dias = []
d = FECHA_INI
while d <= FECHA_FIN:
    dias.append(d)
    d += timedelta(days=1)
intensidad = {d: ESTACION_MES[d.month] * FACTOR_DIA[d.weekday()] * FACTOR_ANIO[d.year] for d in dias}
k_base = VENTAS_OBJETIVO / sum(intensidad.values())

SERIES = {1: ("F001", "B001"), 2: ("F002", "B002"), 3: ("F003", "B003")}
correlativo = {s: 0 for pair in SERIES.values() for s in pair}
METODOS = ["EFECTIVO", "TRANSFERENCIA", "YAPE", "PLIN", "TARJETA", "CREDITO 30 DIAS"]
METODOS_PESO_EMPRESA = [20, 35, 10, 5, 10, 20]
METODOS_PESO_PERSONA = [40, 5, 30, 15, 10, 0]

VENTAS, DETALLES, DESPACHOS = [], [], []
vid = did = dpid = 0
CORTE = datetime(2026, 10, 31, 18, 0, 0)

# clientes elegibles por mes (registrados antes del inicio del mes)
cache_elegibles = {}
def elegibles(suc, d):
    key = (suc, d.year, d.month)
    if key not in cache_elegibles:
        ini_mes = date(d.year, d.month, 1)
        lst = [c for c in CLIENTES if c[5] == suc and c[10] <= ini_mes]
        cache_elegibles[key] = (lst, list(accumulate(c[11] for c in lst)))   # pesos acumulados (más rápido)
    return cache_elegibles[key]

for dia in dias:
    mu = k_base * intensidad[dia]
    n_ventas = max(0, round(rng.gauss(mu, mu ** 0.5)))
    for _ in range(n_ventas):
        suc = rng.choices([1, 2, 3], [s[8] for s in SUCURSALES])[0]
        lst, pesos = elegibles(suc, dia)
        cli = rng.choices(lst, cum_weights=pesos)[0]
        tipo = cli[4]
        _, _, (qmin, qmax), desc_base, _ = TIPO_INFO[tipo]
        vend = rng.choice(VENDEDORES[suc])
        hora = time(rng.randint(8, 18), rng.randint(0, 59), rng.randint(0, 59))
        fecha = datetime.combine(dia, hora)
        es_factura = cli[1] == "RUC"
        serie = SERIES[suc][0] if es_factura else SERIES[suc][1]
        correlativo[serie] += 1
        metodo = rng.choices(METODOS, METODOS_PESO_EMPRESA if es_factura else METODOS_PESO_PERSONA)[0]
        estado = "ANULADA" if rng.random() < 0.015 else "EMITIDA"

        n_items = min(len(PRODUCTO_IDS), 1 + int(rng.expovariate(1 / (2.2 if tipo != "Persona natural" else 0.8))))
        if tipo in ("Supermercado", "Mayorista"):
            n_items = min(len(PRODUCTO_IDS), n_items + rng.randint(3, 8))
        pw = cum_prod(dia.month)
        elegidos = set()
        while len(elegidos) < n_items:
            elegidos.add(rng.choices(PRODUCTO_IDS, cum_weights=pw)[0])
        vid += 1
        subtotal = Decimal("0.00")
        for pid in sorted(elegidos):
            did += 1
            precio = d2(Decimal(str(PRODUCTOS[pid - 1][5])) * PRECIO_ANIO[dia.year])
            cant = rng.randint(qmin, qmax)
            desc = desc_base + (2 if rng.random() < 0.05 else 0)
            st = d2(precio * cant * (Decimal(100 - desc) / 100))
            subtotal += st
            DETALLES.append((did, vid, pid, cant, precio, desc, st))
        igv = d2(subtotal * IGV)
        VENTAS.append((vid, "FACTURA" if es_factura else "BOLETA", serie, correlativo[serie], fecha, cli[0], vend,
                       suc, metodo, subtotal, igv, subtotal + igv, estado))

        # ----- despacho (proceso de distribución) -----
        if estado == "EMITIDA" and (tipo != "Persona natural" or rng.random() < 0.3):
            dpid += 1
            plazo = 1 if suc == 1 else rng.choice([1, 2])
            prog = dia + timedelta(days=plazo)
            if prog.weekday() == 6:
                prog += timedelta(days=1)
            idx = rng.randrange(len(CHOFERES[suc]))
            chofer, plc = CHOFERES[suc][idx], FLOTA[suc][idx]
            r = rng.random()
            atraso = 0 if r < 0.85 else (1 if r < 0.97 else rng.randint(2, 3))
            salida = datetime.combine(prog, time(rng.randint(7, 10), rng.randint(0, 59)))
            entrega = salida + timedelta(days=atraso, minutes=rng.randint(60, 8 * 60))
            if rng.random() < 0.005:
                est_d, salida, entrega = "CANCELADO", None, None
            elif salida > CORTE:
                est_d, salida, entrega = "PENDIENTE", None, None
            elif entrega > CORTE:
                est_d, entrega = "EN RUTA", None
            else:
                est_d = "ENTREGADO"
            dir_ent = f"{cli[7]}, {cli[6].strip().title()}"
            DESPACHOS.append((dpid, vid, chofer, plc, prog, salida, entrega, est_d, dir_ent))

# ---------------------------------------------------------------------------
# 3. Inventario (foto al corte)
# ---------------------------------------------------------------------------
# Stock mínimo = 7 días de venta promedio (ago-oct 2026) de ese producto en esa sede;
# stock máximo = 30 días. Así el inventario es coherente con el volumen de ventas.
from collections import defaultdict
_venta_suc = {v[0]: v[7] for v in VENTAS if v[4] >= datetime(2026, 8, 1) and v[12] == "EMITIDA"}
_unidades = defaultdict(int)
for d_ in DETALLES:
    suc_ = _venta_suc.get(d_[1])
    if suc_:
        _unidades[(suc_, d_[2])] += d_[3]
DIAS_VENTANA = (date(2026, 10, 31) - date(2026, 8, 1)).days + 1
INVENTARIO = []
for s in SUCURSALES:
    for pid in PRODUCTO_IDS:
        diario = _unidades[(s[0], pid)] / DIAS_VENTANA
        minimo = max(10, int(round(diario * 7)))
        maximo = max(minimo * 2, int(round(diario * 30)))
        if rng.random() < 0.10:
            actual = rng.randint(0, max(1, minimo - 1))          # bajo stock -> alertas
        else:
            actual = rng.randint(minimo, maximo)
        INVENTARIO.append((s[0], pid, actual, minimo, maximo, datetime(2026, 10, 31, 20, 0, 0)))

# ---------------------------------------------------------------------------
# 4. Escritura del script T-SQL
# ---------------------------------------------------------------------------
def q(v):
    if v is None:
        return "NULL"
    if isinstance(v, bool):
        return "1" if v else "0"
    if isinstance(v, (int, Decimal)):
        return str(v)
    if isinstance(v, float):
        return f"{v:.2f}"
    if isinstance(v, datetime):
        return "'" + v.strftime("%Y-%m-%dT%H:%M:%S") + "'"
    if isinstance(v, date):
        return "'" + v.strftime("%Y-%m-%d") + "'"
    return "N'" + str(v).replace("'", "''") + "'"

def inserts(out, tabla, columnas, filas, identity=True, lote=1000):
    out.append(f"\n-- ---------- {tabla}: {len(filas):,} filas ----------".replace(",", "."))
    if identity:
        out.append(f"SET IDENTITY_INSERT {tabla} ON;")
    for i in range(0, len(filas), lote):
        bloque = filas[i:i + lote]
        out.append(f"INSERT INTO {tabla} ({', '.join(columnas)}) VALUES")
        out.append(",\n".join("(" + ", ".join(q(v) for v in f) + ")" for f in bloque) + ";")
        if (i // lote) % 10 == 9:
            out.append("GO")
    if identity:
        out.append(f"SET IDENTITY_INSERT {tabla} OFF;")
    out.append("GO")

DDL = r"""/* =====================================================================
   PROYECTO FINAL - BASE DE DATOS AVANZADAS Y BIG DATA (CIIN1487R) - UPN
   Caso: Distribuidora Andina Comercial S.A.C. (empresa FICTICIA)
   Script 01: Creación y carga de la base transaccional (OLTP)

   - Datos 100 % ficticios generados con Python (semilla fija 2026,
     reproducible con generador/generar_bd.py).
   - Periodo de ventas: 2024-01-01 al 2026-10-31.
   - Volumen: ~2 millones de filas (pedidos de reposición semanales).
   - Compatible con SQL Server 2016 o superior.
   - El archivo es grande: SSMS no puede abrirlo. Ejecutar con sqlcmd:
       sqlcmd -S localhost -E -f 65001 -i 01_DistribuidoraAndina_BD.sql
     (la carga tarda varios minutos)
   ===================================================================== */
SET NOCOUNT ON;
USE master;
GO

-- Si la base ya existe, se elimina para recrearla desde cero
IF DB_ID(N'DistribuidoraAndina') IS NOT NULL
BEGIN
    ALTER DATABASE DistribuidoraAndina SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE DistribuidoraAndina;
END
GO

CREATE DATABASE DistribuidoraAndina;
GO
-- Durante la carga masiva se usa SIMPLE (registra menos en el log y es más rápido).
-- Al final del script se cambia a FULL, necesario para los backups de log (paso 3).
ALTER DATABASE DistribuidoraAndina SET RECOVERY SIMPLE;
GO

USE DistribuidoraAndina;
GO

/* ------------------------- TABLAS MAESTRAS ------------------------- */

CREATE TABLE dbo.Sucursal (
    SucursalID      INT IDENTITY(1,1) NOT NULL,
    Codigo          CHAR(3)        NOT NULL,
    Nombre          NVARCHAR(60)   NOT NULL,
    Ciudad          NVARCHAR(40)   NOT NULL,
    Region          NVARCHAR(40)   NOT NULL,
    Direccion       NVARCHAR(120)  NOT NULL,
    Telefono        VARCHAR(15)    NULL,
    FechaApertura   DATE           NOT NULL,
    CONSTRAINT PK_Sucursal PRIMARY KEY (SucursalID),
    CONSTRAINT UQ_Sucursal_Codigo UNIQUE (Codigo)
);

CREATE TABLE dbo.Categoria (
    CategoriaID     INT IDENTITY(1,1) NOT NULL,
    Nombre          NVARCHAR(50)   NOT NULL,
    Descripcion     NVARCHAR(150)  NULL,
    CONSTRAINT PK_Categoria PRIMARY KEY (CategoriaID),
    CONSTRAINT UQ_Categoria_Nombre UNIQUE (Nombre)
);

CREATE TABLE dbo.Producto (
    ProductoID      INT IDENTITY(1,1) NOT NULL,
    SKU             VARCHAR(12)    NOT NULL,
    Nombre          NVARCHAR(80)   NOT NULL,
    CategoriaID     INT            NOT NULL,
    Marca           NVARCHAR(40)   NOT NULL,
    Presentacion    NVARCHAR(40)   NOT NULL,
    UnidadMedida    VARCHAR(5)     NOT NULL,
    PrecioVenta     DECIMAL(10,2)  NOT NULL,   -- precio vigente sin IGV (S/)
    CostoUnitario   DECIMAL(10,2)  NOT NULL,   -- costo vigente (S/)
    Activo          BIT            NOT NULL CONSTRAINT DF_Producto_Activo DEFAULT (1),
    FechaCreacion   DATE           NOT NULL,
    CONSTRAINT PK_Producto PRIMARY KEY (ProductoID),
    CONSTRAINT UQ_Producto_SKU UNIQUE (SKU),
    CONSTRAINT FK_Producto_Categoria FOREIGN KEY (CategoriaID) REFERENCES dbo.Categoria (CategoriaID),
    CONSTRAINT CK_Producto_Precios CHECK (PrecioVenta > 0 AND CostoUnitario > 0 AND CostoUnitario <= PrecioVenta)
);

CREATE TABLE dbo.Cliente (
    ClienteID       INT IDENTITY(1,1) NOT NULL,
    TipoDocumento   VARCHAR(3)     NOT NULL,   -- DNI / RUC
    NumeroDocumento VARCHAR(11)    NOT NULL,
    RazonSocial     NVARCHAR(150)  NOT NULL,
    TipoCliente     NVARCHAR(20)   NOT NULL,
    SucursalID      INT            NOT NULL,   -- sucursal que lo atiende
    Distrito        NVARCHAR(60)   NOT NULL,
    Direccion       NVARCHAR(150)  NOT NULL,
    Telefono        VARCHAR(15)    NULL,
    Email           VARCHAR(100)   NULL,
    FechaRegistro   DATE           NOT NULL,
    Activo          BIT            NOT NULL CONSTRAINT DF_Cliente_Activo DEFAULT (1),
    CONSTRAINT PK_Cliente PRIMARY KEY (ClienteID),
    CONSTRAINT UQ_Cliente_Documento UNIQUE (NumeroDocumento),
    CONSTRAINT FK_Cliente_Sucursal FOREIGN KEY (SucursalID) REFERENCES dbo.Sucursal (SucursalID),
    CONSTRAINT CK_Cliente_TipoDoc CHECK (
        (TipoDocumento = 'DNI' AND LEN(NumeroDocumento) = 8) OR
        (TipoDocumento = 'RUC' AND LEN(NumeroDocumento) = 11)),
    CONSTRAINT CK_Cliente_Tipo CHECK (TipoCliente IN
        (N'Bodega', N'Minimarket', N'Restaurante', N'Persona natural', N'Supermercado', N'Mayorista'))
);

CREATE TABLE dbo.Empleado (
    EmpleadoID      INT IDENTITY(1,1) NOT NULL,
    DNI             CHAR(8)        NOT NULL,
    Nombres         NVARCHAR(60)   NOT NULL,
    Apellidos       NVARCHAR(60)   NOT NULL,
    Cargo           NVARCHAR(30)   NOT NULL,
    SucursalID      INT            NOT NULL,
    FechaIngreso    DATE           NOT NULL,
    Email           VARCHAR(100)   NOT NULL,
    Activo          BIT            NOT NULL CONSTRAINT DF_Empleado_Activo DEFAULT (1),
    CONSTRAINT PK_Empleado PRIMARY KEY (EmpleadoID),
    CONSTRAINT UQ_Empleado_DNI UNIQUE (DNI),
    CONSTRAINT UQ_Empleado_Email UNIQUE (Email),
    CONSTRAINT FK_Empleado_Sucursal FOREIGN KEY (SucursalID) REFERENCES dbo.Sucursal (SucursalID),
    CONSTRAINT CK_Empleado_Cargo CHECK (Cargo IN
        (N'Vendedor', N'Supervisor de ventas', N'Almacenero', N'Chofer', N'Administrador'))
);

/* --------------------- TABLAS TRANSACCIONALES ---------------------- */

CREATE TABLE dbo.Inventario (
    SucursalID          INT        NOT NULL,
    ProductoID          INT        NOT NULL,
    StockActual         INT        NOT NULL,
    StockMinimo         INT        NOT NULL,
    StockMaximo         INT        NOT NULL,
    FechaActualizacion  DATETIME2(0) NOT NULL,
    CONSTRAINT PK_Inventario PRIMARY KEY (SucursalID, ProductoID),
    CONSTRAINT FK_Inventario_Sucursal FOREIGN KEY (SucursalID) REFERENCES dbo.Sucursal (SucursalID),
    CONSTRAINT FK_Inventario_Producto FOREIGN KEY (ProductoID) REFERENCES dbo.Producto (ProductoID),
    CONSTRAINT CK_Inventario_Stock CHECK (StockActual >= 0 AND StockMinimo >= 0 AND StockMaximo >= StockMinimo)
);

CREATE TABLE dbo.Venta (
    VentaID         INT IDENTITY(1,1) NOT NULL,
    TipoComprobante VARCHAR(7)     NOT NULL,   -- FACTURA / BOLETA
    Serie           CHAR(4)        NOT NULL,
    Numero          INT            NOT NULL,
    FechaVenta      DATETIME2(0)   NOT NULL,
    ClienteID       INT            NOT NULL,
    EmpleadoID      INT            NOT NULL,   -- vendedor
    SucursalID      INT            NOT NULL,
    MetodoPago      VARCHAR(20)    NOT NULL,
    Subtotal        DECIMAL(12,2)  NOT NULL,
    IGV             DECIMAL(12,2)  NOT NULL,
    Total           DECIMAL(12,2)  NOT NULL,
    Estado          VARCHAR(10)    NOT NULL CONSTRAINT DF_Venta_Estado DEFAULT ('EMITIDA'),
    CONSTRAINT PK_Venta PRIMARY KEY (VentaID),
    CONSTRAINT UQ_Venta_Comprobante UNIQUE (Serie, Numero),
    CONSTRAINT FK_Venta_Cliente  FOREIGN KEY (ClienteID)  REFERENCES dbo.Cliente (ClienteID),
    CONSTRAINT FK_Venta_Empleado FOREIGN KEY (EmpleadoID) REFERENCES dbo.Empleado (EmpleadoID),
    CONSTRAINT FK_Venta_Sucursal FOREIGN KEY (SucursalID) REFERENCES dbo.Sucursal (SucursalID),
    CONSTRAINT CK_Venta_Tipo   CHECK (TipoComprobante IN ('FACTURA', 'BOLETA')),
    CONSTRAINT CK_Venta_Estado CHECK (Estado IN ('EMITIDA', 'ANULADA')),
    CONSTRAINT CK_Venta_Montos CHECK (Subtotal >= 0 AND IGV >= 0 AND Total = Subtotal + IGV)
);

CREATE TABLE dbo.DetalleVenta (
    DetalleID       INT IDENTITY(1,1) NOT NULL,
    VentaID         INT            NOT NULL,
    ProductoID      INT            NOT NULL,
    Cantidad        INT            NOT NULL,
    PrecioUnitario  DECIMAL(10,2)  NOT NULL,   -- precio sin IGV a la fecha de la venta
    DescuentoPct    DECIMAL(5,2)   NOT NULL CONSTRAINT DF_Detalle_Desc DEFAULT (0),
    Subtotal        DECIMAL(12,2)  NOT NULL,
    CONSTRAINT PK_DetalleVenta PRIMARY KEY (DetalleID),
    CONSTRAINT UQ_Detalle_VentaProducto UNIQUE (VentaID, ProductoID),
    CONSTRAINT FK_Detalle_Venta    FOREIGN KEY (VentaID)    REFERENCES dbo.Venta (VentaID),
    CONSTRAINT FK_Detalle_Producto FOREIGN KEY (ProductoID) REFERENCES dbo.Producto (ProductoID),
    CONSTRAINT CK_Detalle_Valores CHECK (Cantidad > 0 AND PrecioUnitario > 0 AND DescuentoPct BETWEEN 0 AND 100)
);

CREATE TABLE dbo.Despacho (
    DespachoID       INT IDENTITY(1,1) NOT NULL,
    VentaID          INT           NOT NULL,
    ChoferID         INT           NOT NULL,
    PlacaVehiculo    VARCHAR(8)    NOT NULL,
    FechaProgramada  DATE          NOT NULL,
    FechaSalida      DATETIME2(0)  NULL,
    FechaEntrega     DATETIME2(0)  NULL,
    Estado           VARCHAR(10)   NOT NULL,
    DireccionEntrega NVARCHAR(200) NOT NULL,
    CONSTRAINT PK_Despacho PRIMARY KEY (DespachoID),
    CONSTRAINT UQ_Despacho_Venta UNIQUE (VentaID),
    CONSTRAINT FK_Despacho_Venta  FOREIGN KEY (VentaID)  REFERENCES dbo.Venta (VentaID),
    CONSTRAINT FK_Despacho_Chofer FOREIGN KEY (ChoferID) REFERENCES dbo.Empleado (EmpleadoID),
    CONSTRAINT CK_Despacho_Estado CHECK (Estado IN ('PENDIENTE', 'EN RUTA', 'ENTREGADO', 'CANCELADO')),
    CONSTRAINT CK_Despacho_Fechas CHECK (FechaEntrega IS NULL OR FechaEntrega >= FechaSalida)
);
GO
"""

out = [DDL]
inserts(out, "dbo.Sucursal", ["SucursalID", "Codigo", "Nombre", "Ciudad", "Region", "Direccion", "Telefono", "FechaApertura"],
        [s[:8] for s in SUCURSALES])
inserts(out, "dbo.Categoria", ["CategoriaID", "Nombre", "Descripcion"], CATEGORIAS)
prod_rows = []
for i, p in enumerate(PRODUCTOS, start=1):
    precio = d2(Decimal(str(p[5])) * PRECIO_ANIO[2026])
    costo = d2(precio * Decimal(str(rng.uniform(0.72, 0.86))))
    prod_rows.append((i, f"DAC-{p[0]:02d}{i:04d}", f"{p[1]} {p[2]} {p[3]}", p[0], p[2], p[3], p[4], precio, costo, 1,
                      date(2019, 1, 1) + timedelta(days=rng.randint(0, 1700))))
inserts(out, "dbo.Producto", ["ProductoID", "SKU", "Nombre", "CategoriaID", "Marca", "Presentacion", "UnidadMedida",
                              "PrecioVenta", "CostoUnitario", "Activo", "FechaCreacion"], prod_rows)
inserts(out, "dbo.Cliente", ["ClienteID", "TipoDocumento", "NumeroDocumento", "RazonSocial", "TipoCliente", "SucursalID",
                             "Distrito", "Direccion", "Telefono", "Email", "FechaRegistro"], [c[:11] for c in CLIENTES])
inserts(out, "dbo.Empleado", ["EmpleadoID", "DNI", "Nombres", "Apellidos", "Cargo", "SucursalID", "FechaIngreso", "Email"],
        EMPLEADOS)
inserts(out, "dbo.Inventario", ["SucursalID", "ProductoID", "StockActual", "StockMinimo", "StockMaximo", "FechaActualizacion"],
        INVENTARIO, identity=False)
inserts(out, "dbo.Venta", ["VentaID", "TipoComprobante", "Serie", "Numero", "FechaVenta", "ClienteID", "EmpleadoID",
                           "SucursalID", "MetodoPago", "Subtotal", "IGV", "Total", "Estado"], VENTAS)
inserts(out, "dbo.DetalleVenta", ["DetalleID", "VentaID", "ProductoID", "Cantidad", "PrecioUnitario", "DescuentoPct",
                                  "Subtotal"], DETALLES)
inserts(out, "dbo.Despacho", ["DespachoID", "VentaID", "ChoferID", "PlacaVehiculo", "FechaProgramada", "FechaSalida",
                              "FechaEntrega", "Estado", "DireccionEntrega"], DESPACHOS)

out.append(r"""
/* ------------------ MODELO DE RECUPERACIÓN FINAL -------------------- */
USE master;
GO
ALTER DATABASE DistribuidoraAndina SET RECOVERY FULL;
GO
USE DistribuidoraAndina;
GO
""")
out.append(r"""
/* --------------------------- VERIFICACIÓN --------------------------- */
SELECT 'Sucursal' AS Tabla, COUNT(*) AS Filas FROM dbo.Sucursal UNION ALL
SELECT 'Categoria', COUNT(*) FROM dbo.Categoria UNION ALL
SELECT 'Producto', COUNT(*) FROM dbo.Producto UNION ALL
SELECT 'Cliente', COUNT(*) FROM dbo.Cliente UNION ALL
SELECT 'Empleado', COUNT(*) FROM dbo.Empleado UNION ALL
SELECT 'Inventario', COUNT(*) FROM dbo.Inventario UNION ALL
SELECT 'Venta', COUNT(*) FROM dbo.Venta UNION ALL
SELECT 'DetalleVenta', COUNT(*) FROM dbo.DetalleVenta UNION ALL
SELECT 'Despacho', COUNT(*) FROM dbo.Despacho;
GO
""")

salida = sys.argv[1] if len(sys.argv) > 1 else "01_DistribuidoraAndina_BD.sql"
with open(salida, "w", encoding="utf-8-sig", newline="\r\n") as f:
    f.write("\n".join(out))

print(f"Sucursales {len(SUCURSALES)} | Categorías {len(CATEGORIAS)} | Productos {len(PRODUCTOS)} | "
      f"Clientes {len(CLIENTES)} | Empleados {len(EMPLEADOS)} | Inventario {len(INVENTARIO)} | "
      f"Ventas {len(VENTAS)} | Detalles {len(DETALLES)} | Despachos {len(DESPACHOS)}")
