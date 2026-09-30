from book_manager.repositories.repositories import (
    RepositorioLibro, RepositorioGenero, RepositorioEditorial,
    RepositorioStock, RepositorioCotizacionDolar, RepositorioPrecio
)
from book_manager.services.services import LibroService, CotizacionService, PrecioService
from book_manager.ui.console import ConsoleUI
from book_manager.preload_data.preload_data import precargar_datos

def main(import_default_data: bool = True):
    repo_libro = RepositorioLibro()
    repo_genero = RepositorioGenero()
    repo_editorial = RepositorioEditorial()
    repo_stock = RepositorioStock()
    repo_cotizacion = RepositorioCotizacionDolar()
    repo_precio = RepositorioPrecio()

    if import_default_data:
        precargar_datos(repo_libro, repo_genero, repo_editorial, repo_stock, repo_cotizacion, repo_precio)

    libro_service = LibroService(repo_libro, repo_stock)
    cotizacion_service = CotizacionService(repo_cotizacion)
    precio_service = PrecioService(repo_precio, cotizacion_service)

    app = ConsoleUI(libro_service, cotizacion_service, precio_service)
    app.iniciar()

if __name__ == "__main__":
    main(import_default_data=True)