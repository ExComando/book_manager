from book_manager.repositories.repositories import (
    RepositorioLibro, RepositorioGenero, RepositorioEditorial,
    RepositorioStock, RepositorioCotizacionDolar
)
from book_manager.services.services import LibroService, CotizacionService, PrecioService
from book_manager.ui.console import ConsoleUI
from book_manager.preload_data.preload_data import precargar_datos

def main(import_default_data: bool = True):
    # 1. Instanciar repositorios (Capa de Datos)
    repo_libro = RepositorioLibro()
    repo_genero = RepositorioGenero()
    repo_editorial = RepositorioEditorial()
    repo_stock = RepositorioStock()
    repo_cotizacion = RepositorioCotizacionDolar()

    # 2. Precargar datos si el parámetro lo indica
    if import_default_data:
        precargar_datos(repo_libro, repo_genero, repo_editorial, repo_stock, repo_cotizacion)

    # 3. Instanciar servicios e inyectar repositorios (Capa Lógica)
    libro_service = LibroService(repo_libro, repo_stock)
    cotizacion_service = CotizacionService(repo_cotizacion)
    precio_service = PrecioService(cotizacion_service)

    # 4. Instanciar interfaz e inyectar servicios (Capa de Presentación)
    app = ConsoleUI(libro_service, cotizacion_service, precio_service)
    app.iniciar()

if __name__ == "__main__":
    # Al ejecutar el script directamente, precargamos los datos por defecto
    main(import_default_data=True)