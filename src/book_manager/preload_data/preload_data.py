"""Datos de ejemplo del sistema. Genera los CSV de origen en migrations/csv.

Estos archivos son la fuente de la migración a la base de datos (migrations.py).
"""
import csv
import datetime
import os
from decimal import Decimal
from typing import Dict, List

RUTA_CSV_DEFECTO = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "migrations", "csv")

ARCHIVOS: List[str] = [
    "generos.csv", "editoriales.csv", "monedas.csv", "tipos_cotizacion.csv",
    "libros.csv", "precios.csv", "stock.csv", "cotizaciones.csv"]

GENEROS = ["Novela", "Cuento", "Ensayo", "Infantil", "Técnico", "Poesía",
           "Historia", "Ciencia ficción", "Biografía", "Policial"]

EDITORIALES = [
    ("Sudamericana", "Argentina"), ("Planeta", "España"), ("Alfaguara", "España"),
    ("Anagrama", "España"), ("Siglo XXI Editores", "Argentina"),
    ("Fondo de Cultura Económica", "México"), ("Eudeba", "Argentina"),
    ("Alianza Editorial", "España"), ("Kapelusz", "Argentina"),
    ("Penguin Random House", "Estados Unidos")]

MONEDAS = [
    ("ARS", "Peso argentino", "$"), ("USD", "Dólar estadounidense", "US$"),
    ("EUR", "Euro", "€"), ("BRL", "Real brasileño", "R$"),
    ("CLP", "Peso chileno", "CLP$"), ("UYU", "Peso uruguayo", "$U"),
    ("GBP", "Libra esterlina", "£"), ("CHF", "Franco suizo", "CHF"),
    ("JPY", "Yen japonés", "¥"), ("MXN", "Peso mexicano", "MX$")]

TIPOS_COTIZACION = ["Oficial", "Blue", "MEP", "CCL", "Mayorista",
                    "Tarjeta", "Cripto", "Banco Nación", "Promedio", "Turista"]

# (título, autor, id_género, id_editorial, precio_usd, stock)
LIBROS = [
    ("Rayuela", "Julio Cortázar", 1, 1, "18.50", 12),
    ("El Aleph", "Jorge Luis Borges", 2, 8, "15.00", 3),
    ("Martín Fierro", "José Hernández", 6, 9, "9.90", 25),
    ("Sobre héroes y tumbas", "Ernesto Sábato", 1, 2, "16.75", 7),
    ("El Principito", "Antoine de Saint-Exupéry", 4, 3, "11.20", 30),
    ("Clean Code", "Robert C. Martin", 5, 10, "42.00", 4),
    ("Fundación", "Isaac Asimov", 8, 4, "17.30", 9),
    ("Los siete locos", "Roberto Arlt", 1, 7, "13.40", 0),
    ("Breve historia de los argentinos", "Félix Luna", 7, 2, "14.60", 15),
    ("Las venas abiertas de América Latina", "Eduardo Galeano", 3, 5, "19.80", 6),
    ("Ficciones", "Jorge Luis Borges", 2, 6, "14.10", 18),
    ("El nombre de la rosa", "Umberto Eco", 10, 10, "21.90", 2)]

# id_libro -> precio en pesos (solo algunos libros tienen precio fijo en ARS)
PRECIOS_ARS = {1: "25000", 3: "14500", 5: "16800", 6: "62000"}

FECHA_INICIAL = datetime.date(2026, 9, 28)

# id_tipo -> [(compra, venta)] por día consecutivo desde FECHA_INICIAL (valores ficticios)
COTIZACIONES = {
    1: [("1380", "1430"), ("1385", "1435"), ("1390", "1440"), ("1395", "1445")],
    2: [("1450", "1470"), ("1455", "1475"), ("1460", "1480"), ("1465", "1490")],
    3: [("1440", "1445"), ("1442", "1448"), ("1447", "1452"), ("1450", "1455")]}


def _isbn13(base: str) -> str:
    """Completa 12 dígitos con el dígito verificador de un ISBN-13."""
    suma = sum(int(digito) * (1 if posicion % 2 == 0 else 3)
               for posicion, digito in enumerate(base))
    return base + str((10 - suma % 10) % 10)


def _tiene_datos(ruta_csv: str) -> bool:
    """Indica si el archivo de libros ya tiene registros además del encabezado."""
    ruta = os.path.join(ruta_csv, "libros.csv")
    if not os.path.exists(ruta):
        return False
    with open(ruta, encoding="utf-8") as archivo:
        return sum(1 for _ in archivo) > 1


def _escribir(ruta_csv: str, nombre: str, campos: List[str],
              filas: List[Dict[str, object]]) -> None:
    """Escribe un archivo CSV con encabezado."""
    with open(os.path.join(ruta_csv, nombre), "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(filas)


def precargar_datos(ruta_csv: str = RUTA_CSV_DEFECTO, forzar: bool = False) -> bool:
    """Genera los CSV con datos de ejemplo.

    Args:
        ruta_csv: carpeta donde se escriben los archivos.
        forzar: si es True, vuelve a generar los archivos aunque ya existan datos.

    Returns:
        True si generó los archivos, False si ya existían y no se tocaron.
    """
    if _tiene_datos(ruta_csv) and not forzar:
        return False
    os.makedirs(ruta_csv, exist_ok=True)

    _escribir(ruta_csv, "generos.csv", ["id", "nombre"],
              [{"id": i, "nombre": n} for i, n in enumerate(GENEROS, start=1)])
    _escribir(ruta_csv, "editoriales.csv", ["id", "nombre", "pais"],
              [{"id": i, "nombre": n, "pais": p}
               for i, (n, p) in enumerate(EDITORIALES, start=1)])
    _escribir(ruta_csv, "monedas.csv", ["id", "codigo", "nombre", "simbolo"],
              [{"id": i, "codigo": c, "nombre": n, "simbolo": s}
               for i, (c, n, s) in enumerate(MONEDAS, start=1)])
    _escribir(ruta_csv, "tipos_cotizacion.csv", ["id", "nombre"],
              [{"id": i, "nombre": n} for i, n in enumerate(TIPOS_COTIZACION, start=1)])

    libros, precios, stock = [], [], []
    for id_libro, (titulo, autor, id_genero, id_editorial, precio_usd, cantidad) in enumerate(
            LIBROS, start=1):
        libros.append({"id": id_libro, "isbn": _isbn13(f"978950{id_libro:06d}"),
                       "titulo": titulo, "autor": autor,
                       "editorial_id": id_editorial, "genero_id": id_genero})
        precios.append({"id": len(precios) + 1, "libro_id": id_libro, "moneda_id": 2,
                        "valor": precio_usd})
        if id_libro in PRECIOS_ARS:
            precios.append({"id": len(precios) + 1, "libro_id": id_libro, "moneda_id": 1,
                            "valor": PRECIOS_ARS[id_libro]})
        stock.append({"libro_id": id_libro, "cantidad": cantidad})
    _escribir(ruta_csv, "libros.csv",
              ["id", "isbn", "titulo", "autor", "editorial_id", "genero_id"], libros)
    _escribir(ruta_csv, "precios.csv", ["id", "libro_id", "moneda_id", "valor"], precios)
    _escribir(ruta_csv, "stock.csv", ["libro_id", "cantidad"], stock)

    cotizaciones = []
    for id_tipo, valores in COTIZACIONES.items():
        for dias, (compra, venta) in enumerate(valores):
            fecha = FECHA_INICIAL + datetime.timedelta(days=dias)
            cotizaciones.append({"tipo_id": id_tipo, "fecha": fecha.isoformat(),
                                 "valor_compra": Decimal(compra), "valor_venta": Decimal(venta)})
    _escribir(ruta_csv, "cotizaciones.csv",
              ["tipo_id", "fecha", "valor_compra", "valor_venta"], cotizaciones)
    return True
