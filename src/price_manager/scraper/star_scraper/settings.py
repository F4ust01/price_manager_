
# Configuración del proyecto Scrapy para Star Computación.

BOT_NAME = "star_scraper"

SPIDER_MODULES = [
  "star_scraper.spiders"
]

NEWSPIDER_MODULE = (
  "star_scraper.spiders"
)

# Scraping responsable: se respeta robots.txt, que permite el acceso
# (Allow: /) pero solicita una frecuencia de 1 pedido cada 10 segundos
# (Crawl-delay: 10 / Request-rate: 1/10s).
ROBOTSTXT_OBEY = True

DOWNLOAD_DELAY = 10

CONCURRENT_REQUESTS = 1

CONCURRENT_REQUESTS_PER_DOMAIN = 1

# Algunos servidores rechazan el agente por defecto de Scrapy, por lo
# que se utiliza uno equivalente al de un navegador de escritorio.
USER_AGENT = (
  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
  "AppleWebKit/537.36 (KHTML, like Gecko) "
  "Chrome/124.0.0.0 Safari/537.36"
)

# Cabeceras completas de navegador: algunos firewalls rechazan los
# pedidos que solo informan el agente de usuario.
DEFAULT_REQUEST_HEADERS = {
  "Accept": (
    "text/html,application/xhtml+xml,"
    "application/xml;q=0.9,image/avif,"
    "image/webp,*/*;q=0.8"
  ),
  "Accept-Language": (
    "es-AR,es;q=0.9,en;q=0.8"
  ),
  "Accept-Encoding": (
    "gzip, deflate"
  ),
  "Upgrade-Insecure-Requests": "1",
  "Sec-Fetch-Dest": "document",
  "Sec-Fetch-Mode": "navigate",
  "Sec-Fetch-Site": "none",
  "Sec-Fetch-User": "?1"
}

RETRY_ENABLED = True

RETRY_TIMES = 2

# Pipelines del flujo: limpieza, comparación/alertas y persistencia.
ITEM_PIPELINES = {
  "star_scraper.pipelines."
  "LimpiezaValidacionPipeline": 300,
  "star_scraper.pipelines."
  "ComparacionAlertasPipeline": 400,
  "star_scraper.pipelines."
  "GuardarBaseDatosPipeline": 500
}

LOG_LEVEL = "INFO"

FEED_EXPORT_ENCODING = "utf-8"

REQUEST_FINGERPRINTER_IMPLEMENTATION = (
  "2.7"
)

TWISTED_REACTOR = (
  "twisted.internet.asyncioreactor."
  "AsyncioSelectorReactor"
)
