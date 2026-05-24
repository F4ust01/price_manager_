
from typing import List, Optional, TypeVar, Generic

from price_manager.entities.entities import (
  Categoria, Proveedor, Producto,
  Stock, CotizacionDolar,
  Moneda, TipoCotizacion
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


class ServicioBase:
  """Clase base para los servicios con operaciones CRUD"""

  def __init__(self, repo):
    """inicializza el servicio con su repositorio correspondiente"""
    self.repo = repo

  def crear(self, entidad):
    """Crea una nueva entidad en el repositorio"""
    return self.repo.crear(entidad)

  def obtener(self, id):
    """Obtiene una entidad por su ID"""
    entidad = self.repo.leer_por_id(id)
    if not entidad:
      raise ValueError("Entidad no encontrada")
    return entidad

  def listar_todos(self):
    """Obtiene una lista con todas las entidades"""
    return self.repo.leer_todos()

  def actualizar(self, entidad):
    """Actualiza una entidad existente en el repositorio"""
    return self.repo.actualizar(entidad)

  def eliminar(self, id):
    """Elimina una entidad por su ID"""
    if not self.repo.eliminar(id):
      raise ValueError("Entidad no encontrada")


"""Implementacion de los servicios para cada entidad"""

class ServicioCategoria(ServicioBase): pass
"""servicios especializados para la gestion de la entidad categoria"""

class ServicioProveedor(ServicioBase): pass
"""servicios especializados para la gestion de la entidad proveedor"""

class ServicioMoneda(ServicioBase): pass
"""servicios especializados para la gestion de la entidad moneda"""

class ServicioTipoCotizacion(ServicioBase): pass
"""servicios especializados para la gestion de la entidad tipoCotizacion"""



class ServicioProducto(ServicioBase):
  """Servicio especializado para la gestión de la entidad producto
  con su validacion donde se asegura que este vinculado a una categoria y proveedor valido """

  def __init__(self, repo: RepositorioProducto,
               srv_cat: ServicioCategoria,
               srv_prov: ServicioProveedor):

    super().__init__(repo)
    self.srv_cat = srv_cat
    self.srv_prov = srv_prov

  def crear(self, producto: Producto) -> Producto:
    """Crea un nuevo producto en el repositorio validando la existencia de las relaciones"""
    self.srv_cat.obtener(producto.categoria.id)
    self.srv_prov.obtener(producto.proveedor.id)

    return self.repo.crear(producto)

class ServicioStock:
  """Servicio especializado para la gestión de la entidad stock"""

  def __init__(self, repo: RepositorioStock,
               srv_prod: ServicioProducto):
    self.repo = repo
    self.srv_prod = srv_prod

  def registrar_movimiento(self, producto_id: int,
                           cantidad: int):
    """Registra un movimiento de stock para un producto especifico
    si el movimiento resulta en existencias negativas lanza un error"""

    producto = self.srv_prod.obtener(producto_id)
    stock = self.repo.leer_por_producto(producto_id)

    if not stock:
      """ Inicia de manera automatica un stock de 0 para los productos que no tengan uno"""
      stock = Stock(producto, 0, "default")
      self.repo.crear(stock)

    nuevo = stock.cantidad + cantidad

    if nuevo < 0:
      raise ValueError("Stock negativo")

    stock.cantidad = nuevo
    self.repo.actualizar(stock)

  def obtener_stock(self, producto_id: int) -> int:
    """Obtiene el stock de un producto especifico"""
    stock = self.repo.leer_por_producto(producto_id)
    return stock.cantidad if stock else 0

class ServicioCotizacionDolar:
  """Servicio especializado para la gestión de la entidad cotizacionDolar"""
  def __init__(self, repo: RepositorioCotizacionDolar,
               tipo_repo: RepositorioTipoCotizacion):

    self.repo = repo
    self.tipo_repo = tipo_repo

  def registrar_cotizacion(self, cotizacion: CotizacionDolar):
    """Añade una nueva cotización en el repositorio"""
    return self.repo.crear(cotizacion)

  def obtener_historico(self, tipo_id: int) -> List[CotizacionDolar]:
    """Obtiene el historico de cotizaciones de un tipo especifico"""

    tipo = self.tipo_repo.leer_por_id(tipo_id)
    if not tipo:
      raise ValueError("Tipo no existe")

    return self.repo.leer_historico_por_tipo(tipo)
