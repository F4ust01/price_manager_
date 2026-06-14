
import scrapy


class ProductoWebItem(scrapy.Item):
  """Item que modela un producto de la competencia obtenido de la web."""

  producto_id = scrapy.Field()
  nombre_interno = scrapy.Field()
  precio_interno = scrapy.Field()
  nombre_web = scrapy.Field()
  precio_web = scrapy.Field()
  url_img = scrapy.Field()
  formas_pago = scrapy.Field()
  descripcion = scrapy.Field()
  url_extraccion = scrapy.Field()
  diferencia = scrapy.Field()
