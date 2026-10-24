"""Pipelines del scraper: validan cada ítem y lo guardan en la base de datos."""
import logging
from typing import Dict, Optional

from itemadapter import ItemAdapter
from scrapy.crawler import Crawler
from scrapy.exceptions import DropItem

from book_manager.database.connection import ConexionDB
from book_manager.entities.entities import Libro, PrecioWeb
from book_manager.models.models import crear_tablas
from book_manager.repositories.repositories import RepositorioLibro, RepositorioPrecioWeb

logger = logging.getLogger(__name__)


class ValidacionPipeline:
    """Descarta los ítems a los que les faltan los datos mínimos para ser comparables."""

    CAMPOS_OBLIGATORIOS = ("libro_id", "titulo_web", "url", "precio", "posicion",
                           "fecha_extraccion")

    def process_item(self, item):
        """Deja pasar el ítem si tiene los datos obligatorios y un precio positivo.

        Raises:
            DropItem: si falta algún dato obligatorio o el precio no es mayor que cero.
        """
        datos = ItemAdapter(item)
        faltantes = [campo for campo in self.CAMPOS_OBLIGATORIOS
                     if datos.get(campo) in (None, "")]
        if faltantes:
            raise DropItem(f"Faltan datos ({', '.join(faltantes)}): {datos.get('url')}")
        if datos["precio"] <= 0:
            raise DropItem(f"Precio no válido ({datos['precio']}): {datos['url']}")
        return item


class PersistenciaPipeline:
    """Guarda cada ítem como un PrecioWeb en la tabla precios_web."""

    def __init__(self, crawler: Optional[Crawler] = None) -> None:
        """Prepara los atributos; la conexión se abre al iniciar el spider."""
        self.crawler = crawler
        self._conexion: Optional[ConexionDB] = None
        self._repositorio: Optional[RepositorioPrecioWeb] = None
        self._libros: Dict[int, Libro] = {}
        self._proximo_id = 1

    @classmethod
    def from_crawler(cls, crawler: Crawler) -> "PersistenciaPipeline":
        """Crea el pipeline con acceso al crawler (para las estadísticas)."""
        return cls(crawler)

    def open_spider(self) -> None:
        """Abre la conexión, crea la tabla si falta, carga el catálogo y calcula el próximo id."""
        self._conexion = ConexionDB()
        crear_tablas(self._conexion.engine)
        self._repositorio = RepositorioPrecioWeb(self._conexion)
        self._libros = {libro.id: libro
                        for libro in RepositorioLibro(self._conexion).leer_todos()}
        self._proximo_id = self._repositorio.siguiente_id()

    def process_item(self, item):
        """Convierte el ítem en entidad PrecioWeb y la guarda en la base.

        Raises:
            DropItem: si el libro buscado ya no existe en el catálogo.
        """
        datos = ItemAdapter(item)
        libro = self._libros.get(datos["libro_id"])
        if libro is None:
            raise DropItem(f"El libro {datos['libro_id']} no está en el catálogo.")
        self._repositorio.crear(PrecioWeb(
            self._proximo_id, libro, datos["titulo_web"], datos.get("isbn_web"),
            datos["url"], datos["precio"], datos.get("url_imagen"),
            datos.get("formas_pago"), datos.get("descripcion"), datos["posicion"],
            bool(datos.get("coincide_isbn")), datos["fecha_extraccion"]))
        self._proximo_id += 1
        return item

    def close_spider(self) -> None:
        """Cierra la conexión con la base de datos."""
        if self._conexion is not None:
            self._conexion.cerrar()
