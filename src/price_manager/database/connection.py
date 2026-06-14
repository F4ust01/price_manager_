
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class ConexionDB:
    """Clase encargada de gestionar la conexión y las sesiones de la base de datos."""

    def __init__(self):
        """Inicializa la configuración de la base de datos SQLite y su motor de conexión."""

        # Se establece el directorio de la base de datos y se crea si no existe.
        self.DATA_BASE_DIRECTORY = "/content/base_de_datos/"
        os.makedirs(self.DATA_BASE_DIRECTORY, exist_ok=True)

        # Se define el nombre del archivo de la base de datos.
        self.DATA_BASE_NAME = "base_str.db"

        # URL de conexión a SQLite.
        self.database_url = (
            f"sqlite:///{self.DATA_BASE_DIRECTORY}{self.DATA_BASE_NAME}"
        )

        # Se inicializa el motor (engine) de SQLAlchemy.
        self.engine = create_engine(
            self.database_url,
            echo=False
        )

        # Se configura la fábrica de sesiones locales.
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

    def get_engine(self):
        """Retorna el motor de conexión de SQLAlchemy configurado."""
        return self.engine

    def get_session(self):
        """
        Crea y retorna una nueva sesión local de la base de datos.

        El usuario es responsable de cerrar la sesión una vez finalizada
        su utilización.
        """
        return self.SessionLocal()
