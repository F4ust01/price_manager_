
import datetime

class Categoria:
  """Representa la división de categorias de los productos."""

  def __init__(self, id: int, nombre: str) -> None:
    """Inicia una nueva instancia de Categoria."""
    self._id = id
    self._nombre = nombre

  @property
  def id(self) -> int:
    """obtiene el ID de la categoría."""
    return self._id

  @property
  def nombre(self) -> str:
    """obtiene el nombre de la categoría."""
    return self._nombre


class Proveedor:
  """Representa a los proveedores de los productos."""

  def __init__(self, id: int, nombre: str, contacto: str) -> None:
    """Inicia una nueva instancia de proveedores."""
    self._id = id
    self._nombre = nombre
    self._contacto = contacto

  @property
  def id(self) -> int:
    """obtiene el ID del proveedor."""
    return self._id

  @property
  def nombre(self) -> str:
    """obtiene el nombre del proveedor."""
    return self._nombre

  @property
  def contacto(self) -> str:
    """obtiene el contacto del proveedor."""
    return self._contacto


class Moneda:
  """Representa el tipo de divisa utilizada para los precios de los productos."""

  def __init__(self, id: int, nombre: str) -> None:
    """Inicia una nueva instancia de moneda."""
    self._id = id
    self._nombre = nombre

  @property
  def id(self) -> int:
    """obtiene el ID de la moneda."""
    return self._id

  @property
  def nombre(self) -> str:
    """obtiene el nombre de la moneda."""
    return self._nombre

  @nombre.setter


  def nombre(self, nombre: str) -> None:
    limpio = nombre.strip().upper()
    if len(limpio) != 3:
      raise ValueError("El código de moneda debe tener exactamente 3 letras (ej: ARS)")
    self._nombre = limpio

class TipoCotizacion:
  """ Representa los tipos de cotizaciones de una moneda """

  def __init__(self, id: int, nombre: str) -> None:
    """Inicia una nueva instancia de Tipocotizacion."""
    self._id = id
    self._nombre = nombre

  @property
  def id(self) -> int:
    """obtiene el ID de la cotizacion."""
    return self._id

  @property
  def nombre(self) -> str:
    """obtiene el nombre de la cotizacion."""
    return self._nombre

class Precio:
  """ Representa el valor de los productos en una fecha dada, estos no pueden ser negativos"""
  def __init__(self, valor: float,
               moneda: Moneda,
               fecha: datetime.date) -> None:
    """ inicia una nueva instancia de precio e incluye una condicion acerca del valor"""
    if valor < 0:
      raise ValueError("El precio no puede ser negativo")

    self._valor = valor
    self._moneda = moneda
    self._fecha = fecha

  @property
  def valor(self) -> float:
    """obtiene el valor del precio"""
    return self._valor

  @valor.setter
  def valor(self, v: float) -> None:
    """Valida que el valor del precio sea positivo"""
    if v < 0:
      raise ValueError("Precio inválido")
    self._valor = v

  @property
  def moneda(self) -> Moneda:
    """obtiene la moneda del precio"""
    return self._moneda

  @property
  def fecha(self) -> datetime.date:
    """obtiene la fecha del precio en ese momento"""
    return self._fecha



class Producto:
  """Representa los productos que se venden en la tienda"""
  def __init__(self, id: int, nombre: str,
               descripcion: str,
               precio: Precio,
               categoria: Categoria,
               proveedor: Proveedor) -> None:

    self._id = id
    self._nombre = nombre
    self._descripcion = descripcion
    self._precio = precio
    self._categoria = categoria
    self._proveedor = proveedor

  @property
  def id(self) -> int:
    """obtiene el ID del producto"""
    return self._id

  @property
  def nombre(self) -> str:
    """obtiene el nombre del producto"""
    return self._nombre

  @nombre.setter
  def nombre(self, v: str) -> None:
    """Actualiza el nombre del producto"""
    self._nombre = v

  @property
  def descripcion(self) -> str:
    """obtiene la descripcion del producto"""
    return self._descripcion

  @property
  def precio(self) -> Precio:
    """obtiene el precio del producto"""
    return self._precio

  @property
  def categoria(self) -> Categoria:
    """obtiene la categoria del producto"""
    return self._categoria

  @property
  def proveedor(self) -> Proveedor:
    """obtiene el proveedor del producto"""
    return self._proveedor



class Stock:
  """Representa el stock de un producto"""
  def __init__(self, producto: Producto,
               cantidad: int,
               almacen: str) -> None:
    """ inicia una nueva instancia de stock e incluye una condicion acerca del valor"""

    if cantidad < 0:
      raise ValueError("Stock inválido")

    self._producto = producto
    self._cantidad = cantidad
    self._almacen = almacen

  @property
  def producto(self) -> Producto:
    """obtiene el producto del stock"""
    return self._producto

  @property
  def cantidad(self) -> int:
    """obtiene la cantidad del stock"""
    return self._cantidad

  @cantidad.setter
  def cantidad(self, v: int) -> None:
    """Valida que la cantidad del stock sea positiva"""
    if v < 0:
      raise ValueError("Stock inválido")
    self._cantidad = v

  @property
  def almacen(self) -> str:
    """obtiene el almacen del stock"""
    return self._almacen


class CotizacionDolar:
  """Representa la cotización del dólar en una fecha dada"""
  def __init__(self, valor: float,
               fecha: datetime.date,
               tipo: TipoCotizacion) -> None:
    """ inicia una nueva instancia de cotizacion dolar e incluye una condicion acerca del valor"""

    if valor <= 0:
      raise ValueError("Cotización inválida")

    self._valor = valor
    self._fecha = fecha
    self._tipo = tipo

  @property
  def valor(self) -> float:
    """obtiene el valor de la cotización"""
    return self._valor

  @property
  def fecha(self) -> datetime.date:
    """obtiene la fecha de la cotización"""
    return self._fecha

  @property
  def tipo(self) -> TipoCotizacion:
    """obtiene el tipo de la cotización"""
    return self._tipo
