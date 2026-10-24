"""Ítems del scraper: los datos de una publicación de Cúspide."""
import scrapy


class LibroWebItem(scrapy.Item):
    """Una publicación de Cúspide encontrada al buscar un libro del catálogo."""

    libro_id = scrapy.Field()          # id del libro del catálogo por el que se buscó
    titulo_buscado = scrapy.Field()    # título usado en la búsqueda
    posicion = scrapy.Field()          # lugar en los resultados (1 a 10)
    titulo_web = scrapy.Field()        # título tal como se publica en la web
    isbn_web = scrapy.Field()          # ISBN / código de la publicación (solo dígitos)
    coincide_isbn = scrapy.Field()     # True si isbn_web es el ISBN del libro buscado
    url = scrapy.Field()               # dirección de la ficha
    precio = scrapy.Field()            # precio en pesos (Decimal)
    url_imagen = scrapy.Field()        # dirección de la imagen de la tapa
    formas_pago = scrapy.Field()       # formas de pago, separadas por " | "
    descripcion = scrapy.Field()       # descripción detallada (o ficha técnica)
    fecha_extraccion = scrapy.Field()  # momento de la corrida (igual para todos los ítems)
