
import json
import os
import subprocess
import sys

from price_manager.models.models import (
  ProductoModel,
  CotizacionDolarModel,
  ResultadoScrapingModel
)

# Rutas del proyecto calculadas desde la ubicación de este módulo.
RUTA_PAQUETE = os.path.dirname(
  os.path.dirname(
    os.path.abspath(__file__)
  )
)

RUTA_SCRAPER = os.path.join(
  RUTA_PAQUETE,
  "scraper"
)

RUTA_SRC = os.path.dirname(
  RUTA_PAQUETE
)


class ServicioScraper:
  """
  Orquesta la ejecución del spider de Star Computación.

  Prepara el catálogo propio con los precios expresados en pesos y
  lanza el proceso de Scrapy en un subproceso, lo que permite ejecutar
  el scraping varias veces dentro de una misma sesión de la consola.
  """

  def __init__(self, session):
    """Inicializa el servicio con una sesión activa de base de datos."""

    self.session = session

  def _ultima_cotizacion(self):
    """Retorna el valor de la cotización más reciente registrada."""

    cotizacion = self.session.query(
      CotizacionDolarModel
    ).order_by(
      CotizacionDolarModel.fecha.desc(),
      CotizacionDolarModel.id.desc()
    ).first()

    return (
      cotizacion.valor
      if cotizacion
      else None
    )

  def _precio_en_pesos(
    self,
    producto,
    cotizacion
  ) -> float:
    """
    Convierte el precio interno del producto a pesos argentinos.

    Los precios web de la competencia están en pesos, por lo que los
    precios propios en otra divisa se convierten con la última
    cotización disponible para que la comparación sea homogénea.
    """

    valor = producto.precio.valor

    moneda = (
      producto.precio.moneda.nombre
    )

    if moneda == "ARS":

      return valor

    if cotizacion:

      return valor * cotizacion

    return valor

  def _preparar_catalogo(self) -> tuple:
    """Genera el JSON con los productos propios para el spider."""

    cotizacion = (
      self._ultima_cotizacion()
    )

    productos = self.session.query(
      ProductoModel
    ).all()

    catalogo = [
      {
        "id": p.id,
        "nombre": p.nombre,
        "precio_interno": round(
          self._precio_en_pesos(
            p,
            cotizacion
          ),
          2
        )
      }
      for p in productos
    ]

    ruta_json = os.path.join(
      RUTA_SCRAPER,
      "productos_propios.json"
    )

    with open(
      ruta_json,
      mode="w",
      encoding="utf-8"
    ) as archivo:

      json.dump(
        catalogo,
        archivo,
        ensure_ascii=False,
        indent=2
      )

    return ruta_json, catalogo

  def _contar_resultados(self) -> int:
    """Cuenta los resultados de scraping persistidos en la base."""

    return self.session.query(
      ResultadoScrapingModel
    ).count()

  def ejecutar_scraping(
    self,
    umbral: float
  ) -> bool:
    """
    Ejecuta el spider con el umbral de alerta indicado por el usuario.

    Retorna True si el proceso guardó al menos un resultado nuevo.
    """

    ruta_json, catalogo = (
      self._preparar_catalogo()
    )

    if not catalogo:

      print(
        "No hay productos cargados "
        "en la base de datos: el "
        "spider no tiene nada que "
        "buscar. Cargue productos "
        "(opción 1 o la celda de "
        "carga de datos) y vuelva "
        "a intentar."
      )

      return False

    print(f"\nBuscando {len(catalogo)} productos en el sitio.")

    print("Productos a buscar:")

    for indice, producto in enumerate(
      catalogo,
      start=1
    ):

      print(
        f"  {indice}. {producto['nombre']} "
        f"(precio interno: "
        f"${producto['precio_interno']})"
      )

    print(
      "\nLanzando el scraper... El detalle "
      "de cada búsqueda se mostrará al "
      "finalizar el proceso.\n"
    )

    resultados_previos = (
      self._contar_resultados()
    )

    entorno = os.environ.copy()

    entorno["PYTHONPATH"] = (
      f"{RUTA_SRC}{os.pathsep}"
      f"{RUTA_SCRAPER}"
    )

    proceso = subprocess.run(
      [
        sys.executable,
        "-m",
        "scrapy",
        "crawl",
        "star_computacion",
        "-a",
        f"productos_json={ruta_json}",
        "-a",
        f"umbral={umbral}",
        "-L",
        "INFO"
      ],
      cwd=RUTA_SCRAPER,
      env=entorno,
      capture_output=True,
      text=True
    )

    registro = (
      (proceso.stdout or "")
      + "\n"
      + (proceso.stderr or "")
    )

    if proceso.returncode != 0:

      print(
        "El scraping finalizó "
        "con errores."
      )

      self._mostrar_log(registro, ultimas=25)

      return False

    # La sesión se sincroniza para ver lo escrito por el subproceso.
    self.session.expire_all()

    nuevos = (
      self._contar_resultados()
      - resultados_previos
    )

    print(
      f"\n[SCRAPING] Finalizado. "
      f"Resultados nuevos guardados: "
      f"{nuevos}."
    )

    print(
      "\n--- Detalle del proceso de "
      "búsqueda ---"
    )

    self._mostrar_log(registro, filtro="[SCRAPING]")

    if nuevos == 0:

      print(
        "No se guardaron resultados "
        "nuevos. Últimas líneas del "
        "log de Scrapy (si aparece "
        "HTTP 403, el sitio bloquea "
        "los pedidos desde "
        "servidores en la nube y "
        "debe ejecutarse localmente):"
      )

      self._mostrar_log(registro, ultimas=25)

      return False

    return True

  def _mostrar_log(
    self,
    registro: str,
    filtro: str = "",
    ultimas: int = 0
  ) -> None:
    """Imprime líneas del log del spider, con filtro o tope opcionales."""

    lineas = registro.split("\n")

    if filtro:
      lineas = [l for l in lineas if filtro in l]

    if ultimas:
      lineas = lineas[-ultimas:]

    if not lineas:
      print("  (sin información disponible)")
      return

    for linea in lineas:
      inicio = linea.find(filtro) if filtro else 0
      print(f"  {linea[inicio:]}")


# =========================================
# REPORTE COMPARATIVO EN EXCEL
# =========================================

from openpyxl import Workbook
from openpyxl.styles import Font

from price_manager.models.models import (
  ResultadoScrapingModel
)

import datetime

RUTA_REPORTES = (
  "/content/price_manager/reportes"
)


class ServicioReporte:
  """Genera el reporte comparativo de precios en formato Excel."""

  def __init__(self, session):
    """Inicializa el servicio con una sesión activa de base de datos."""

    self.session = session

  def generar_reporte_excel(self) -> str:
    """
    Crea un archivo .xlsx con la comparativa interna contra la web.

    Las columnas del reporte son: Producto, Precio interno, Precio
    web, Diferencia y Fecha de extracción. Retorna la ruta del archivo.
    """

    resultados = self.session.query(
      ResultadoScrapingModel
    ).order_by(
      ResultadoScrapingModel
      .fecha_extraccion
      .desc()
    ).all()

    if not resultados:

      raise ValueError(
        "No hay resultados de scraping. "
        "Ejecute primero el scraper."
      )

    os.makedirs(
      RUTA_REPORTES,
      exist_ok=True
    )

    libro = Workbook()

    hoja = libro.active

    hoja.title = "Comparativa"

    encabezados = [
      "Producto",
      "Precio interno",
      "Precio web",
      "Diferencia",
      "Fecha de extracción"
    ]

    hoja.append(encabezados)

    # Se resaltan los encabezados del reporte.
    for celda in hoja[1]:

      celda.font = Font(bold=True)

    for resultado in resultados:

      # Si el producto interno no está disponible se utiliza el
      # nombre publicado en la web como referencia.
      nombre = (
        resultado.producto.nombre
        if resultado.producto is not None
        else resultado.nombre_web
      )

      hoja.append([
        nombre,
        round(
          resultado.precio_interno,
          2
        ),
        round(
          resultado.precio_web,
          2
        ),
        round(
          resultado.diferencia,
          2
        ),
        resultado
        .fecha_extraccion
        .strftime("%Y-%m-%d %H:%M")
      ])

    # Ajuste simple del ancho de las columnas.
    anchos = [35, 16, 16, 14, 20]

    for indice, ancho in enumerate(
      anchos,
      start=1
    ):

      letra = hoja.cell(
        row=1,
        column=indice
      ).column_letter

      hoja.column_dimensions[
        letra
      ].width = ancho

    marca_tiempo = (
      datetime.datetime.now().strftime(
        "%Y-%m-%d_%H%M%S"
      )
    )

    ruta_excel = os.path.join(
      RUTA_REPORTES,
      f"reporte_precios_{marca_tiempo}.xlsx"
    )

    libro.save(ruta_excel)

    print(
      f"Reporte generado: {ruta_excel}"
    )

    return ruta_excel
