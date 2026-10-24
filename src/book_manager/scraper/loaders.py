"""Loaders del scraper: limpian y normalizan los datos antes de armar el ítem."""
import re
from decimal import Decimal, InvalidOperation
from typing import Any, Optional

from itemloaders.processors import Join, MapCompose, TakeFirst
from scrapy.loader import ItemLoader


def limpiar_texto(valor: Any) -> Any:
    """Quita espacios y saltos de línea repetidos de un texto.

    Los valores que no son texto (números, fechas, booleanos) se devuelven sin cambios.
    Si el texto queda vacío devuelve None, y el loader lo descarta.
    """
    if not isinstance(valor, str):
        return valor
    texto = re.sub(r"\s+", " ", valor).strip()
    return texto or None


def limpiar_forma_pago(valor: str) -> Optional[str]:
    """Limpia un ítem de la lista de formas de pago (quita el '>' inicial del sitio)."""
    texto = limpiar_texto(valor)
    if texto is None:
        return None
    return texto.lstrip("> ").strip() or None


def a_precio(valor: Any) -> Optional[Decimal]:
    """Convierte un precio en Decimal con dos decimales.

    Acepta el formato del sitio ('$ 26.999,00': punto de miles y coma decimal) y el del
    JSON de la página ('30000.00'). Devuelve None si el valor no es un número.
    """
    if valor is None:
        return None
    texto = re.sub(r"[^\d.,]", "", str(valor))
    if not texto:
        return None
    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")
    try:
        return Decimal(texto).quantize(Decimal("0.01"))
    except InvalidOperation:
        return None


def solo_digitos(valor: Any) -> Optional[str]:
    """Deja solo los dígitos de un código (por ejemplo un ISBN con guiones)."""
    digitos = re.sub(r"\D", "", str(valor)) if valor is not None else ""
    return digitos or None


class LibroWebLoader(ItemLoader):
    """Loader del ítem LibroWebItem: toma el primer valor de cada campo, ya normalizado."""

    default_input_processor = MapCompose(limpiar_texto)
    default_output_processor = TakeFirst()

    isbn_web_in = MapCompose(solo_digitos)
    precio_in = MapCompose(a_precio)
    url_imagen_in = MapCompose(limpiar_texto)
    formas_pago_in = MapCompose(limpiar_forma_pago)
    formas_pago_out = Join(" | ")
    descripcion_out = Join("\n")
