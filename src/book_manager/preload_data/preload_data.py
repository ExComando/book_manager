import csv
import os
from datetime import date
from book_manager.entities.entities import (
    Genero, Editorial, Moneda, TipoCotizacion, Libro, CotizacionDolar, Precio, Stock
)
from book_manager.repositories.repositories import (
    RepositorioLibro, RepositorioGenero, RepositorioEditorial, RepositorioStock, RepositorioCotizacionDolar, RepositorioPrecio
)

RUTA_CSV = "src/book_manager/migrations/csv"

def generar_archivos_csv():
    os.makedirs(RUTA_CSV, exist_ok=True)
    
    # Géneros y Editoriales
    generos = [[1, "Romance"], [2, "Deep Learning"], [3, "Inteligencia Artificial"], [4, "Novela Histórica"], [5, "Ciencia Ficción"], [6, "Terror"], [7, "Fantasía"], [8, "Desarrollo Personal"], [9, "Thriller"], [10, "Ensayo"]]
    with open(f"{RUTA_CSV}/generos.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id_genero", "nombre"])
        writer.writerows(generos)

    editoriales = [[1, "MIT Press"], [2, "O'Reilly Media"], [3, "Springer"], [4, "Planeta"], [5, "Alfaguara"], [6, "Tusquets"], [7, "Manning Publications"], [8, "Packt"], [9, "Anagrama"], [10, "Sexto Piso"]]
    with open(f"{RUTA_CSV}/editoriales.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id_editorial", "nombre"])
        writer.writerows(editoriales)

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

    monedas = [[1, "ARS", "$"], [2, "USD", "u$s"], [3, "EUR", "€"]]
    with open(f"{RUTA_CSV}/monedas.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id_moneda", "codigo", "simbolo"])
        writer.writerows(monedas)

    tipos_cotizacion = [[1, "Oficial"], [2, "Blue"], [3, "MEP"]]
    with open(f"{RUTA_CSV}/tipos_cotizacion.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id_tipo", "nombre"])
        writer.writerows(tipos_cotizacion)

    # Cotizaciones reales indicadas por el usuario
    cotizaciones = [
        [1, "2026-09-29", 1545.00], 
        [2, "2026-09-29", 1560.00], 
        [3, "2026-09-29", 1250.00]
    ]
    with open(f"{RUTA_CSV}/cotizaciones.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id_tipo", "fecha", "valor_venta"])
        writer.writerows(cotizaciones)

    stocks = [[libro[0], 25] for libro in libros]
    with open(f"{RUTA_CSV}/stocks.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["isbn", "cantidad"])
        writer.writerows(stocks)

    # Nuevos precios base en dólares (USD = Moneda ID 2)
    precios = [[libro[0], 2, 35.50] for libro in libros] # Todos cuestan 35.50 USD de base
    with open(f"{RUTA_CSV}/precios.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["isbn", "id_moneda", "monto"])
        writer.writerows(precios)

def precargar_datos(repo_libro, repo_genero, repo_editorial, repo_stock, repo_cotizacion, repo_precio):
    generar_archivos_csv()

    # Cargar entidades base
    with open(f"{RUTA_CSV}/generos.csv", "r", encoding="utf-8") as f:
        next(f); [repo_genero.crear(Genero(int(fila[0]), fila[1])) for fila in csv.reader(f)]
    with open(f"{RUTA_CSV}/editoriales.csv", "r", encoding="utf-8") as f:
        next(f); [repo_editorial.crear(Editorial(int(fila[0]), fila[1])) for fila in csv.reader(f)]
    
    # Cargar libros
    with open(f"{RUTA_CSV}/libros.csv", "r", encoding="utf-8") as f:
        next(f)
        for fila in csv.reader(f):
            repo_libro.crear(Libro(fila[0], fila[1], fila[2], repo_editorial.leer_por_id(int(fila[3])), repo_genero.leer_por_id(int(fila[4]))))

    # Cargar stocks
    with open(f"{RUTA_CSV}/stocks.csv", "r", encoding="utf-8") as f:
        next(f)
        for fila in csv.reader(f):
            libro = repo_libro.leer_por_id(fila[0])
            if libro: repo_stock.crear(Stock(libro, int(fila[1])))

    # Cargar cotizaciones
    tipos = {}
    with open(f"{RUTA_CSV}/tipos_cotizacion.csv", "r", encoding="utf-8") as f:
        next(f)
        tipos = {int(fila[0]): TipoCotizacion(int(fila[0]), fila[1]) for fila in csv.reader(f)}
    with open(f"{RUTA_CSV}/cotizaciones.csv", "r", encoding="utf-8") as f:
        next(f)
        for fila in csv.reader(f):
            partes = fila[1].split("-")
            repo_cotizacion.crear(CotizacionDolar(tipos[int(fila[0])], date(int(partes[0]), int(partes[1]), int(partes[2])), float(fila[2])))

    # Cargar Precios
    moneda_usd = Moneda(2, "USD", "u$s")
    with open(f"{RUTA_CSV}/precios.csv", "r", encoding="utf-8") as f:
        next(f)
        for fila in csv.reader(f):
            libro = repo_libro.leer_por_id(fila[0])
            if libro:
                repo_precio.crear(Precio(libro, moneda_usd, float(fila[2])))