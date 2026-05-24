
import abc
from typing import TypeVar, Generic, List, Optional


# importaciones locales organizadas segun procedencia.
from price_manager.entities.entities import (
  Categoria, Proveedor, Producto,
  Stock, CotizacionDolar,
  Moneda, TipoCotizacion
)

# Definición de tipo genérico para los repositorios.
T = TypeVar('T')


class IRepositorio(abc.ABC, Generic[T]):
  """interfaz para definir las operaciones basicas del crud """

  @abc.abstractmethod
  def crear(self, entidad: T) -> T: pass
  """ Operación para insertar una entidad en el almacen de datos """

  @abc.abstractmethod
  def leer_por_id(self, id: int) -> Optional[T]: pass
  """ Operación para leer una entidad por su ID """

  @abc.abstractmethod
  def leer_todos(self) -> List[T]: pass
  """ Operación para leer todas las entidades """

  @abc.abstractmethod
  def actualizar(self, entidad: T) -> T: pass
  """ Operación para actualizar una entidad """

  @abc.abstractmethod
  def eliminar(self, id: int) -> bool: pass
  """ Operación para eliminar una entidad por su ID """


class RepositorioMemoria(IRepositorio[T]):
  """Implementación del repositorio en memoria"""

  def __init__(self) -> None:
    """Inicia el contenedor de datos del repositorio"""
    self._datos: dict[int, T] = {}

  def crear(self, entidad: T) -> T:
    """Crea una nueva entidad en el repositorio comprobando que su ID no este duplicado"""
    if entidad.id in self._datos:
      raise ValueError("Entidad ya existe")
    self._datos[entidad.id] = entidad
    return entidad

  def leer_por_id(self, id: int) -> Optional[T]:
    """Retorna una entidad por su ID"""
    return self._datos.get(id)

  def leer_todos(self) -> List[T]:
    """Retorna una lista con todas las entidades"""
    return list(self._datos.values())

  def actualizar(self, entidad: T) -> T:
    """Actualiza una entidad existente en el repositorio o lanza un error si no la encuentra"""
    if entidad.id not in self._datos:
      raise ValueError("Entidad no encontrada")
    self._datos[entidad.id] = entidad
    return entidad

  def eliminar(self, id: int) -> bool:
    """Elimina una entidad por su ID y devuelve false si no la pudo eliminar"""
    if id in self._datos:
      del self._datos[id]
      return True
    return False


# Implementa la clase anterior (generica) de manera especifica para cada entidad del sistema
class RepositorioCategoria(RepositorioMemoria[Categoria]): pass
"""Repositio perteneciente a la entidad Categorias"""

class RepositorioProveedor(RepositorioMemoria[Proveedor]): pass
"""Repositio perteneciente a la entidad Proveedores"""

class RepositorioProducto(RepositorioMemoria[Producto]): pass
"""Repositio perteneciente a la entidad Productos"""

class RepositorioMoneda(RepositorioMemoria[Moneda]): pass
"""Repositio perteneciente a la entidad Monedas"""

class RepositorioTipoCotizacion(RepositorioMemoria[TipoCotizacion]): pass
"""Repositio perteneciente a la entidad TipoCotizacion"""


class RepositorioStock:
  """Utiliza el ID del producto para sus respectivas operaciones"""

  def __init__(self) -> None:
    """Inicia el contenedor de datos del repositorio"""
    self._datos: dict[int, Stock] = {}

  def crear(self, stock: Stock) -> Stock:
    """Carga un nuevo stock en el repositorio comprobando que segun su ID no cuente con un stock existente"""
    pid = stock.producto.id
    if pid in self._datos:
      raise ValueError("Stock ya existe")
    self._datos[pid] = stock
    return stock

  def leer_por_producto(self, producto_id: int) -> Optional[Stock]:
    """Retorna un stock por su ID de producto"""
    return self._datos.get(producto_id)

  def actualizar(self, stock: Stock) -> Stock:
    """Actualiza un stock existente en el repositorio o lanza un error si no lo encuentra"""
    pid = stock.producto.id
    if pid not in self._datos:
      raise ValueError("Stock no encontrado")
    self._datos[pid] = stock
    return stock

  def eliminar(self, producto_id: int) -> bool:
    """Elimina un stock por su ID de producto y devuelve false si no lo pudo eliminar"""
    if producto_id in self._datos:
      del self._datos[producto_id]
      return True
    return False


class RepositorioCotizacionDolar:
  """Utiliza el ID de la cotización para sus respectivas operaciones"""

  def __init__(self) -> None:
    """Inicia el contenedor de datos del repositorio"""
    self._datos: List[CotizacionDolar] = []

  def crear(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
    """Carga una nueva cotización en el repositorio comprobando que no cuente ya con una"""
    for c in self._datos:
      if c.tipo.id == cotizacion.tipo.id and c.fecha == cotizacion.fecha:
        raise ValueError("Cotización duplicada")

    self._datos.append(cotizacion)
    return cotizacion

  def leer_historico_por_tipo(
    self, tipo: TipoCotizacion
  ) -> List[CotizacionDolar]:
    """Retorna una lista de todas las cotizaciones de un tipo en especifico."""

    return [c for c in self._datos if c.tipo.id == tipo.id]
