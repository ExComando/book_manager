from typing import List, Optional
from book_manager.entities.entities import Libro, Stock, CotizacionDolar, Precio
from book_manager.repositories.repositories import (
    RepositorioLibro, RepositorioStock, RepositorioCotizacionDolar
)
from book_manager.repositories.repositories import RepositorioPrecio

class LibroService:
    def __init__(self, repo_libro: RepositorioLibro, repo_stock: RepositorioStock):
        self.repo_libro = repo_libro
        self.repo_stock = repo_stock

    def registrar_libro(self, libro: Libro, cantidad_inicial: int) -> Libro:
        """Registra un libro nuevo y le asigna un stock inicial."""
        libro_creado = self.repo_libro.crear(libro)
        stock = Stock(libro=libro_creado, cantidad=cantidad_inicial)
        self.repo_stock.crear(stock)
        return libro_creado

    def obtener_libro(self, isbn: str) -> Optional[Libro]:
        return self.repo_libro.leer_por_id(isbn)

    def actualizar_stock(self, isbn: str, nueva_cantidad: int) -> Stock:
        stock_actual = self.repo_stock.leer_por_libro(isbn)
        if not stock_actual:
            raise ValueError("No se encontró stock para el libro indicado.")
        stock_actual.cantidad = nueva_cantidad
        return self.repo_stock.actualizar(stock_actual)

    def listar_libros_con_stock(self) -> List[tuple[Libro, int]]:
        libros = self.repo_libro.leer_todos()
        resultado = []
        for libro in libros:
            stock = self.repo_stock.leer_por_libro(libro.isbn)
            cantidad = stock.cantidad if stock else 0
            resultado.append((libro, cantidad))
        return resultado


class CotizacionService:
    def __init__(self, repo_cotizacion: RepositorioCotizacionDolar):
        self.repo_cotizacion = repo_cotizacion

    def registrar_cotizacion(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        return self.repo_cotizacion.crear(cotizacion)

    def obtener_cotizacion_actual(self, tipo_id: int) -> Optional[CotizacionDolar]:
        """Busca el histórico de un tipo de dólar y devuelve el más reciente."""
        historico = self.repo_cotizacion.leer_historico_por_tipo(tipo_id)
        if not historico:
            return None
        # Ordena las cotizaciones de la más nueva a la más antigua
        historico.sort(key=lambda c: c.fecha, reverse=True)
        return historico[0]


class PrecioService:
    def __init__(self, repo_precio: RepositorioPrecio, cotizacion_service: CotizacionService):
        self.repo_precio = repo_precio
        self.cotizacion_service = cotizacion_service

    def obtener_precio_base(self, isbn: str) -> Optional[Precio]:
        """Devuelve el objeto Precio base (en USD) de un libro."""
        return self.repo_precio.leer_por_libro(isbn)

    def calcular_precio_ars(self, precio_usd: Precio, tipo_cotizacion_id: int) -> float:
        if precio_usd.moneda.codigo != "USD":
            raise ValueError("El precio base debe estar en USD para calcular la conversión.")
        
        cotizacion_actual = self.cotizacion_service.obtener_cotizacion_actual(tipo_cotizacion_id)
        if not cotizacion_actual:
            raise ValueError("No hay cotizaciones registradas para el tipo especificado.")
        
        return precio_usd.monto * cotizacion_actual.valor_venta