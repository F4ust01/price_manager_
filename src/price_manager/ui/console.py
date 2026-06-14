
import csv
import datetime

from price_manager.database.connection import ConexionDB

from price_manager.models.models import (
  CategoriaModel,
  ProveedorModel,
  ProductoModel,
  PrecioModel,
  MonedaModel,
  StockModel
)

from price_manager.repositories.repositories import (
  RepositorioCategoria,
  RepositorioProveedor,
  RepositorioProducto,
  RepositorioMoneda,
  RepositorioStock,
  RepositorioTipoCotizacion,
  RepositorioCotizacionDolar,
  RepositorioAuditoria
)

from price_manager.services.services import (
  ServicioCategoria,
  ServicioProveedor,
  ServicioProducto,
  ServicioMoneda,
  ServicioStock,
  ServicioTipoCotizacion,
  ServicioCotizacionDolar
)

from price_manager.services.scraping_services import (
  ServicioScraper,
  ServicioReporte
)


# Inicialización y configuración de dependencias de la aplicación.

def init_app() -> dict:
  """
  Inicializa el entorno de la aplicación de consola.

  Construye la sesión de la base de datos, instancia los repositorios
  y configura la inyección de dependencias para los servicios. Retorna
  un diccionario con todos los servicios disponibles.
  """

  db = ConexionDB()
  session = db.get_session()

  # Repositorios
  repo_cat = RepositorioCategoria(session)
  repo_prov = RepositorioProveedor(session)
  repo_prod = RepositorioProducto(session)
  repo_mon = RepositorioMoneda(session)
  repo_stock = RepositorioStock(session)
  repo_tipo = RepositorioTipoCotizacion(session)
  repo_cot = RepositorioCotizacionDolar(session)
  repo_aud = RepositorioAuditoria(session)

  # Servicios
  srv_cat = ServicioCategoria(repo_cat)
  srv_prov = ServicioProveedor(repo_prov)
  srv_mon = ServicioMoneda(repo_mon)
  srv_tipo = ServicioTipoCotizacion(repo_tipo)

  srv_prod = ServicioProducto(
    repo_prod,
    srv_cat,
    srv_prov
  )

  srv_stock = ServicioStock(
    repo_stock,
    srv_prod
  )

  srv_cot = ServicioCotizacionDolar(
    repo_cot,
    repo_tipo
  )

  return {
    "cat": srv_cat,
    "prov": srv_prov,
    "prod": srv_prod,
    "mon": srv_mon,
    "stock": srv_stock,
    "tipo": srv_tipo,
    "cot": srv_cot,
    "scraper": ServicioScraper(session),
    "reporte": ServicioReporte(session),
    "auditoria": repo_aud
  }


# Interfaces de menús y paneles de visualización.

def menu_principal() -> None:
  """Muestra en la terminal las opciones principales de navegación."""
  print("\n=== PRICE MANAGER ===")
  print("1. Productos")
  print("2. Stock")
  print("3. Cotizaciones")
  print("4. Catálogos (categorías/proveedores/monedas)")
  print("5. Obtener cotizaciones por API")
  print("6. Ver lista de precios bimonetaria")
  print("7. Exportar precios a CSV")
  print("8. Ejecutar scraping")
  print("9. Generar reporte")
  print("10. Ver historial de auditoría")
  print("0. Salir")


def menu_productos(ctx: dict) -> None:
  """Gestiona el submenú con el CRUD completo de los productos."""

  srv_prod = ctx["prod"]
  srv_cat = ctx["cat"]
  srv_prov = ctx["prov"]
  srv_mon = ctx["mon"]

  while True:

    print("\n--- Productos ---")
    print("1. Listar")
    print("2. Crear")
    print("3. Modificar")
    print("4. Eliminar")
    print("0. Volver")

    op = input("Opción: ")

    if op == "1":

      for p in srv_prod.listar_todos():
        precio = (
          p.precio.valor
          if p.precio
          else 0
        )
        print(
          p.id,
          p.nombre,
          f"${precio:.2f}"
        )

    elif op == "2":

      nombre = input("Nombre: ")
      descripcion = input("Descripción: ")
      valor = float(input("Precio: "))

      print("\nMonedas:")
      for m in srv_mon.listar_todos():
        print(m.id, m.nombre)

      moneda = srv_mon.obtener(
        int(input("Moneda ID: "))
      )

      print("\nCategorías:")
      for c in srv_cat.listar_todos():
        print(c.id, c.nombre)

      categoria = srv_cat.obtener(
        int(input("Categoría ID: "))
      )

      print("\nProveedores:")
      for pr in srv_prov.listar_todos():
        print(pr.id, pr.nombre)

      proveedor = srv_prov.obtener(
        int(input("Proveedor ID: "))
      )

      precio = PrecioModel(
        valor=valor,
        fecha=datetime.date.today(),
        moneda_id=moneda.id
      )

      producto = ProductoModel(
        nombre=nombre,
        descripcion=descripcion,
        categoria_id=categoria.id,
        proveedor_id=proveedor.id,
        precio=precio
      )

      srv_prod.crear(producto)

      print("Producto creado correctamente")

    elif op == "3":

      producto = srv_prod.obtener(
        int(input("ID a modificar: "))
      )

      if not producto:
        print("Producto inexistente")
        continue

      nombre = input(
        f"Nombre [{producto.nombre}]: "
      )

      if nombre:
        producto.nombre = nombre

      descripcion = input(
        f"Descripción "
        f"[{producto.descripcion}]: "
      )

      if descripcion:
        producto.descripcion = descripcion

      valor = input(
        f"Precio "
        f"[{producto.precio.valor}]: "
      )

      if valor:
        producto.precio.valor = float(valor)
        producto.precio.fecha = (
          datetime.date.today()
        )

      srv_prod.actualizar(producto)

      print("Producto actualizado")

    elif op == "4":

      if srv_prod.eliminar(
        int(input("ID a eliminar: "))
      ):
        print("Producto eliminado")
      else:
        print("Producto inexistente")

    elif op == "0":
      break


def menu_stock(ctx: dict) -> None:
  """Controla el submenú de gestión del inventario físico."""

  srv_stock = ctx["stock"]

  while True:

    print("\n--- Stock ---")
    print("1. Ver stock")
    print("2. Actualizar cantidad")
    print("0. Volver")

    op = input("Opción: ")

    if op == "1":

      for s in srv_stock.listar_todos():
        print(
          s.producto_id,
          s.producto.nombre,
          s.cantidad,
          s.almacen
        )

    elif op == "2":

      stock = (
        srv_stock.obtener_por_producto(
          int(input("Producto ID: "))
        )
      )

      if not stock:
        print("Stock inexistente")
        continue

      cantidad = int(
        input(
          f"Cantidad "
          f"[{stock.cantidad}]: "
        )
      )

      if cantidad < 0:
        print(
          "La cantidad no puede "
          "ser negativa"
        )
        continue

      stock.cantidad = cantidad

      srv_stock.actualizar(stock)

      print("Stock actualizado")

    elif op == "0":
      break


def menu_cotizaciones(ctx: dict) -> None:
  """Administra el submenú de revisión del historial cambiario."""

  srv_cot = ctx["cot"]
  srv_tipo = ctx["tipo"]

  while True:

    print("\n--- Cotizaciones ---")
    print("1. Ver histórico")
    print("0. Volver")

    op = input("Opción: ")

    if op == "1":

      for t in srv_tipo.listar_todos():
        print(t.id, t.nombre)

      historico = (
        srv_cot.obtener_historico(
          int(input("Tipo ID: "))
        )
      )

      for c in historico:
        print(c.fecha, c.valor)

    elif op == "0":
      break


def abm_generico(
  srv,
  nombre_entidad: str,
  campos: list,
  constructor
) -> None:
  """
  Submenú genérico de altas, bajas y modificaciones de catálogos.

  Reutiliza la misma lógica para categorías, proveedores y monedas,
  evitando duplicar código de menús con estructura idéntica.
  """

  while True:

    print(f"\n--- {nombre_entidad} ---")
    print("1. Listar")
    print("2. Crear")
    print("3. Modificar")
    print("4. Eliminar")
    print("0. Volver")

    op = input("Opción: ")

    if op == "1":

      for entidad in srv.listar_todos():
        valores = [
          getattr(entidad, campo)
          for campo in campos
        ]
        print(entidad.id, *valores)

    elif op == "2":

      datos = {
        campo: input(f"{campo}: ")
        for campo in campos
      }

      srv.crear(constructor(**datos))

      print(f"{nombre_entidad} creado/a")

    elif op == "3":

      entidad = srv.obtener(
        int(input("ID a modificar: "))
      )

      if not entidad:
        print("Registro inexistente")
        continue

      for campo in campos:

        actual = getattr(entidad, campo)

        nuevo = input(
          f"{campo} [{actual}]: "
        )

        if nuevo:
          setattr(entidad, campo, nuevo)

      srv.actualizar(entidad)

      print("Registro actualizado")

    elif op == "4":

      if srv.eliminar(
        int(input("ID a eliminar: "))
      ):
        print("Registro eliminado")
      else:
        print("Registro inexistente")

    elif op == "0":
      break


def menu_catalogos(ctx: dict) -> None:
  """Agrupa los ABM de las entidades de catálogo del sistema."""

  while True:

    print("\n--- Catálogos ---")
    print("1. Categorías")
    print("2. Proveedores")
    print("3. Monedas")
    print("0. Volver")

    op = input("Opción: ")

    if op == "1":

      abm_generico(
        ctx["cat"],
        "Categorías",
        ["nombre"],
        CategoriaModel
      )

    elif op == "2":

      abm_generico(
        ctx["prov"],
        "Proveedores",
        ["nombre", "contacto"],
        ProveedorModel
      )

    elif op == "3":

      abm_generico(
        ctx["mon"],
        "Monedas",
        ["nombre"],
        MonedaModel
      )

    elif op == "0":
      break


# Integraciones y procedimientos de los ejercicios.

def obtener_cotizaciones_api(ctx: dict) -> None:
  """Consulta y persiste las cotizaciones actuales desde la API externa."""

  print("\nConsultando API de cotizaciones...")

  try:

    ctx["cot"].obtener_cotizaciones()

    print("Cotizaciones actualizadas correctamente.")

  except Exception as error:

    print(f"Error al obtener cotizaciones: {error}")


def ver_lista_bimonetaria(ctx: dict) -> None:
  """
  Muestra los precios de los productos en pesos y dólares en la terminal.

  Calcula la equivalencia bimonetaria utilizando la última cotización
  disponible del catálogo correspondiente al identificador seleccionado.
  """

  srv_prod = ctx["prod"]
  srv_cot = ctx["cot"]
  srv_tipo = ctx["tipo"]

  tipos = srv_tipo.listar_todos()

  if not tipos:
    print("\nNo hay tipos de cotización registrados.")
    return

  print("\n--- Tipos de cotización disponibles ---")

  for t in tipos:
    print(t.id, t.nombre)

  tipo_id = int(input("\nSeleccione Tipo ID: "))

  try:

    historico = srv_cot.obtener_historico(tipo_id)

  except ValueError as error:

    print(f"Error: {error}")
    return

  if not historico:
    print("\nNo hay cotizaciones para ese tipo.")
    return

  # Se obtiene el registro de cotización más reciente de la colección.
  ultima = sorted(
    historico,
    key=lambda c: c.fecha,
    reverse=True
  )[0]

  dolar = ultima.valor

  productos = srv_prod.listar_todos()

  print(f"\nCotización usada: ${dolar:.2f} (al {ultima.fecha})")
  print("-" * 60)

  for p in productos:

    ars = p.precio.valor if p.precio else 0

    usd = ars / dolar if dolar > 0 else 0

    print(
      f"{p.nombre} | "
      f"ARS ${ars:.2f} | "
      f"USD {usd:.2f}"
    )


def exportar_precios_csv(ctx: dict) -> None:
  """
  Exporta la lista de precios consolidada a un archivo en formato CSV.

  Genera una matriz de columnas dinámicas que calcula los precios de cada
  producto tanto en pesos argentinos como en cada tipo de dólar disponible.
  """

  srv_prod = ctx["prod"]
  srv_cot = ctx["cot"]
  srv_tipo = ctx["tipo"]

  productos = srv_prod.listar_todos()
  tipos = srv_tipo.listar_todos()

  # Obtener la última cotización por cada tipo.
  cotizaciones = {}

  for tipo in tipos:

    try:

      historico = srv_cot.obtener_historico(tipo.id)

    except ValueError:

      continue

    if historico:

      ultima = sorted(
        historico,
        key=lambda c: c.fecha,
        reverse=True
      )[0]

      cotizaciones[tipo.nombre] = ultima.valor

  nombre_archivo = (
    f"lista_precios_{datetime.date.today()}.csv"
  )

  try:

    with open(
      nombre_archivo,
      mode="w",
      newline="",
      encoding="utf-8"
    ) as archivo:

      writer = csv.writer(archivo)

      # Encabezados dinámicos según tipos de cotización.
      encabezados = ["ID", "Producto", "Precio ARS"]
      encabezados.extend(
        [f"USD {nombre}" for nombre in cotizaciones.keys()]
      )

      writer.writerow(encabezados)

      for p in productos:

        precio_ars = p.precio.valor if p.precio else 0

        fila = [
          p.id,
          p.nombre,
          round(precio_ars, 2)
        ]

        for valor_tipo in cotizaciones.values():

          precio_usd = (
            precio_ars / valor_tipo
            if valor_tipo > 0
            else 0
          )

          fila.append(round(precio_usd, 2))

        writer.writerow(fila)

    print(f"\nCSV exportado correctamente: {nombre_archivo}")

  except Exception as error:

    print(f"\nError al exportar CSV: {error}")


def ejecutar_scraping_consola(ctx: dict) -> None:
  """
  Solicita el umbral de alerta y lanza el scraper de la competencia.

  La diferencia de precios para generar alertas debe ser ingresada
  por el usuario antes de cada ejecución del scraper.
  """

  try:

    umbral = float(
      input(
        "Diferencia mínima de precios "
        "para alertar ($): "
      )
    )

  except ValueError:

    print("El umbral debe ser numérico.")
    return

  ctx["scraper"].ejecutar_scraping(umbral)


def generar_reporte_consola(ctx: dict) -> None:
  """Genera el reporte comparativo de precios en formato Excel."""

  try:

    ctx["reporte"].generar_reporte_excel()

  except ValueError as error:

    print(f"Error: {error}")


def ver_auditoria(ctx: dict) -> None:
  """Muestra los últimos registros del historial de auditoría."""

  registros = (
    ctx["auditoria"].leer_ultimos(20)
  )

  if not registros:
    print("\nNo hay registros de auditoría.")
    return

  print("\n--- Historial de auditoría ---")

  for registro in registros:

    fecha = registro.fecha.strftime(
      "%Y-%m-%d %H:%M:%S"
    )

    print(
      f"{fecha} | "
      f"{registro.accion} | "
      f"{registro.detalles[:80]}"
    )


# Bucle de control principal de la aplicación.

def run() -> None:
  """Ejecuta el ciclo de vida continuo de la interfaz de consola."""

  ctx = init_app()

  opciones = {
    "1": menu_productos,
    "2": menu_stock,
    "3": menu_cotizaciones,
    "4": menu_catalogos,
    "5": obtener_cotizaciones_api,
    "6": ver_lista_bimonetaria,
    "7": exportar_precios_csv,
    "8": ejecutar_scraping_consola,
    "9": generar_reporte_consola,
    "10": ver_auditoria
  }

  while True:

    menu_principal()

    op = input("Opción: ")

    if op == "0":
      print("Saliendo...")
      break

    accion = opciones.get(op)

    if accion:
      accion(ctx)
    else:
      print("Opción inválida")
