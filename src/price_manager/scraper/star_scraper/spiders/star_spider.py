
import json
from collections import defaultdict
import re
import unicodedata

from urllib.parse import quote_plus

import scrapy

from star_scraper.items import ProductoWebItem
from star_scraper.loaders import ProductoWebLoader

# Palabras que identifican medios de pago en el detalle del producto.
PATRON_PAGOS = re.compile(
  r"(efectivo|transferencia|d[eé]bito|"
  r"cr[eé]dito|tarjeta|cuota|"
  r"mercado\s*pago)",
  re.IGNORECASE
)


class StarComputacionSpider(scrapy.Spider):
  """
  Spider que busca en Star Computación los productos de nuestra tienda.

  Por cada producto propio (recibido por archivo JSON) consulta el
  buscador del sitio y procesa como máximo los 10 primeros resultados.
  """

  name = "star_computacion"

  allowed_domains = [
    "starcomputacion.com.ar"
  ]

  URL_BUSQUEDA = (
    "https://www.starcomputacion.com.ar"
    "/prods/search/?search={termino}"
  )

  MAX_RESULTADOS = 10

  def __init__(
    self,
    productos_json: str = "",
    umbral: str = "0",
    *args,
    **kwargs
  ):
    """Carga el catálogo propio y el umbral de alerta de precios."""

    super().__init__(*args, **kwargs)

    self.umbral = float(umbral)

    self.procesados = defaultdict(int)

    with open(
      productos_json,
      encoding="utf-8"
    ) as archivo:

      self.productos_propios = json.load(
        archivo
      )


  def _normalizar(
    self,
    texto: str
  ) -> str:
    """Pasa un texto a minúsculas y le quita los acentos."""

    descompuesto = unicodedata.normalize(
      "NFKD",
      texto
    )

    return "".join(
      c for c in descompuesto
      if not unicodedata.combining(c)
    ).lower()

  def _request_busqueda(
    self,
    producto: dict,
    termino: str
  ):
    """Arma la petición de búsqueda para un término dado."""

    return scrapy.Request(
      url=self.URL_BUSQUEDA.format(
        termino=quote_plus(termino)
      ),
      callback=self.parse_busqueda,
      cb_kwargs={"producto": producto}
    )

  async def start(self):
    """
    Punto de entrada para Scrapy 2.13 o superior, donde el método
    start_requests ya no se invoca automáticamente.
    """

    for peticion in self.start_requests():

      yield peticion

  def start_requests(self):
    """Genera una búsqueda en el sitio por cada producto propio."""

    print(
      f"\n[SCRAPING] Iniciando búsqueda de "
      f"{len(self.productos_propios)} productos..."
    )

    for producto in self.productos_propios:

      print(
        f"[SCRAPING] Buscando: {producto['nombre']}"
      )

      yield self._request_busqueda(
        producto,
        self._normalizar(producto["nombre"])
      )

  def _tarjetas(
    self,
    response
  ) -> list:
    """
    Selecciona las tarjetas de producto de una página de listado.

    En Star Computación cada resultado es un enlace con clase
    "product" hacia la ficha "prod/<slug>-<id>/", que contiene la
    imagen, el título y el precio (formato "ARS 247950"). Si la clase
    no estuviera presente se usa el patrón del enlace como respaldo.
    """

    enlaces = response.xpath(
      "//a[contains(concat(' ', "
      "normalize-space(@class), ' '), "
      "' product ')]"
    )

    if not enlaces:

      # Respaldo: enlaces a fichas de producto (relativos o
      # absolutos), excluyendo los listados "prods/".
      enlaces = response.xpath(
        "//a[contains(@href, 'prod/')]"
        "[not(contains(@href, 'prods/'))]"
      )

    enlaces_vistos = set()

    tarjetas = []

    for enlace in enlaces:

      destino = enlace.xpath(
        "@href"
      ).get(default="").split("?")[0]

      if not destino:

        continue

      destino = response.urljoin(destino)

      if destino in enlaces_vistos:

        continue

      enlaces_vistos.add(destino)

      tarjetas.append(enlace)

    return tarjetas

  def _procesar_tarjetas(
    self,
    response,
    producto: dict,
    tarjetas: list
  ):
    """Construye los items y sigue el detalle de cada tarjeta."""

    clave = producto["id"]

    for tarjeta in tarjetas:

      if self.procesados[clave] >= self.MAX_RESULTADOS:
        return

      self.procesados[clave] += 1

      loader = ProductoWebLoader(
        item=ProductoWebItem(),
        selector=tarjeta
      )

      loader.add_value(
        "producto_id",
        producto["id"]
      )

      loader.add_value(
        "nombre_interno",
        producto["nombre"]
      )

      loader.add_value(
        "precio_interno",
        producto["precio_interno"]
      )

      # El título de la tarjeta es la fuente principal del nombre.
      loader.add_xpath(
        "nombre_web",
        ".//div[contains(@class, 'title')]"
        "//text()"
      )

      loader.add_xpath(
        "nombre_web",
        ".//img/@alt"
      )

      loader.add_value(
        "nombre_web",
        producto["nombre"]
      )

      # El precio se extrae del texto completo de la tarjeta.
      loader.add_xpath(
        "precio_web",
        "string(.)"
      )

      url_imagen = tarjeta.xpath(
        ".//img/@src"
      ).get()

      if url_imagen:

        loader.add_value(
          "url_img",
          response.urljoin(url_imagen)
        )

      item = loader.load_item()

      enlace = tarjeta.xpath(
        "@href"
      ).get()

      if enlace:

        yield response.follow(
          enlace,
          callback=self.parse_detalle,
          cb_kwargs={"item": item}
        )

      else:

        item["url_extraccion"] = (
          response.url
        )

        yield item

  def parse_busqueda(
    self,
    response,
    producto: dict
  ):
    """Procesa la página de resultados del buscador del sitio."""

    tarjetas = self._tarjetas(response)

    if tarjetas:

      print(
        f"[SCRAPING] ✓ {producto['nombre']}: "
        f"{len(tarjetas)} resultado(s)"
      )

      yield from self._procesar_tarjetas(
        response,
        producto,
        tarjetas
      )

    else:

      print(
        f"[SCRAPING] ✗ {producto['nombre']}: "
        f"sin resultados en el sitio"
      )

  def parse_detalle(
    self,
    response,
    item: ProductoWebItem
  ):
    """
    Completa el item con los datos de la página de detalle.

    Obtiene la descripción detallada, las formas de pago con su precio
    y una imagen de mejor calidad si está disponible.
    """

    loader = ProductoWebLoader(
      item=item,
      response=response
    )

    # Descripción detallada: bloque descriptivo de la ficha real,
    # con metadatos y clases descriptivas como respaldo.
    descripcion = " ".join(
      response.xpath(
        "string(//div["
        "@id='contenido_desc'])"
      ).get(default="").split()
    )

    if not descripcion:

      descripcion = response.xpath(
        "//meta[@property="
        "'og:description']/@content"
      ).get(default="")

    if not descripcion:

      fragmentos = response.xpath(
        "//*[contains(@class, 'desc')]"
        "//text()"
      ).getall()

      descripcion = " ".join(
        " ".join(f.split())
        for f in fragmentos
        if f.strip()
      )

    loader.add_value(
      "descripcion",
      (descripcion or "Sin descripción")[
        :2000
      ]
    )

    # Formas de pago y precio: tabla de precios de la ficha
    # (CONTADO, DEBITO, CUOTAS) emparejando etiqueta y monto.
    formas = self._formas_pago_tabla(
      response
    )

    if not formas:

      lineas_pago: list = []

      for texto in response.xpath(
        "//body//text()"
      ).getall():

        linea = " ".join(texto.split())

        if linea and PATRON_PAGOS.search(
          linea
        ):

          lineas_pago.append(linea)

      formas = " | ".join(
        dict.fromkeys(lineas_pago)
      )

    loader.add_value(
      "formas_pago",
      (formas or "No informado")[:1000]
    )

    # Imagen principal: galería de la ficha o metadato del sitio.
    imagen = response.xpath(
      "//div[@id='gallery']//img/@src"
    ).get() or response.xpath(
      "//meta[@property='og:image']"
      "/@content"
    ).get()

    if imagen:

      loader.add_value(
        "url_img",
        response.urljoin(imagen)
      )

    # Si el listado no informó el precio, se toma el CONTADO de
    # la tabla de precios de la ficha.
    if not item.get("precio_web"):

      loader.add_xpath(
        "precio_web",
        "string(//table["
        "@id='prices_table']"
        "//td[contains(@class,"
        " 'price_td')][1])"
      )

      loader.add_xpath(
        "precio_web",
        "string(//body)"
      )

    loader.add_value(
      "url_extraccion",
      response.url
    )

    item_final = loader.load_item()

    print(
      f"[SCRAPING]   → Detalle: "
      f"{item_final.get('nombre_web', item_final.get('nombre_interno', '?'))[:60]} "
      f"| ${ item_final.get('precio_web', '?')}"
    )

    yield item_final

  def _formas_pago_tabla(
    self,
    response
  ) -> str:
    """
    Extrae las formas de pago con su precio desde la tabla de la
    ficha del producto (filas CONTADO, DEBITO, CUOTAS).
    """

    celdas = response.xpath(
      "//table[@id='prices_table']//td"
    )

    pares: list = []

    etiqueta = ""

    for celda in celdas:

      clase = celda.xpath(
        "@class"
      ).get(default="")

      texto = " ".join(
        celda.xpath(
          "string(.)"
        ).get(default="").split()
      )

      if "price_td" in clase:

        if etiqueta and texto:

          pares.append(
            f"{etiqueta}: {texto}"
          )

        etiqueta = ""

      elif texto:

        etiqueta = texto

    return " | ".join(pares)
