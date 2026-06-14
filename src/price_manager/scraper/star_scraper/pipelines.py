
import csv
import datetime
import os

from scrapy.exceptions import DropItem

from price_manager.database.connection import (
  ConexionDB
)

from price_manager.models.models import (
  Base,
  ResultadoScrapingModel
)

# Carpeta donde se depositan los archivos descargables del sistema.
RUTA_REPORTES = (
  "/content/price_manager/reportes"
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


class ComparacionAlertasPipeline:
  """
  Compara el precio interno con el precio web y genera las alertas.

  En cada ejecución del spider se crea un archivo CSV descargable con
  los productos cuya diferencia de precios supera el umbral ingresado
  por el usuario antes de la corrida.
  """

  def open_spider(self, spider):
    """Crea el archivo CSV de alertas de la ejecución actual."""

    os.makedirs(
      RUTA_REPORTES,
      exist_ok=True
    )

    marca_tiempo = (
      datetime.datetime.now().strftime(
        "%Y-%m-%d_%H%M%S"
      )
    )

    self.ruta_csv = os.path.join(
      RUTA_REPORTES,
      f"alertas_precios_{marca_tiempo}.csv"
    )

    self.archivo = open(
      self.ruta_csv,
      mode="w",
      newline="",
      encoding="utf-8"
    )

    self.writer = csv.writer(
      self.archivo
    )

    self.writer.writerow([
      "producto_id",
      "producto",
      "nombre_web",
      "precio_interno",
      "precio_web",
      "diferencia",
      "umbral",
      "fecha"
    ])

    self.alertas: int = 0

  def process_item(self, item, spider):
    """Calcula la diferencia y registra la alerta si supera el umbral."""

    diferencia = round(
      item["precio_web"]
      -
      item["precio_interno"],
      2
    )

    item["diferencia"] = diferencia

    if abs(diferencia) >= spider.umbral:

      self.writer.writerow([
        item["producto_id"],
        item["nombre_interno"],
        item.get("nombre_web", ""),
        round(
          item["precio_interno"],
          2
        ),
        round(item["precio_web"], 2),
        diferencia,
        spider.umbral,
        datetime.date.today()
      ])

      self.alertas += 1

    return item

  def close_spider(self, spider):
    """Cierra el CSV e informa la ubicación del archivo de alertas."""

    self.archivo.close()

    spider.logger.info(
      "Alertas generadas: %s | "
      "Archivo: %s",
      self.alertas,
      self.ruta_csv
    )

    print(
      f"\nArchivo de alertas generado: "
      f"{self.ruta_csv} "
      f"({self.alertas} alertas)"
    )


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

      print(
        "\n[SCRAPING] Resultados "
        "persistidos en la base de datos."
      )

    except Exception:

      self.session.rollback()

      raise

    finally:

      self.session.close()
