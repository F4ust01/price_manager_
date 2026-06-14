
import re

from itemloaders.processors import (
  Join,
  MapCompose,
  TakeFirst
)

from scrapy.loader import ItemLoader

# Patrón de precios del sitio y en formato argentino. Acepta tanto
# "ARS 247950" (formato usado por Star Computación) como
# "$ 1.234.567,89" (formato tradicional con separadores).
PATRON_PRECIO = re.compile(
  r"(?:ARS|\$)\s*([\d\.]+(?:,\d+)?)",
  re.IGNORECASE
)


def limpiar_texto(
  valor: str
) -> str:
  """Normaliza espacios y saltos de línea de un texto extraído."""

  if valor is None:

    return ""

  return " ".join(
    str(valor).split()
  ).strip()


def extraer_precio(
  texto: str
):
  """
  Extrae el primer precio en pesos presente en un texto.

  Convierte el formato argentino (puntos de miles y coma decimal)
  a un número flotante. Retorna None si no hay precio.
  """

  if not texto:

    return None

  coincidencia = PATRON_PRECIO.search(
    str(texto)
  )

  if not coincidencia:

    return None

  crudo = coincidencia.group(1)

  normalizado = crudo.replace(
    ".",
    ""
  ).replace(
    ",",
    "."
  )

  try:

    return float(normalizado)

  except ValueError:

    return None


def filtrar_vacios(
  valor: str
):
  """Descarta cadenas vacías para que TakeFirst tome el primer dato útil."""

  return valor if valor else None


class ProductoWebLoader(ItemLoader):
  """Loader con los procesadores de entrada y salida del item web."""

  default_input_processor = MapCompose(
    limpiar_texto,
    filtrar_vacios
  )

  default_output_processor = TakeFirst()

  # El precio se parsea desde el texto crudo de la tarjeta del producto.
  precio_web_in = MapCompose(
    extraer_precio
  )

  precio_interno_in = MapCompose(
    float
  )

  # Las formas de pago detectadas se conservan todas, unidas con " | ".
  formas_pago_out = Join(
    " | "
  )

  producto_id_in = MapCompose(
    int
  )
