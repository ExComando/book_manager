"""Ejecución del scraper: dentro de un proceso (main) o en un proceso aparte (lanzar)."""
import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

from book_manager.scraper import URL_BASE

# Carpeta src, para que el proceso hijo encuentre el paquete book_manager.
CARPETA_SRC = Path(__file__).resolve().parents[2]


def ejecutar_scraper(base_url: str = URL_BASE, fecha_extraccion: Optional[str] = None) -> int:
    """Corre el spider y guarda los resultados en la base de datos.

    Scrapy no puede reiniciarse dentro de un mismo proceso, por eso esta función se
    ejecuta una sola vez por proceso (ver lanzar_scraper).

    Returns:
        La cantidad de precios guardados.
    """
    from scrapy.crawler import CrawlerProcess
    from scrapy.settings import Settings

    from book_manager.scraper.spiders.cuspide import CuspideSpider

    configuracion = Settings()
    configuracion.setmodule("book_manager.scraper.settings")
    proceso = CrawlerProcess(configuracion)
    crawler = proceso.create_crawler(CuspideSpider)
    proceso.crawl(crawler, base_url=base_url, fecha_extraccion=fecha_extraccion)
    proceso.start()

    estadisticas = crawler.stats.get_stats()
    guardados = estadisticas.get("item_scraped_count", 0)
    print(f"Scraping finalizado: {guardados} precios guardados, "
          f"{estadisticas.get('item_dropped_count', 0)} descartados, "
          f"{estadisticas.get('downloader/request_count', 0)} solicitudes.")
    bloqueadas = estadisticas.get("robotstxt/forbidden", 0)
    if bloqueadas:
        print(f"Atención: el robots.txt del sitio bloqueó {bloqueadas} solicitudes.")
    return guardados


def lanzar_scraper(base_url: str = URL_BASE, fecha_extraccion: Optional[str] = None) -> int:
    """Corre el scraper en un proceso aparte y muestra su salida.

    Un proceso aparte permite ejecutar el scraping varias veces desde el menú y que su
    salida se vea también en un notebook.

    Returns:
        El código de salida del proceso (0 si terminó bien).
    """
    comando = [sys.executable, "-m", "book_manager.scraper.runner", "--base-url", base_url]
    if fecha_extraccion:
        comando += ["--fecha", fecha_extraccion]
    entorno = dict(os.environ)
    entorno["PYTHONPATH"] = os.pathsep.join(
        ruta for ruta in (str(CARPETA_SRC), entorno.get("PYTHONPATH")) if ruta)
    entorno["PYTHONIOENCODING"] = "utf-8"
    entorno["PYTHONUNBUFFERED"] = "1"
    with subprocess.Popen(comando, env=entorno, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, text=True, encoding="utf-8") as proceso:
        for linea in proceso.stdout:
            print(linea, end="")
    return proceso.returncode


def main() -> None:
    """Punto de entrada: python -m book_manager.scraper.runner"""
    analizador = argparse.ArgumentParser(description="Scraping de precios en Cúspide.")
    analizador.add_argument("--base-url", default=URL_BASE, help="dirección del sitio")
    analizador.add_argument("--fecha", default=None, help="fecha y hora ISO de la corrida")
    argumentos = analizador.parse_args()
    ejecutar_scraper(argumentos.base_url, argumentos.fecha)


if __name__ == "__main__":
    main()
