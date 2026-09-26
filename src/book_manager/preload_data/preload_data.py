import csv
import os
from datetime import date
from book_manager.entities.entities import (
    Genero, Editorial, Moneda, TipoCotizacion, Libro, CotizacionDolar, Precio, Stock
)
from book_manager.repositories.repositories import (
    RepositorioLibro, RepositorioGenero, RepositorioEditorial, RepositorioStock, RepositorioCotizacionDolar
)

RUTA_CSV = "src/book_manager/migrations/csv"

def generar_archivos_csv():
    os.makedirs(RUTA_CSV, exist_ok=True)
    
    # Géneros reales
    generos = [
        [1, "Romance"], [2, "Deep Learning"], [3, "Inteligencia Artificial"], [4, "Novela Histórica"],
        [5, "Ciencia Ficción"], [6, "Terror"], [7, "Fantasía"], [8, "Desarrollo Personal"],
        [9, "Thriller"], [10, "Ensayo"]
    ]
    with open(f"{RUTA_CSV}/generos.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id_genero", "nombre"])
        writer.writerows(generos)

    # Editoriales reales
    editoriales = [
        [1, "MIT Press"], [2, "O'Reilly Media"], [3, "Springer"], [4, "Planeta"],
        [5, "Alfaguara"], [6, "Tusquets"], [7, "Manning Publications"], [8, "Packt"],
        [9, "Anagrama"], [10, "Sexto Piso"]
    ]
    with open(f"{RUTA_CSV}/editoriales.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id_editorial", "nombre"])
        writer.writerows(editoriales)

    # Libros reales divididos en Romance e IA/Deep Learning
    libros = [
        ["978-0262035613", "Deep Learning", "Ian Goodfellow", 1, 2],
        ["978-1492032649", "Hands-On Machine Learning", "Aurélien Géron", 2, 3],
        ["978-0387310732", "Pattern Recognition and Machine Learning", "Christopher Bishop", 3, 2],
        ["978-8408193488", "Orgullo y Prejuicio", "Jane Austen", 4, 1],
        ["978-8420412146", "Cumbres Borrascosas", "Emily Brontë", 5, 1],
        ["978-8483832230", "El amor en los tiempos del cólera", "Gabriel García Márquez", 6, 1],
        ["978-1617294433", "Deep Learning with Python", "François Chollet", 7, 2],
        ["978-8415594017", "Bajo la misma estrella", "John Green", 4, 1],
        ["978-0134610993", "Artificial Intelligence: A Modern Approach", "Stuart Russell", 8, 3],
        ["978-8433979435", "Yo antes de ti", "Jojo Moyes", 9, 1]
    ]
    with open(f"{RUTA_CSV}/libros.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["isbn", "titulo", "autor", "id_editorial", "id_genero"])
        writer.writerows(libros)

    monedas = [
        [1, "ARS", "$"], [2, "USD", "u$s"], [3, "EUR", "€"], [4, "GBP", "£"], [5, "BRL", "R$"],
        [6, "CLP", "$"], [7, "UYU", "$U"], [8, "MXN", "$"], [9, "COP", "$"], [10, "PEN", "S/"]
    ]
    with open(f"{RUTA_CSV}/monedas.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id_moneda", "codigo", "simbolo"])
        writer.writerows(monedas)

    tipos_cotizacion = [
        [1, "Oficial"], [2, "Blue"], [3, "MEP"], [4, "CCL"], [5, "Tarjeta"],
        [6, "Cripto"], [7, "Mayorista"], [8, "Minorista"], [9, "Solidario"], [10, "Turista"]
    ]
    with open(f"{RUTA_CSV}/tipos_cotizacion.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id_tipo", "nombre"])
        writer.writerows(tipos_cotizacion)

    cotizaciones = [
        [1, "2026-09-26", 1050.50], [2, "2026-09-26", 1300.00], [3, "2026-09-26", 1250.00],
        [4, "2026-09-26", 1280.00], [5, "2026-09-26", 1600.00], [6, "2026-09-26", 1310.00],
        [7, "2026-09-26", 1040.00], [8, "2026-09-26", 1060.00], [9, "2026-09-26", 1500.00],
        [10, "2026-09-26", 1550.00]
    ]
    with open(f"{RUTA_CSV}/cotizaciones.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id_tipo", "fecha", "valor_venta"])
        writer.writerows(cotizaciones)

    # Cantidad de stock base
    stocks = [[libro[0], 25] for libro in libros]
    with open(f"{RUTA_CSV}/stocks.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["isbn", "cantidad"])
        writer.writerows(stocks)

def precargar_datos(repo_libro, repo_genero, repo_editorial, repo_stock, repo_cotizacion):
    generar_archivos_csv()

    with open(f"{RUTA_CSV}/generos.csv", "r", encoding="utf-8") as f:
        next(f)
        for fila in csv.reader(f):
            repo_genero.crear(Genero(int(fila[0]), fila[1]))

    with open(f"{RUTA_CSV}/editoriales.csv", "r", encoding="utf-8") as f:
        next(f)
        for fila in csv.reader(f):
            repo_editorial.crear(Editorial(int(fila[0]), fila[1]))

    with open(f"{RUTA_CSV}/libros.csv", "r", encoding="utf-8") as f:
        next(f)
        for fila in csv.reader(f):
            genero = repo_genero.leer_por_id(int(fila[4]))
            editorial = repo_editorial.leer_por_id(int(fila[3]))
            repo_libro.crear(Libro(fila[0], fila[1], fila[2], editorial, genero))

    with open(f"{RUTA_CSV}/stocks.csv", "r", encoding="utf-8") as f:
        next(f)
        for fila in csv.reader(f):
            libro = repo_libro.leer_por_id(fila[0])
            if libro:
                repo_stock.crear(Stock(libro, int(fila[1])))

    with open(f"{RUTA_CSV}/tipos_cotizacion.csv", "r", encoding="utf-8") as f:
        next(f)
        tipos = {int(fila[0]): TipoCotizacion(int(fila[0]), fila[1]) for fila in csv.reader(f)}

    with open(f"{RUTA_CSV}/cotizaciones.csv", "r", encoding="utf-8") as f:
        next(f)
        for fila in csv.reader(f):
            partes_fecha = fila[1].split("-")
            fecha_obj = date(int(partes_fecha[0]), int(partes_fecha[1]), int(partes_fecha[2]))
            tipo = tipos[int(fila[0])]
            repo_cotizacion.crear(CotizacionDolar(tipo, fecha_obj, float(fila[2])))