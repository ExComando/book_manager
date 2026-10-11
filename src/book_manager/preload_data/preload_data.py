"""Datos de ejemplo del sistema. Genera los CSV en migrations/csv."""
import datetime
import os
from decimal import Decimal
from typing import List

from book_manager.entities.entities import (
    CotizacionDolar, Editorial, Genero, Libro, Moneda, Precio, Stock, TipoCotizacion)
from book_manager.repositories.repositories import (
    RUTA_CSV_DEFECTO, RepositorioCotizacionDolar, RepositorioEditorial,
    RepositorioGenero, RepositorioLibro, RepositorioMoneda, RepositorioPrecio,
    RepositorioStock, RepositorioTipoCotizacion)

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


def precargar_datos(ruta_csv: str = RUTA_CSV_DEFECTO, forzar: bool = False) -> bool:
    """Genera los CSV con datos de ejemplo.

    Args:
        ruta_csv: carpeta donde se escriben los archivos.
        forzar: si es True, borra los datos existentes y los vuelve a generar.

    Returns:
        True si cargó los datos, False si ya existían y no se tocaron.
    """
    if _tiene_datos(ruta_csv) and not forzar:
        return False
    for nombre in ARCHIVOS:
        ruta = os.path.join(ruta_csv, nombre)
        if os.path.exists(ruta):
            os.remove(ruta)

    repo_genero = RepositorioGenero(os.path.join(ruta_csv, "generos.csv"))
    repo_editorial = RepositorioEditorial(os.path.join(ruta_csv, "editoriales.csv"))
    repo_moneda = RepositorioMoneda(os.path.join(ruta_csv, "monedas.csv"))
    repo_tipo = RepositorioTipoCotizacion(os.path.join(ruta_csv, "tipos_cotizacion.csv"))
    repo_libro = RepositorioLibro(repo_editorial, repo_genero,
                                  os.path.join(ruta_csv, "libros.csv"))
    repo_precio = RepositorioPrecio(repo_libro, repo_moneda,
                                    os.path.join(ruta_csv, "precios.csv"))
    repo_stock = RepositorioStock(repo_libro, os.path.join(ruta_csv, "stock.csv"))
    repo_cotizacion = RepositorioCotizacionDolar(repo_tipo,
                                                 os.path.join(ruta_csv, "cotizaciones.csv"))

    for id_genero, nombre in enumerate(GENEROS, start=1):
        repo_genero.crear(Genero(id_genero, nombre))
    for id_editorial, (nombre, pais) in enumerate(EDITORIALES, start=1):
        repo_editorial.crear(Editorial(id_editorial, nombre, pais))
    for id_moneda, (codigo, nombre, simbolo) in enumerate(MONEDAS, start=1):
        repo_moneda.crear(Moneda(id_moneda, codigo, nombre, simbolo))
    for id_tipo, nombre in enumerate(TIPOS_COTIZACION, start=1):
        repo_tipo.crear(TipoCotizacion(id_tipo, nombre))

    ars = repo_moneda.leer_por_id(1)
    usd = repo_moneda.leer_por_id(2)
    id_precio = 1
    for id_libro, (titulo, autor, id_genero, id_editorial, precio_usd, cantidad) in enumerate(
            LIBROS, start=1):
        isbn = _isbn13(f"978950{id_libro:06d}")
        libro = repo_libro.crear(Libro(
            id_libro, isbn, titulo, autor,
            repo_editorial.leer_por_id(id_editorial), repo_genero.leer_por_id(id_genero)))
        repo_precio.crear(Precio(id_precio, libro, usd, precio_usd))
        id_precio += 1
        if id_libro in PRECIOS_ARS:
            repo_precio.crear(Precio(id_precio, libro, ars, PRECIOS_ARS[id_libro]))
            id_precio += 1
        repo_stock.crear(Stock(libro, cantidad))

    for id_tipo, valores in COTIZACIONES.items():
        tipo = repo_tipo.leer_por_id(id_tipo)
        for dias, (compra, venta) in enumerate(valores):
            fecha = FECHA_INICIAL + datetime.timedelta(days=dias)
            repo_cotizacion.crear(CotizacionDolar(tipo, fecha, Decimal(compra), Decimal(venta)))
    return True
