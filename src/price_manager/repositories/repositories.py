
from sqlalchemy.orm import Session

from price_manager.models.models import (
  CategoriaModel,
  ProveedorModel,
  ProductoModel,
  PrecioModel,
  MonedaModel,
  StockModel,
  TipoCotizacionModel,
  CotizacionDolarModel,
  ResultadoScrapingModel,
  AuditoriaModel
)

from price_manager.services.auditoria import (
  auditar
)


class RepositorioCategoria:
  """Gestiona las operaciones de persistencia para el modelo CategoriaModel."""

  def __init__(self, session: Session):
    """Inicializa el repositorio con una sesión activa de SQLAlchemy."""
    self.session = session

  @auditar("crear_categoria")
  def crear(self, categoria):
    """Registra una nueva categoría en la base de datos."""
    self.session.add(categoria)
    self.session.commit()
    return categoria

  @auditar("leer_categoria")
  def leer_por_id(self, id: int):
    """Busca y retorna una categoría según su identificador único."""
    return self.session.query(
      CategoriaModel
    ).filter_by(id=id).first()

  @auditar("listar_categorias")
  def leer_todos(self):
    """Retorna una lista con todas las categorías registradas."""
    return self.session.query(
      CategoriaModel
    ).all()

  @auditar("actualizar_categoria")
  def actualizar(self, categoria):
    """Confirma los cambios realizados sobre una categoría existente."""
    self.session.commit()
    return categoria

  @auditar("eliminar_categoria")
  def eliminar(self, id: int):
    """Elimina una categoría del sistema por su identificador único."""
    categoria = self.session.query(
      CategoriaModel
    ).filter_by(id=id).first()

    if categoria:
      self.session.delete(categoria)
      self.session.commit()
      return True

    return False


class RepositorioProveedor:
  """Gestiona las operaciones de persistencia para el modelo ProveedorModel."""

  def __init__(self, session: Session):
    """Inicializa el repositorio con una sesión activa de SQLAlchemy."""
    self.session = session

  @auditar("crear_proveedor")
  def crear(self, proveedor):
    """Registra un nuevo proveedor en la base de datos."""
    self.session.add(proveedor)
    self.session.commit()
    return proveedor

  @auditar("leer_proveedor")
  def leer_por_id(self, id: int):
    """Busca y retorna un proveedor según su identificador único."""
    return self.session.query(
      ProveedorModel
    ).filter_by(id=id).first()

  @auditar("listar_proveedores")
  def leer_todos(self):
    """Retorna una lista con todos los proveedores registrados."""
    return self.session.query(
      ProveedorModel
    ).all()

  @auditar("actualizar_proveedor")
  def actualizar(self, proveedor):
    """Confirma los cambios realizados sobre un proveedor existente."""
    self.session.commit()
    return proveedor

  @auditar("eliminar_proveedor")
  def eliminar(self, id: int):
    """Elimina un proveedor del sistema por su identificador único."""
    proveedor = self.session.query(
      ProveedorModel
    ).filter_by(id=id).first()

    if proveedor:
      self.session.delete(proveedor)
      self.session.commit()
      return True

    return False


class RepositorioProducto:
  """Gestiona las operaciones de persistencia para el modelo ProductoModel."""

  def __init__(self, session: Session):
    """Inicializa el repositorio con una sesión activa de SQLAlchemy."""
    self.session = session

  @auditar("crear_producto")
  def crear(self, producto):
    """Registra un nuevo producto en la base de datos."""
    self.session.add(producto)
    self.session.commit()
    return producto

  @auditar("leer_producto")
  def leer_por_id(self, id: int):
    """Busca y retorna un producto según su identificador único."""
    return self.session.query(
      ProductoModel
    ).filter_by(id=id).first()

  @auditar("listar_productos")
  def leer_todos(self):
    """Retorna una lista con todos los productos registrados."""
    return self.session.query(
      ProductoModel
    ).all()

  @auditar("actualizar_producto")
  def actualizar(self, producto):
    """Confirma los cambios realizados sobre un producto existente."""
    self.session.commit()
    return producto

  @auditar("eliminar_producto")
  def eliminar(self, id: int):
    """Elimina un producto del sistema por su identificador único."""
    producto = self.session.query(
      ProductoModel
    ).filter_by(id=id).first()

    if producto:
      self.session.delete(producto)
      self.session.commit()
      return True

    return False


class RepositorioMoneda:
  """Gestiona las operaciones de persistencia para el modelo MonedaModel."""

  def __init__(self, session: Session):
    """Inicializa el repositorio con una sesión activa de SQLAlchemy."""
    self.session = session

  @auditar("crear_moneda")
  def crear(self, moneda):
    """Registra una nueva divisa en la base de datos."""
    self.session.add(moneda)
    self.session.commit()
    return moneda

  @auditar("leer_moneda")
  def leer_por_id(self, id: int):
    """Busca y retorna una divisa según su identificador único."""
    return self.session.query(
      MonedaModel
    ).filter_by(id=id).first()

  @auditar("listar_monedas")
  def leer_todos(self):
    """Retorna una lista con todas las divisas registradas."""
    return self.session.query(
      MonedaModel
    ).all()

  @auditar("actualizar_moneda")
  def actualizar(self, moneda):
    """Confirma los cambios realizados sobre una divisa existente."""
    self.session.commit()
    return moneda

  @auditar("eliminar_moneda")
  def eliminar(self, id: int):
    """Elimina una divisa del sistema por su identificador único."""
    moneda = self.session.query(
      MonedaModel
    ).filter_by(id=id).first()

    if moneda:
      self.session.delete(moneda)
      self.session.commit()
      return True

    return False


class RepositorioStock:
  """Gestiona las operaciones de persistencia para el modelo StockModel."""

  def __init__(self, session: Session):
    """Inicializa el repositorio con una sesión activa de SQLAlchemy."""
    self.session = session

  @auditar("crear_stock")
  def crear(self, stock):
    """Registra un nuevo control de stock en la base de datos."""
    self.session.add(stock)
    self.session.commit()
    return stock

  @auditar("leer_stock")
  def leer_por_producto(self, producto_id: int):
    """Busca y retorna las existencias asociadas a un producto específico."""
    return self.session.query(
      StockModel
    ).filter_by(producto_id=producto_id).first()

  @auditar("listar_stock")
  def leer_todos(self):
    """Retorna una lista con todos los registros de stock existentes."""
    return self.session.query(
      StockModel
    ).all()

  @auditar("actualizar_stock")
  def actualizar(self, stock):
    """Confirma los cambios realizados sobre el stock de un producto."""
    self.session.commit()
    return stock

  @auditar("eliminar_stock")
  def eliminar(self, producto_id: int):
    """Elimina el registro de stock asociado a un producto."""
    stock = self.session.query(
      StockModel
    ).filter_by(producto_id=producto_id).first()

    if stock:
      self.session.delete(stock)
      self.session.commit()
      return True

    return False


class RepositorioTipoCotizacion:
  """Gestiona las operaciones de consulta para el modelo TipoCotizacionModel."""

  def __init__(self, session: Session):
    """Inicializa el repositorio con una sesión activa de SQLAlchemy."""
    self.session = session

  @auditar("crear_tipo_cotizacion")
  def crear(self, tipo):
    """Registra un nuevo tipo de cotización en la base de datos."""
    self.session.add(tipo)
    self.session.commit()
    return tipo

  @auditar("leer_tipo_cotizacion")
  def leer_por_id(self, id: int):
    """Busca y retorna un tipo de cotización según su identificador único."""
    return self.session.query(
      TipoCotizacionModel
    ).filter_by(id=id).first()

  @auditar("listar_tipos_cotizacion")
  def leer_todos(self):
    """Retorna una lista con todos los tipos de cotización registrados."""
    return self.session.query(
      TipoCotizacionModel
    ).all()


class RepositorioCotizacionDolar:
  """Gestiona la persistencia para el modelo CotizacionDolarModel."""

  def __init__(self, session: Session):
    """Inicializa el repositorio con una sesión activa de SQLAlchemy."""
    self.session = session

  @auditar("crear_cotizacion")
  def crear(self, cotizacion):
    """Registra una nueva cotización en la base de datos."""
    self.session.add(cotizacion)
    self.session.commit()
    return cotizacion

  @auditar("listar_cotizaciones")
  def leer_todos(self):
    """Retorna una lista con todas las cotizaciones registradas."""
    return self.session.query(
      CotizacionDolarModel
    ).all()

  @auditar("leer_historico_cotizacion")
  def leer_historico_por_tipo(self, tipo_id: int):
    """Busca y retorna una lista de cotizaciones de un tipo específico."""
    return self.session.query(
      CotizacionDolarModel
    ).filter_by(tipo_id=tipo_id).all()


class RepositorioResultadoScraping:
  """Gestiona la lectura de los resultados generados por el scraper."""

  def __init__(self, session: Session):
    """Inicializa el repositorio con una sesión activa de SQLAlchemy."""
    self.session = session

  @auditar("listar_resultados_scraping")
  def leer_todos(self):
    """Retorna todos los resultados del scraping ordenados por fecha."""
    return self.session.query(
      ResultadoScrapingModel
    ).order_by(
      ResultadoScrapingModel
      .fecha_extraccion
      .desc()
    ).all()


class RepositorioAuditoria:
  """
  Gestiona la lectura del historial de auditoría.

  Sus métodos no se auditan a sí mismos para evitar que la consulta
  del historial genere registros adicionales que ensucien la traza.
  """

  def __init__(self, session: Session):
    """Inicializa el repositorio con una sesión activa de SQLAlchemy."""
    self.session = session

  def leer_ultimos(self, cantidad: int = 20):
    """Retorna los últimos registros de auditoría, el más nuevo primero."""
    return self.session.query(
      AuditoriaModel
    ).order_by(
      AuditoriaModel.fecha.desc(),
      AuditoriaModel.id.desc()
    ).limit(cantidad).all()
