
import os

from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class ConexionDB:
  """
  Clase encargada de gestionar
  la conexión y las sesiones
  de la base de datos.
  """

  def __init__(self):
    """
    Inicializa la configuración
    de la base de datos SQLite.
    """

    # Directorio de la base de datos
    self.DATA_BASE_DIRECTORY = (
      "/content/base_de_datos/"
    )

    os.makedirs(
      self.DATA_BASE_DIRECTORY,
      exist_ok=True
    )

    # Nombre del archivo SQLite
    self.DATA_BASE_NAME = (
      "base_str.db"
    )

    # URL de conexión
    self.database_url = (
      f"sqlite:///"
      f"{self.DATA_BASE_DIRECTORY}"
      f"{self.DATA_BASE_NAME}"
    )

    # Motor SQLAlchemy
    self.engine = create_engine(
      self.database_url,
      echo=False
    )

    # Fábrica de sesiones
    self.SessionLocal = (
      sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=self.engine
      )
    )

  def get_engine(self):
    """
    Retorna el engine
    configurado.
    """

    return self.engine

  def get_session(self):
    """
    Retorna una nueva sesión
    de base de datos.
    """

    return self.SessionLocal()

  @contextmanager
  def session_scope(self):
    """
    Context manager para
    manejar transacciones
    automáticamente.
    """

    session = self.SessionLocal()

    try:

      yield session

      session.commit()

    except Exception:

      session.rollback()

      raise

    finally:

      session.close()
