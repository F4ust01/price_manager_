
import datetime

from scrapy.exceptions import DropItem

from price_manager.database.connection import (
  ConexionDB
)

from price_manager.models.models import (
  Base,
  ResultadoScrapingModel
)


class LimpiezaValidacionPipeline:
  """Valida y normaliza los items antes de continuar el flujo."""

  def process_item(self, item, spider):
    """Descarta items sin precio web válido o sin producto asociado."""

    if not item.get("producto_id"):

      raise DropItem(
        "Item sin producto propio asociado"
      )

    precio = item.get("precio_web")

    if not precio or precio <= 0:

      raise DropItem(
        "Item sin precio web válido"
      )

    item.setdefault(
      "url_img",
      ""
    )

    item.setdefault(
      "formas_pago",
      "No informado"
    )

    item.setdefault(
      "descripcion",
      "Sin descripción"
    )

    return item


class GuardarBaseDatosPipeline:
  """Persiste los resultados del scraping en la base de datos."""

  def open_spider(self, spider):
    """Abre la sesión de base de datos al iniciar el spider."""

    self.db = ConexionDB()

    # Por robustez: garantiza que las tablas existan también cuando el
    # spider corre en un subproceso recién iniciado.
    Base.metadata.create_all(
      bind=self.db.get_engine()
    )

    self.session = self.db.get_session()

  def process_item(self, item, spider):
    """Registra el resultado obtenido para su posterior reporte."""

    spider.logger.info(
      "Guardando en BD: %s | $%s",
      item.get("nombre_web", item.get("nombre_interno", "?")),
      item.get("precio_web", "?")
    )

    resultado = ResultadoScrapingModel(
      producto_id=item["producto_id"],
      nombre_web=item.get(
        "nombre_web",
        item["nombre_interno"]
      ),
      precio_interno=item[
        "precio_interno"
      ],
      precio_web=item["precio_web"],
      diferencia=item.get(
        "diferencia",
        0.0
      ),
      url_img=item.get("url_img"),
      formas_pago=item.get(
        "formas_pago"
      ),
      descripcion=item.get(
        "descripcion"
      ),
      url_extraccion=item.get(
        "url_extraccion"
      ),
      fecha_extraccion=(
        datetime.datetime.now()
      )
    )

    self.session.add(resultado)

    return item

  def close_spider(self, spider):
    """Confirma la transacción y libera la sesión."""

    try:

      self.session.commit()

    except Exception:

      self.session.rollback()

      raise

    finally:

      self.session.close()
