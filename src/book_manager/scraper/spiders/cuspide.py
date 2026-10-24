"""Spider de Cúspide: busca por título cada libro del catálogo y lee sus publicaciones."""
import datetime
import json
from typing import Any, AsyncIterator, Dict, List, Optional
from urllib.parse import urlencode, urlparse

import scrapy
from scrapy.http import Response

from book_manager.scraper.items import LibroWebItem
from book_manager.scraper.loaders import LibroWebLoader, solo_digitos

URL_BASE = "https://cuspide.com"

# Una tarjeta por resultado en la página de búsqueda.
SELECTOR_TARJETAS = "div.products div.product-small.type-product"
# Fragmentos de XPath de la ficha: la sección "Descripción" de la página del libro.
XPATH_SECCION_DESCRIPCION = (
    '//div[contains(@class, "product-section")][.//h5[contains(., "Descripci")]]'
    '//div[contains(@class, "entry-content")]')


class CuspideSpider(scrapy.Spider):
    """Busca en Cúspide cada libro del catálogo y toma los primeros resultados.

    Por cada libro hace una búsqueda por título, sigue los primeros MAX_RESULTADOS
    resultados y en cada ficha lee precio, imagen, formas de pago y descripción.

    Args:
        libros: lista de diccionarios {"id", "isbn", "titulo"}. Si no se indica, se
            lee el catálogo de la base de datos.
        base_url: dirección del sitio (se cambia solo en las pruebas).
        fecha_extraccion: fecha y hora de la corrida en formato ISO. Si no se indica,
            se usa el momento actual.
    """

    name = "cuspide"
    MAX_RESULTADOS = 10

    def __init__(self, libros: Optional[List[Dict[str, Any]]] = None,
                 base_url: str = URL_BASE, fecha_extraccion: Optional[str] = None,
                 **kwargs: Any) -> None:
        """Guarda los parámetros de la corrida."""
        super().__init__(**kwargs)
        self.base_url = base_url.rstrip("/")
        self.allowed_domains = [urlparse(self.base_url).hostname]
        self.libros = libros
        if fecha_extraccion:
            self.fecha_extraccion = datetime.datetime.fromisoformat(fecha_extraccion)
        else:
            self.fecha_extraccion = datetime.datetime.now().replace(microsecond=0)

    def _catalogo(self) -> List[Dict[str, Any]]:
        """Devuelve los libros a buscar: los recibidos o, si no hay, los de la base."""
        if self.libros is not None:
            return self.libros
        from book_manager.database.connection import ConexionDB
        from book_manager.repositories.repositories import RepositorioLibro
        conexion = ConexionDB()
        try:
            return [{"id": libro.id, "isbn": libro.isbn, "titulo": libro.titulo}
                    for libro in RepositorioLibro(conexion).leer_todos()]
        finally:
            conexion.cerrar()

    def url_busqueda(self, titulo: str) -> str:
        """Arma la dirección de la búsqueda de productos por título."""
        return f"{self.base_url}/?" + urlencode({"s": titulo.strip(), "post_type": "product"})

    async def start(self) -> AsyncIterator[scrapy.Request]:
        """Genera una búsqueda por cada libro del catálogo (solo los libros propios)."""
        for libro in self._catalogo():
            yield scrapy.Request(self.url_busqueda(libro["titulo"]),
                                 callback=self.parse_resultados,
                                 cb_kwargs={"libro": libro})

    def parse_resultados(self, response: Response, libro: Dict[str, Any]):
        """Sigue las fichas de los primeros resultados de la búsqueda de un libro."""
        tarjetas = response.css(SELECTOR_TARJETAS)[:self.MAX_RESULTADOS]
        if not tarjetas:
            self.logger.warning("Sin resultados para '%s'.", libro["titulo"])
        for posicion, tarjeta in enumerate(tarjetas, start=1):
            enlace = tarjeta.css("p.name a::attr(href)").get()
            if enlace:
                # dont_filter: la misma ficha puede salir en la búsqueda de dos libros del
                # catálogo y a cada uno le corresponde su propio registro.
                yield response.follow(enlace, callback=self.parse_ficha, dont_filter=True,
                                      cb_kwargs={"libro": libro, "posicion": posicion})

    @staticmethod
    def _producto_json_ld(response: Response) -> Dict[str, Any]:
        """Devuelve el bloque Product del JSON-LD de la ficha ({} si no hay)."""
        for texto in response.xpath('//script[@type="application/ld+json"]/text()').getall():
            try:
                datos = json.loads(texto)
            except json.JSONDecodeError:
                continue
            nodos = datos.get("@graph", [datos]) if isinstance(datos, dict) else datos
            for nodo in nodos:
                if isinstance(nodo, dict) and nodo.get("@type") == "Product":
                    return nodo
        return {}

    @staticmethod
    def _especificaciones(response: Response) -> List[str]:
        """Lee la tabla de especificaciones de la ficha como líneas 'Etiqueta: valor'."""
        lineas = []
        for fila in response.css("table.shop_attributes tr"):
            etiqueta = " ".join(fila.css("th ::text").getall()).strip()
            valor = " ".join(fila.css("td ::text").getall()).strip()
            if etiqueta and valor:
                lineas.append(f"{etiqueta}: {valor}")
        return lineas

    def parse_ficha(self, response: Response, libro: Dict[str, Any], posicion: int):
        """Lee los datos de la ficha de una publicación y genera el ítem."""
        producto = self._producto_json_ld(response)
        ofertas = producto.get("offers") or []
        oferta = (ofertas[0] if isinstance(ofertas, list) and ofertas else
                  ofertas if isinstance(ofertas, dict) else {})
        isbn_web = solo_digitos(producto.get("sku"))
        isbn_libro = solo_digitos(libro.get("isbn"))

        loader = LibroWebLoader(item=LibroWebItem(), response=response)
        loader.add_value("libro_id", libro["id"])
        loader.add_value("titulo_buscado", libro["titulo"])
        loader.add_value("posicion", posicion)
        loader.add_css("titulo_web", "h1.product_title::text")
        loader.add_value("isbn_web", isbn_web)
        loader.add_value("coincide_isbn", bool(isbn_web) and isbn_web == isbn_libro)
        loader.add_value("url", response.url)
        if oferta.get("price") is not None:
            loader.add_value("precio", oferta["price"])
        else:
            loader.add_css("precio", "p.product-page-price bdi::text")
        loader.add_css("url_imagen",
                       ".woocommerce-product-gallery img.wp-post-image::attr(data-large_image)")
        loader.add_css("url_imagen",
                       ".woocommerce-product-gallery img.wp-post-image::attr(src)")
        loader.add_css("formas_pago", "#contentPaymentsPopUpArg ul li::text")
        loader.add_xpath(
            "descripcion",
            f"{XPATH_SECCION_DESCRIPCION}//text()"
            '[not(ancestor::*[contains(@class, "livriz-hidden")])]')
        if not loader.get_collected_values("descripcion"):
            # Sin sinopsis en la ficha: se guarda la ficha técnica (peso, idioma, páginas...).
            loader.add_value("descripcion", self._especificaciones(response))
        loader.add_value("fecha_extraccion", self.fecha_extraccion)
        yield loader.load_item()
