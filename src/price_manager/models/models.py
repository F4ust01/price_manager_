
from sqlalchemy import (
  Column,
  Integer,
  String,
  Float,
  Date,
  DateTime,
  ForeignKey
)

from sqlalchemy.orm import (
  declarative_base,
  relationship
)

# Se inicializa la clase base declarativa para el mapeo objeto-relacional.
Base = declarative_base()


class CategoriaModel(Base):
  """Representa las distintas categorías conceptuales de los productos."""

  __tablename__ = "categorias"

  id = Column(Integer, primary_key=True)
  nombre = Column(String(100), nullable=False)

  productos = relationship(
    "ProductoModel",
    back_populates="categoria"
  )


class ProveedorModel(Base):
  """Almacena la información de contacto de las entidades proveedoras."""

  __tablename__ = "proveedores"

  id = Column(Integer, primary_key=True)
  nombre = Column(String(100), nullable=False)
  contacto = Column(String(150), nullable=False)

  productos = relationship(
    "ProductoModel",
    back_populates="proveedor"
  )


class MonedaModel(Base):
  """Define los tipos de divisas comerciales registradas en el sistema."""

  __tablename__ = "monedas"

  id = Column(Integer, primary_key=True)
  nombre = Column(String(3), nullable=False)

  precios = relationship(
    "PrecioModel",
    back_populates="moneda"
  )


class TipoCotizacionModel(Base):
  """Clasifica las diferentes variantes de cotización para las divisas."""

  __tablename__ = "tipos_cotizacion"

  id = Column(Integer, primary_key=True)
  nombre = Column(String(50), nullable=False)

  cotizaciones = relationship(
    "CotizacionDolarModel",
    back_populates="tipo"
  )


class PrecioModel(Base):
  """Registra el histórico de precios asignados con su respectiva divisa."""

  __tablename__ = "precios"

  id = Column(Integer, primary_key=True)
  valor = Column(Float, nullable=False)
  fecha = Column(Date, nullable=False)

  moneda_id = Column(
    Integer,
    ForeignKey("monedas.id"),
    nullable=False
  )

  moneda = relationship(
    "MonedaModel",
    back_populates="precios"
  )

  producto = relationship(
    "ProductoModel",
    back_populates="precio",
    uselist=False
  )


class ProductoModel(Base):
  """Entidad principal que consolida las características de los artículos."""

  __tablename__ = "productos"

  id = Column(Integer, primary_key=True)
  nombre = Column(String(100), nullable=False)
  descripcion = Column(String(255), nullable=False)

  precio_id = Column(
    Integer,
    ForeignKey("precios.id"),
    nullable=False
  )

  categoria_id = Column(
    Integer,
    ForeignKey("categorias.id"),
    nullable=False
  )

  proveedor_id = Column(
    Integer,
    ForeignKey("proveedores.id"),
    nullable=False
  )

  precio = relationship(
    "PrecioModel",
    back_populates="producto"
  )

  categoria = relationship(
    "CategoriaModel",
    back_populates="productos"
  )

  proveedor = relationship(
    "ProveedorModel",
    back_populates="productos"
  )

  stock = relationship(
    "StockModel",
    back_populates="producto",
    uselist=False
  )

  resultados_scraping = relationship(
    "ResultadoScrapingModel",
    back_populates="producto"
  )

class StockModel(Base):
  """Monitorea las existencias físicas de cada producto por almacén."""

  __tablename__ = "stock"

  id = Column(Integer, primary_key=True)

  producto_id = Column(
    Integer,
    ForeignKey("productos.id"),
    nullable=False
  )

  cantidad = Column(Integer, nullable=False)
  almacen = Column(String(100), nullable=False)

  producto = relationship(
    "ProductoModel",
    back_populates="stock"
  )


class CotizacionDolarModel(Base):
  """Historial de las fluctuaciones en el valor de cotización de la divisa."""

  __tablename__ = "cotizaciones"

  id = Column(Integer, primary_key=True)

  valor = Column(Float, nullable=False)
  fecha = Column(Date, nullable=False)

  tipo_id = Column(
    Integer,
    ForeignKey("tipos_cotizacion.id"),
    nullable=False
  )

  tipo = relationship(
    "TipoCotizacionModel",
    back_populates="cotizaciones"
  )


class ResultadoScrapingModel(Base):
  """Almacena cada precio de la competencia obtenido por el scraper."""

  __tablename__ = "resultados_scraping"

  id = Column(Integer, primary_key=True)

  producto_id = Column(
    Integer,
    ForeignKey("productos.id"),
    nullable=False
  )

  nombre_web = Column(String(255), nullable=False)
  precio_interno = Column(Float, nullable=False)
  precio_web = Column(Float, nullable=False)
  diferencia = Column(Float, nullable=False)
  url_img = Column(String(500), nullable=True)
  formas_pago = Column(String(1000), nullable=True)
  descripcion = Column(String(2000), nullable=True)
  url_extraccion = Column(String(500), nullable=True)
  fecha_extraccion = Column(DateTime, nullable=False)

  producto = relationship(
    "ProductoModel",
    back_populates="resultados_scraping"
  )

