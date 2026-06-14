
import datetime
import functools

from typing import Callable

from price_manager.database.connection import (
  ConexionDB
)

from price_manager.models.models import (
  AuditoriaModel
)

# Longitud máxima del campo de detalles de la tabla de auditoría.
LONGITUD_DETALLES: int = 500


def _registrar(
  accion: str,
  detalles: str
) -> None:
  """
  Inserta un registro en la tabla de auditoría.

  Utiliza una sesión propia e independiente para que la auditoría
  no interfiera con las transacciones de la operación auditada.
  """

  db = ConexionDB()

  with db.session_scope() as session:

    session.add(
      AuditoriaModel(
        accion=accion,
        fecha=(
          datetime.datetime.now()
        ),
        detalles=detalles[
          :LONGITUD_DETALLES
        ]
      )
    )


def auditar(
  accion: str
) -> Callable:
  """
  Decorador que audita la ejecución de cualquier operación.

  Registra la acción, la fecha y los detalles (función invocada,
  argumentos y estado final) tanto en caso de éxito como de error.
  """

  def decorador(
    funcion: Callable
  ) -> Callable:

    @functools.wraps(funcion)
    def envoltura(*args, **kwargs):

      # Se omite el primer argumento (self) en el detalle.
      argumentos = ", ".join(
        [
          repr(a)
          for a in args[1:]
        ]
        +
        [
          f"{k}={v!r}"
          for k, v in kwargs.items()
        ]
      )

      detalles = (
        f"{funcion.__qualname__}"
        f"({argumentos})"
      )

      try:

        resultado = funcion(
          *args,
          **kwargs
        )

        _registrar(
          accion,
          f"{detalles} | estado=OK"
        )

        return resultado

      except Exception as error:

        _registrar(
          accion,
          f"{detalles} | "
          f"estado=ERROR: {error}"
        )

        raise

    return envoltura

  return decorador
