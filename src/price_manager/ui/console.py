
import datetime

from price_manager.database.connection import ConexionDB

from price_manager.models.models import (
  CategoriaModel,
  ProveedorModel,
  ProductoModel,
  PrecioModel,
  MonedaModel,
  StockModel,
  TipoCotizacionModel,
  CotizacionDolarModel
)

from price_manager.repositories.repositories import (
  RepositorioCategoria,
  RepositorioProveedor,
  RepositorioProducto,
  RepositorioMoneda,
  RepositorioStock,
  RepositorioTipoCotizacion,
  RepositorioCotizacionDolar
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

# Inicialización y configuración de dependencias de la aplicación.

def init_app():
  """
  Inicializa el entorno de la aplicación web o de consola.

  Construye la sesión de la base de datos, instancia todos los repositorios
  y configura la inyección de dependencias para las clases de servicios.
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

  return (
    srv_cat,
    srv_prov,
    srv_prod,
    srv_stock,
    srv_cot,
    srv_mon,
    srv_tipo
  )


# Interfaces de menús y paneles de visualización.

def menu_principal():
  """Muestra en la terminal las opciones principales de navegación."""
  print("\n=== PRICE MANAGER ===")
  print("1. Productos")
  print("2. Stock")
  print("3. Cotizaciones")
  print("0. Salir")

#Gestiona el submenú operativo y de creación para los productos.

def menu_productos(
  srv_prod,
  srv_cat,
  srv_prov,
  srv_mon
):

  while True:

    print("\n--- Productos ---")
    print("1. Listar")
    print("2. Crear")
    print("0. Volver")

    op = input("Opción: ")

    if op == "1":

      productos = srv_prod.listar_todos()

      for p in productos:
        print(
          p.id,
          p.nombre
        )

    elif op == "2":

      nombre = input("Nombre: ")
      descripcion = input("Descripción: ")
      valor = float(input("Precio: "))

      print("\nMonedas:")
      monedas = srv_mon.listar_todos()

      for m in monedas:
        print(m.id, m.nombre)

      moneda_id = int(input("Moneda ID: "))
      moneda = srv_mon.obtener(moneda_id)

      print("\nCategorías:")
      categorias = srv_cat.listar_todos()

      for c in categorias:
        print(c.id, c.nombre)

      categoria_id = int(input("Categoria ID: "))
      categoria = srv_cat.obtener(categoria_id)

      print("\nProveedores:")
      proveedores = srv_prov.listar_todos()

      for p in proveedores:
        print(p.id, p.nombre)

      proveedor_id = int(input("Proveedor ID: "))
      proveedor = srv_prov.obtener(proveedor_id)

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

    elif op == "0":
      break


def menu_stock(srv_stock):
  """Controla el submenú de visualización de inventario físico."""
  while True:

    print("\n--- Stock ---")
    print("1. Ver stock")
    print("0. Volver")

    op = input("Opción: ")

    if op == "1":

      stocks = srv_stock.listar_todos()

      for s in stocks:
        print(
          s.producto_id,
          s.cantidad
        )

    elif op == "0":
      break

#Administra el submenú de revisión del historial cambiario.

def menu_cotizaciones(
  srv_cot,
  srv_tipo
):

  while True:

    print("\n--- Cotizaciones ---")
    print("1. Ver histórico")
    print("0. Volver")

    op = input("Opción: ")

    if op == "1":

      tipos = srv_tipo.listar_todos()

      for t in tipos:
        print(t.id, t.nombre)

      tipo_id = int(input("Tipo ID: "))

      historico = srv_cot.obtener_historico(
        tipo_id
      )

      for c in historico:
        print(
          c.fecha,
          c.valor
        )

    elif op == "0":
      break


# Bucle de control principal de la aplicación.

def run():
  """Ejecuta el ciclo de vida continuo de la interfaz de consola."""
  (
    srv_cat,
    srv_prov,
    srv_prod,
    srv_stock,
    srv_cot,
    srv_mon,
    srv_tipo
  ) = init_app()

  while True:

    menu_principal()

    op = input("Opción: ")

    if op == "1":

      menu_productos(
        srv_prod,
        srv_cat,
        srv_prov,
        srv_mon
      )

    elif op == "2":

      menu_stock(
        srv_stock
      )

    elif op == "3":

      menu_cotizaciones(
        srv_cot,
        srv_tipo
      )

    elif op == "0":

      print("Saliendo...")
      break
