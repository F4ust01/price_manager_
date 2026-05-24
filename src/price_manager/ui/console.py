
import datetime

from price_manager.entities.entities import (
  Producto, Precio, CotizacionDolar
)

from price_manager.repositories.repositories import (
  RepositorioCategoria,
  RepositorioProveedor,
  RepositorioProducto,
  RepositorioStock,
  RepositorioCotizacionDolar,
  RepositorioMoneda,
  RepositorioTipoCotizacion
)

from price_manager.services.services import (
  ServicioCategoria,
  ServicioProveedor,
  ServicioProducto,
  ServicioStock,
  ServicioCotizacionDolar,
  ServicioMoneda,
  ServicioTipoCotizacion
)

from price_manager.preload_data.preload_data import preload_all

# ======================
# INIT & CONFIGURACIÓN
# ======================

# Este módulo define toda la interfaz de consola del sistema:
# inicialización de repositorios/servicios y los menús para gestionar
# productos, stock y cotizaciones dentro del Price Manager.


def init_app(import_default_data: bool = True):
  """
  Inicializa los repositorios y servicios del sistema.
  Opcionalmente carga los datos por defecto desde los CSV.
  """

  # Crear instancias de repositorios (capa de persistencia).
  repo_cat = RepositorioCategoria()
  repo_prov = RepositorioProveedor()
  repo_prod = RepositorioProducto()
  repo_stock = RepositorioStock()
  repo_cot = RepositorioCotizacionDolar()
  repo_mon = RepositorioMoneda()
  repo_tipo = RepositorioTipoCotizacion()

  # Importación de datos iniciales si está habilitada.
  if import_default_data:
    preload_all(
      repo_cat, repo_prov, repo_prod,
      repo_stock, repo_cot,
      repo_mon, repo_tipo
    )

  # Crear servicios (capa de lógica).
  srv_cat = ServicioCategoria(repo_cat)
  srv_prov = ServicioProveedor(repo_prov)
  srv_mon = ServicioMoneda(repo_mon)
  srv_tipo = ServicioTipoCotizacion(repo_tipo)

  # Servicios que dependen de otros servicios/repos.
  srv_prod = ServicioProducto(repo_prod, srv_cat, srv_prov)
  srv_stock = ServicioStock(repo_stock, srv_prod)
  srv_cot = ServicioCotizacionDolar(repo_cot, repo_tipo)

  # Se devuelven todos los servicios listos para usar en la UI.
  return (
    srv_cat, srv_prov, srv_prod,
    srv_stock, srv_cot,
    srv_mon, srv_tipo
  )


# ======================
# MENÚ PRINCIPAL
# ======================

def menu_principal():
  """Imprime el menú principal del sistema."""
  print("\n=== PRICE MANAGER ===")
  print("1. Productos")
  print("2. Stock")
  print("3. Cotización")
  print("0. Salir")


# ======================
# PRODUCTOS
# ======================

def menu_productos(srv_prod, srv_cat, srv_prov, srv_mon):
  """
  Menú para operar con productos:
  listar productos existentes y crear nuevos.
  """

  while True:
    print("\n--- Productos ---")
    print("1. Listar")
    print("2. Crear")
    print("0. Volver")

    op = input("Opción: ")

    # Mostrar todos los productos registrados.
    if op == "1":
      for p in srv_prod.listar_todos():
        print(p.id, p.nombre, p.precio.valor, p.precio.moneda.nombre)

    # Crear un nuevo producto solicitando sus datos.
    elif op == "2":
      id = int(input("ID: "))
      nombre = input("Nombre: ")
      desc = input("Descripción: ")
      valor = float(input("Precio: "))

      # Selección de moneda.
      print("Monedas:")
      for m in srv_mon.listar_todos():
        print(m.id, m.nombre)
      moneda_id = int(input("Moneda ID: "))
      moneda = srv_mon.obtener(moneda_id)

      # Selección de categoría.
      print("Categorías:")
      for c in srv_cat.listar_todos():
        print(c.id, c.nombre)
      cat_id = int(input("Categoria ID: "))
      categoria = srv_cat.obtener(cat_id)

      # Selección de proveedor.
      print("Proveedores:")
      for p in srv_prov.listar_todos():
        print(p.id, p.nombre)
      prov_id = int(input("Proveedor ID: "))
      proveedor = srv_prov.obtener(prov_id)

      # Crear entidades asociadas al producto.
      precio = Precio(valor, moneda, datetime.date.today())
      prod = Producto(id, nombre, desc, precio, categoria, proveedor)

      # Registro del producto.
      srv_prod.crear(prod)

    elif op == "0":
      break


# ======================
# STOCK
# ======================

def menu_stock(srv_stock):
  """
  Menú para registrar movimientos de stock
  y consultar el nivel actual de un producto.
  """

  while True:
    print("\n--- Stock ---")
    print("1. Movimiento")
    print("2. Ver stock")
    print("0. Volver")

    op = input("Opción: ")

    # Registrar entrada o salida de stock.
    if op == "1":
      pid = int(input("Producto ID: "))
      cant = int(input("Cantidad (+/-): "))
      srv_stock.registrar_movimiento(pid, cant)

    # Consultar el stock actual de un producto.
    elif op == "2":
      pid = int(input("Producto ID: "))
      print("Stock:", srv_stock.obtener_stock(pid))

    elif op == "0":
      break


# ======================
# COTIZACION
# ======================

def menu_cotizacion(srv_cot, srv_tipo):
  """
  Menú para gestionar cotizaciones del dólar:
  registrar una nueva y consultar el histórico por tipo.
  """

  while True:
    print("\n--- Cotización ---")
    print("1. Registrar")
    print("2. Histórico")
    print("0. Volver")

    op = input("Opción: ")

    # Registrar una nueva cotización.
    if op == "1":
      valor = float(input("Valor: "))

      # Mostrar tipos de cotización disponibles.
      print("Tipos:")
      for t in srv_tipo.listar_todos():
        print(t.id, t.nombre)

      tipo_id = int(input("Tipo ID: "))
      tipo = srv_tipo.obtener(tipo_id)

      # Crear la entidad de cotización y registrarla.
      cot = CotizacionDolar(valor, datetime.date.today(), tipo)
      srv_cot.registrar_cotizacion(cot)

    # Mostrar histórico filtrado por tipo.
    elif op == "2":
      tipo_id = int(input("Tipo ID: "))
      hist = srv_cot.obtener_historico(tipo_id)

      for c in hist:
        print(c.fecha, c.valor)

    elif op == "0":
      break


# ======================
# MAIN LOOP
# ======================

def run(import_default_data: bool = True):
  """
  Ejecuta el ciclo principal de la aplicación de consola.
  Controla la navegación entre los distintos menús.
  """

  # Inicialización completa del sistema.
  (
    srv_cat, srv_prov, srv_prod,
    srv_stock, srv_cot,
    srv_mon, srv_tipo
  ) = init_app(import_default_data)

  # Bucle principal de interacción con el usuario.
  while True:
    menu_principal()
    op = input("Opción: ")

    if op == "1":
      menu_productos(srv_prod, srv_cat, srv_prov, srv_mon)

    elif op == "2":
      menu_stock(srv_stock)

    elif op == "3":
      menu_cotizacion(srv_cot, srv_tipo)

    elif op == "0":
      print("Saliendo...")
      break
