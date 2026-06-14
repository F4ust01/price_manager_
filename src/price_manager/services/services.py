
import os
import requests
from datetime import date

from dotenv import load_dotenv

from price_manager.models.models import (
  CotizacionDolarModel
)


# Carga de variables de entorno globales.
load_dotenv()

API_URL = os.getenv(
  "API_URL"
)


class ServicioCategoria:
  """Orquesta la lógica de negocio para la gestión de categorías."""
  def __init__(self, repo):
    """Inicializa el servicio vinculando su repositorio correspondiente."""
    self.repo = repo

  def crear(self, categoria):
    """Registra una nueva categoría a través del repositorio."""
    return self.repo.crear(
      categoria
    )

  def obtener(self, id: int):
    """Recupera una categoría específica según su identificador único."""
    return self.repo.leer_por_id(
      id
    )

  def listar_todos(self):
    """Retorna todas las categorías registradas en la base de datos."""
    return self.repo.leer_todos()

  def actualizar(self, categoria):
    """Actualiza los datos de una categoría previamente registrada."""
    return self.repo.actualizar(
      categoria
    )

  def eliminar(self, id: int):
    """Remueve una categoría del sistema mediante su identificador."""
    return self.repo.eliminar(
      id
    )


class ServicioProveedor:
  """Orquesta la lógica de negocio para la gestión de proveedores."""

  def __init__(self, repo):
    """Inicializa el servicio vinculando su repositorio correspondiente."""
    self.repo = repo

  def crear(self, proveedor):
    """Registra un nuevo proveedor a través del repositorio."""
    return self.repo.crear(
      proveedor
    )

  def obtener(self, id: int):
    """Recupera un proveedor específico según su identificador único."""
    return self.repo.leer_por_id(
      id
    )

  def listar_todos(self):
    """Retorna el listado completod e proveedores existentes."""
    return self.repo.leer_todos()

  def actualizar(self, proveedor):
    """Actualiza los datos de un proveedor previamente registrado."""
    return self.repo.actualizar(
      proveedor
    )

  def eliminar(self, id: int):
    """Remueve un proveedor del sistema mediante su identificador."""
    return self.repo.eliminar(
      id
    )



class ServicioProducto:
  """Administra las reglas de negocio y validaciones para los productos."""
  def __init__(
    self,
    repo,
    srv_categoria,
    srv_proveedor
  ):
    """Inicializa el servicio vinculando sus repositorios y servicios correspondientes."""
    self.repo = repo

    self.srv_categoria = (
      srv_categoria
    )

    self.srv_proveedor = (
      srv_proveedor
    )

  def crear(self, producto):
    """Valida las relaciones jerárquicas y registra un nuevo producto."""
    categoria = (
      self.srv_categoria.obtener(
        producto.categoria_id
      )
    )

    if not categoria:

      raise ValueError(
        "La categoria no existe"
      )

    proveedor = (
      self.srv_proveedor.obtener(
        producto.proveedor_id
      )
    )

    if not proveedor:

      raise ValueError(
        "El proveedor no existe"
      )

    return self.repo.crear(
      producto
    )

  def obtener(self, id: int):
    """Recupera un producto específico según su identificador único."""
    return self.repo.leer_por_id(
      id
    )

  def listar_todos(self):
    """Retorna el listado completod de productos existentes."""
    return self.repo.leer_todos()

  def actualizar(self, producto):
    """Actualiza los datos de un producto previamente registrado."""
    return self.repo.actualizar(
      producto
    )

  def eliminar(self, id: int):
    """Remueve un producto del sistema mediante su identificador."""
    return self.repo.eliminar(
      id
    )

class ServicioMoneda:
  """Orquesta la lógica de negocio para la gestión de monedas."""
  def __init__(self, repo):
    """Inicializa el servicio vinculando su repositorio correspondiente."""
    self.repo = repo

  def crear(self, moneda):
    """Registra una nueva moneda en el sistema."""
    return self.repo.crear(
      moneda
    )

  def obtener(self, id: int):
    """Recupera una moneda específica según su identificador único."""
    return self.repo.leer_por_id(
      id
    )

  def listar_todos(self):
    """Retorna el listado completod de monedas existentes."""
    return self.repo.leer_todos()

  def actualizar(self, moneda):
    """Actualiza los datos de una moneda previamente registrada."""
    return self.repo.actualizar(
      moneda
    )

  def eliminar(self, id: int):
    """Remueve una moneda del sistema mediante su identificador."""
    return self.repo.eliminar(
      id
    )


class ServicioStock:
  """Valida y administra los niveles de inventario de los productos."""

  def __init__(
    self,
    repo,
    srv_producto
  ):
    """Inicializa el servicio vinculando el repositorio y el servicio de productos."""

    self.repo = repo

    self.srv_producto = (
      srv_producto
    )

  def crear(self, stock):
    """Valida la existencia del producto y registra su stock inicial."""
    producto = (
      self.srv_producto.obtener(
        stock.producto_id
      )
    )

    if not producto:

      raise ValueError(
        "El producto no existe"
      )

    return self.repo.crear(
      stock
    )

  def obtener_por_producto(
    self,
    producto_id: int
  ):
    """Recupera el registro de inventario asociado a un producto."""

    return self.repo.leer_por_producto(
      producto_id
    )

  def listar_todos(self):
    """Retorna el listado completo de productos existentes."""
    return self.repo.leer_todos()

  def actualizar(self, stock):
    """Actualiza los datos de un stock previamente registrado."""
    return self.repo.actualizar(
      stock
    )

  def eliminar(
    self,
    producto_id: int
  ):
    """Remueve el control de stock asociado a un identificador de producto."""

    return self.repo.eliminar(
      producto_id
    )



class ServicioTipoCotizacion:
  """Gestiona los catálogos y clasificaciones de tipos de cotizaciones."""


  def __init__(self, repo):
    """Inicializa el servicio vinculando su repositorio correspondiente."""
    self.repo = repo

  def crear(self, tipo):
    """Registra un nuevo tipo de cotización."""
    return self.repo.crear(
      tipo
    )

  def obtener(self, id: int):
    """Recupera un tipo de cotización específico según su identificador único."""
    return self.repo.leer_por_id(
      id
    )

  def listar_todos(self):
    """Retorna el listado completo de tipos de cotización existentes."""
    return self.repo.leer_todos()


class ServicioCotizacionDolar:
  """
  Servicio especializado para la gestión y actualización de cotizaciones.

  Centraliza las interacciones transaccionales del historial del dólar,
  incluyendo la consulta sincrónica a plataformas de datos externas.
  """

  def __init__(
    self,
    repo,
    tipo_repo
  ):
    """Inicializa el servicio vinculando ñps repositorios requeridos."""

    self.repo = repo

    self.tipo_repo = (
      tipo_repo
    )

  def registrar_cotizacion(
    self,
    cotizacion
  ):
    """Registra una nueva cotización en la base de datos."""

    return self.repo.crear(
      cotizacion
    )

  def obtener_historico(
    self,
    tipo_id: int
  ):
    """Retorna la serie cronológica de valores para un tipo de cotización."""

    tipo = (
      self.tipo_repo.leer_por_id(
        tipo_id
      )
    )

    if not tipo:

      raise ValueError(
        "Tipo no existe"
      )

    return (
      self.repo.leer_historico_por_tipo(
        tipo_id
      )
    )

  def obtener_cotizaciones(self):
    """
    Sincroniza y guarda en la base de datos las cotizaciones desde la API.

    Realiza una petición HTTP hacia el endpoint configurado, empareja las
    entidades devueltas según su equivalencia semántica y persiste los
    nuevos valores de venta registrados para la fecha actual.
    """

    if not API_URL:

      raise ValueError(
        "La API_URL no está definida en .env"
      )

    response = requests.get(
      API_URL,
      timeout=10
    )

    response.raise_for_status()

    datos = response.json()

    tipos = (
      self.tipo_repo.leer_todos()
    )

    for d in datos:

      venta = d.get(
        "venta"
      )

      if venta is None:

        continue

      nombre_tipo = d.get(
        "nombre"
      )

      tipo_existente = None

      for t in tipos:

        if (
          t.nombre.lower()
          ==
          nombre_tipo.lower()
        ):

          tipo_existente = t
          break

      if not tipo_existente:

        continue

      cotizacion = (
        CotizacionDolarModel(
          valor=float(venta),
          fecha=date.today(),
          tipo_id=tipo_existente.id
        )
      )

      self.repo.crear(
        cotizacion
      )

    return True
