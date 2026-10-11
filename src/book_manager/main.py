"""Punto de entrada de Book Manager."""
import os

from book_manager.preload_data.preload_data import precargar_datos
from book_manager.repositories.repositories import (
    RUTA_CSV_DEFECTO, RepositorioCotizacionDolar, RepositorioEditorial,
    RepositorioGenero, RepositorioLibro, RepositorioMoneda, RepositorioPrecio,
    RepositorioStock, RepositorioTipoCotizacion)
from book_manager.services.services import (
    CotizacionService, DolarApiProveedor, EditorialService, GeneroService,
    LibroService, MonedaService, PrecioService, StockService, TipoCotizacionService)
from book_manager.ui.console import Consola


def crear_consola(ruta_csv: str = RUTA_CSV_DEFECTO) -> Consola:
    """Crea repositorios, servicios y consola, y los conecta entre sí."""
    def ruta(nombre: str) -> str:
        return os.path.join(ruta_csv, nombre)

    repo_genero = RepositorioGenero(ruta("generos.csv"))
    repo_editorial = RepositorioEditorial(ruta("editoriales.csv"))
    repo_moneda = RepositorioMoneda(ruta("monedas.csv"))
    repo_tipo = RepositorioTipoCotizacion(ruta("tipos_cotizacion.csv"))
    repo_libro = RepositorioLibro(repo_editorial, repo_genero, ruta("libros.csv"))
    repo_precio = RepositorioPrecio(repo_libro, repo_moneda, ruta("precios.csv"))
    repo_stock = RepositorioStock(repo_libro, ruta("stock.csv"))
    repo_cotizacion = RepositorioCotizacionDolar(repo_tipo, ruta("cotizaciones.csv"))

    servicio_cotizacion = CotizacionService(repo_cotizacion, DolarApiProveedor())
    return Consola(
        generos=GeneroService(repo_genero, repo_libro),
        editoriales=EditorialService(repo_editorial, repo_libro),
        monedas=MonedaService(repo_moneda, repo_precio),
        tipos=TipoCotizacionService(repo_tipo, repo_cotizacion),
        libros=LibroService(repo_libro, repo_precio, repo_stock),
        precios=PrecioService(repo_precio, servicio_cotizacion),
        stock=StockService(repo_stock),
        cotizaciones=servicio_cotizacion)


def main(import_default_data: bool = False) -> None:
    """Ejecuta el sistema.

    Args:
        import_default_data: si es True, genera los CSV de ejemplo antes de iniciar
            (no pisa datos existentes).
    """
    if import_default_data:
        if precargar_datos():
            print("Datos de ejemplo cargados.")
        else:
            print("Ya existen datos; no se modificaron.")
    crear_consola().ejecutar()


if __name__ == "__main__":
    main()
