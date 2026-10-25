"""Punto de entrada de Book Manager."""
from sqlalchemy import text

from book_manager.database.connection import ConexionDB
from book_manager.migrations.migrations import (
    CARPETA_SQL_DEFECTO, TABLAS, cargar_datos_desde_sql)
from book_manager.models.models import crear_tablas
from book_manager.repositories.repositories import (
    RepositorioCotizacionDolar, RepositorioEditorial, RepositorioGenero, RepositorioLibro,
    RepositorioMoneda, RepositorioPrecio, RepositorioPrecioWeb, RepositorioStock,
    RepositorioTipoCotizacion)
from book_manager.scraper.runner import lanzar_scraper
from book_manager.services.services import (
    DolarApiProveedor, ServicioCotizacionDolar, ServicioEditorial, ServicioGenero,
    ServicioLibro, ServicioMoneda, ServicioPrecio, ServicioScraping, ServicioStock,
    ServicioTipoCotizacion)
from book_manager.ui.console import Consola


def crear_consola(conexion: ConexionDB) -> Consola:
    """Crea repositorios, servicios y consola, y los conecta entre sí."""
    repo_genero = RepositorioGenero(conexion)
    repo_editorial = RepositorioEditorial(conexion)
    repo_moneda = RepositorioMoneda(conexion)
    repo_tipo = RepositorioTipoCotizacion(conexion)
    repo_libro = RepositorioLibro(conexion)
    repo_precio = RepositorioPrecio(conexion)
    repo_stock = RepositorioStock(conexion)
    repo_cotizacion = RepositorioCotizacionDolar(conexion)
    repo_precio_web = RepositorioPrecioWeb(conexion)

    servicio_cotizacion = ServicioCotizacionDolar(
        repo_cotizacion, repo_tipo, DolarApiProveedor())
    servicio_precio = ServicioPrecio(repo_precio, servicio_cotizacion)
    servicio_scraping = ServicioScraping(
        repo_libro, repo_precio_web, servicio_precio, lanzar_scraper)
    return Consola(
        generos=ServicioGenero(repo_genero, repo_libro),
        editoriales=ServicioEditorial(repo_editorial, repo_libro),
        monedas=ServicioMoneda(repo_moneda, repo_precio),
        tipos=ServicioTipoCotizacion(repo_tipo, repo_cotizacion),
        libros=ServicioLibro(repo_libro, repo_precio, repo_stock),
        precios=servicio_precio,
        stock=ServicioStock(repo_stock),
        cotizaciones=servicio_cotizacion,
        scraping=servicio_scraping)


def _base_sin_datos(conexion: ConexionDB) -> bool:
    """Indica si todas las tablas del sistema están vacías."""
    with conexion.transaccion() as sesion:
        return all(sesion.execute(text(f"SELECT COUNT(*) FROM {tabla}")).scalar() == 0
                   for tabla, _ in TABLAS)


def main(import_default_data: bool = False) -> None:
    """Ejecuta el sistema.

    Args:
        import_default_data: si es True, carga los datos de ejemplo (ejecuta los .sql de
            migrations/sql) antes de iniciar. Sin importar su valor, si la base está
            completamente vacía también se cargan, para que el sistema no arranque sin
            datos. Cargarlos es repetible: no duplica registros.
    """
    conexion = ConexionDB()
    try:
        crear_tablas(conexion.engine)
        if import_default_data or _base_sin_datos(conexion):
            cargar_datos_desde_sql(CARPETA_SQL_DEFECTO, conexion)
        crear_consola(conexion).ejecutar()
    finally:
        conexion.cerrar()


if __name__ == "__main__":
    main()
