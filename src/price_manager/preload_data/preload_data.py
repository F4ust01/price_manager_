
import csv
import datetime

from price_manager.entities.entities import (
  Categoria, Proveedor, Producto,
  Precio, Stock, CotizacionDolar,
  Moneda, TipoCotizacion
)


def preload_all(
  repo_cat, repo_prov, repo_prod,
  repo_stock, repo_cot,
  repo_mon, repo_tipo
):

  # Monedas
  with open("price_manager/migrations/csv/monedas.csv") as f:
    for r in csv.DictReader(f):
      repo_mon.crear(Moneda(int(r["id"]), r["nombre"]))

  # Tipos
  with open("price_manager/migrations/csv/tipos_cotizacion.csv") as f:
    for r in csv.DictReader(f):
      repo_tipo.crear(TipoCotizacion(int(r["id"]), r["nombre"]))

  # Categorías
  with open("price_manager/migrations/csv/categorias.csv") as f:
    for r in csv.DictReader(f):
      repo_cat.crear(Categoria(int(r["id"]), r["nombre"]))

  # Proveedores
  with open("price_manager/migrations/csv/proveedores.csv") as f:
    for r in csv.DictReader(f):
      repo_prov.crear(
        Proveedor(int(r["id"]), r["nombre"], r["contacto"])
      )

  # Productos
  with open("price_manager/migrations/csv/productos.csv") as f:
    for r in csv.DictReader(f):

      moneda = repo_mon.leer_por_id(int(r["moneda_id"]))
      categoria = repo_cat.leer_por_id(int(r["categoria_id"]))
      proveedor = repo_prov.leer_por_id(int(r["proveedor_id"]))

      precio = Precio(
        float(r["valor"]),
        moneda,
        datetime.date.today()
      )

      repo_prod.crear(
        Producto(
          int(r["id"]),
          r["nombre"],
          r["descripcion"],
          precio,
          categoria,
          proveedor
        )
      )

  # Stock
  with open("price_manager/migrations/csv/stock.csv") as f:
    for r in csv.DictReader(f):
      prod = repo_prod.leer_por_id(int(r["producto_id"]))
      repo_stock.crear(
        Stock(prod, int(r["cantidad"]), r["almacen"])
      )

  # Cotizaciones
  with open("price_manager/migrations/csv/cotizaciones.csv") as f:
    for r in csv.DictReader(f):

      tipo = repo_tipo.leer_por_id(int(r["tipo_id"]))

      repo_cot.crear(
        CotizacionDolar(
          float(r["valor"]),
          datetime.datetime.strptime(r["fecha"], "%Y-%m-%d").date(),
          tipo
        )
      )
