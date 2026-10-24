"""Configuración del scraper de Cúspide."""

BOT_NAME = "book_manager_scraper"
SPIDER_MODULES = ["book_manager.scraper.spiders"]
NEWSPIDER_MODULE = "book_manager.scraper.spiders"

# Se respeta el robots.txt del sitio.
ROBOTSTXT_OBEY = True
USER_AGENT = "book_manager-tp-ugr (trabajo práctico universitario)"

# Pocas solicitudes por vez y con pausa: son unas 140 en total y no queremos saturar el sitio.
DOWNLOAD_DELAY = 0.5
CONCURRENT_REQUESTS_PER_DOMAIN = 2
AUTOTHROTTLE_ENABLED = True
RETRY_TIMES = 2
DOWNLOAD_TIMEOUT = 30

ITEM_PIPELINES = {
    "book_manager.scraper.pipelines.ValidacionPipeline": 100,
    "book_manager.scraper.pipelines.PersistenciaPipeline": 300,
}

# Solo se muestran advertencias y errores; el resumen lo imprime el runner.
LOG_LEVEL = "WARNING"
TELNETCONSOLE_ENABLED = False
FEED_EXPORT_ENCODING = "utf-8"
