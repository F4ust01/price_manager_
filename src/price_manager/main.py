
from price_manager.database.connection import ConexionDB

from price_manager.models.models import Base

from price_manager.migrations.migrations import (
  migrar_datos
)

from price_manager.ui.console import (
  run as iniciar_consola
)


def main(
  import_default_data=True
):
  """
  Punto de entrada general para la orquestación del sistema.

  Se encarga de inicializar la estructura relacional de la base de datos,
  coordinar el proceso opcional de migración de datos base y dar inicio
  a la interfaz de usuario en consola.
  """

  db = ConexionDB()

  # Se crean de forma mandatoria las tablas definidas en el ORM.
  Base.metadata.create_all(
    bind=db.get_engine()
  )

  # Se verifica e inicia la importación de los datos base del negocio.
  if import_default_data:

    migrar_datos(
      carpeta_csvs=(
        "price_manager/migrations/csv"
      ),
      carpeta_sqls=(
        "price_manager/migrations/sql"
      )
    )

  # Se transfiere el control de ejecución al bucle de la consola.
  iniciar_consola()


if __name__ == "__main__":

  main()
