
import os
import csv
import datetime

import requests

from dotenv import load_dotenv

from sqlalchemy.orm import Session

from price_manager.database.connection import ConexionDB

from price_manager.models.models import (
  CategoriaModel,
  ProveedorModel,
  MonedaModel,
  TipoCotizacionModel,
  PrecioModel,
  ProductoModel,
  StockModel,
  CotizacionDolarModel
)


# ======================
# VARIABLES DE ENTORNO
# ======================

# Carga de variables de entorno del sistema.
load_dotenv()

API_URL = os.getenv(
  "API_URL"
)


# Funciones auxiliares del proceso de migración.

def escribir_sql(
  ruta_archivo: str,
  sentencia: str
) -> None:
    """
    Guarda una sentencia SQL dentro del archivo de respaldo indicado.

    Abre el archivo en modo de anexado con codificación UTF-8 y añade
    un salto de línea al final de la instrucción.
    """

    with open(
      ruta_archivo,
      "a",
      encoding="utf-8"
    ) as archivo:

      archivo.write(
        sentencia + "\n"
      )

# Lógica principal de migración de datos.

def migrar_datos(
  carpeta_csvs: str,
  carpeta_sqls: str
) -> None:
    """
    Realiza la migración de datos desde archivos CSV hacia la base de datos.

    Lee el origen de datos en formato CSV, inyecta la información en las
    tablas administradas por el ORM SQLite y paralelamente genera archivos de
    respaldo con scripts de inserción puramente SQL.
    """

    os.makedirs(
      carpeta_sqls,
      exist_ok=True
    )

    db = ConexionDB()

    session: Session = (
      db.get_session()
    )

    try:

      # Migración de la entidad Monedas.

      ruta_sql = (
        f"{carpeta_sqls}/monedas.sql"
      )

      with open(
        f"{carpeta_csvs}/monedas.csv",
        encoding="utf-8"
      ) as archivo:

        for registro in csv.DictReader(
          archivo
        ):

          moneda = MonedaModel(
            id=int(registro["id"]),
            nombre=registro["nombre"]
          )

          session.add(
            moneda
          )

          sql = (
            "INSERT INTO monedas "
            "(id, nombre) "
            f"VALUES ({registro['id']}, "
            f"'{registro['nombre']}');"
          )

          escribir_sql(
            ruta_sql,
            sql
          )

      # Migración de la entidad Tipos de Cotización.

      ruta_sql = (
        f"{carpeta_sqls}/tipos_cotizacion.sql"
      )

      with open(
        f"{carpeta_csvs}/tipos_cotizacion.csv",
        encoding="utf-8"
      ) as archivo:

        for registro in csv.DictReader(
          archivo
        ):

          tipo = TipoCotizacionModel(
            id=int(registro["id"]),
            nombre=registro["nombre"]
          )

          session.add(
            tipo
          )

          sql = (
            "INSERT INTO tipos_cotizacion "
            "(id, nombre) "
            f"VALUES ({registro['id']}, "
            f"'{registro['nombre']}');"
          )

          escribir_sql(
            ruta_sql,
            sql
          )

      # Migración de la entidad Categorías.

      ruta_sql = (
        f"{carpeta_sqls}/categorias.sql"
      )

      with open(
        f"{carpeta_csvs}/categorias.csv",
        encoding="utf-8"
      ) as archivo:

        for registro in csv.DictReader(
          archivo
        ):

          categoria = CategoriaModel(
            id=int(registro["id"]),
            nombre=registro["nombre"]
          )

          session.add(
            categoria
          )

          sql = (
            "INSERT INTO categorias "
            "(id, nombre) "
            f"VALUES ({registro['id']}, "
            f"'{registro['nombre']}');"
          )

          escribir_sql(
            ruta_sql,
            sql
          )

      # Migración de la entidad Proveedores.

      ruta_sql = (
        f"{carpeta_sqls}/proveedores.sql"
      )

      with open(
        f"{carpeta_csvs}/proveedores.csv",
        encoding="utf-8"
      ) as archivo:

        for registro in csv.DictReader(
          archivo
        ):

          proveedor = ProveedorModel(
            id=int(registro["id"]),
            nombre=registro["nombre"],
            contacto=registro["contacto"]
          )

          session.add(
            proveedor
          )

          sql = (
            "INSERT INTO proveedores "
            "(id, nombre, contacto) "
            f"VALUES ({registro['id']}, "
            f"'{registro['nombre']}', "
            f"'{registro['contacto']}');"
          )

          escribir_sql(
            ruta_sql,
            sql
          )

      # Migración simultánea de las entidades Precios y Productos.

      ruta_sql_prod = (
        f"{carpeta_sqls}/productos.sql"
      )

      ruta_sql_prec = (
        f"{carpeta_sqls}/precios.sql"
      )

      with open(
        f"{carpeta_csvs}/productos.csv",
        encoding="utf-8"
      ) as archivo:

        for registro in csv.DictReader(
          archivo
        ):

          precio = PrecioModel(
            id=int(registro["id"]),
            valor=float(registro["valor"]),
            fecha=datetime.date.today(),
            moneda_id=int(
              registro["moneda_id"]
            )
          )

          session.add(
            precio
          )

          sql_precio = (
            "INSERT INTO precios "
            "(id, valor, fecha, moneda_id) "
            f"VALUES ({registro['id']}, "
            f"{registro['valor']}, "
            f"'{datetime.date.today()}', "
            f"{registro['moneda_id']});"
          )

          escribir_sql(
            ruta_sql_prec,
            sql_precio
          )

          producto = ProductoModel(
            id=int(registro["id"]),
            nombre=registro["nombre"],
            descripcion=registro["descripcion"],
            precio_id=int(registro["id"]),
            categoria_id=int(
              registro["categoria_id"]
            ),
            proveedor_id=int(
              registro["proveedor_id"]
            )
          )

          session.add(
            producto
          )

          sql_producto = (
            "INSERT INTO productos "
            "(id, nombre, descripcion, "
            "precio_id, categoria_id, "
            "proveedor_id) "
            f"VALUES ({registro['id']}, "
            f"'{registro['nombre']}', "
            f"'{registro['descripcion']}', "
            f"{registro['id']}, "
            f"{registro['categoria_id']}, "
            f"{registro['proveedor_id']});"
          )

          escribir_sql(
            ruta_sql_prod,
            sql_producto
          )

      # Migración de la entidad Stock.

      ruta_sql = (
        f"{carpeta_sqls}/stock.sql"
      )

      with open(
        f"{carpeta_csvs}/stock.csv",
        encoding="utf-8"
      ) as archivo:

        for registro in csv.DictReader(
          archivo
        ):

          stock = StockModel(
            producto_id=int(
              registro["producto_id"]
            ),
            cantidad=int(
              registro["cantidad"]
            ),
            almacen=registro["almacen"]
          )

          session.add(
            stock
          )

          sql = (
            "INSERT INTO stock "
            "(producto_id, cantidad, almacen) "
            f"VALUES ({registro['producto_id']}, "
            f"{registro['cantidad']}, "
            f"'{registro['almacen']}');"
          )

          escribir_sql(
            ruta_sql,
            sql
          )

      # Migración de datos históricos de Cotizaciones mediante archivo local.

      ruta_sql = (
        f"{carpeta_sqls}/cotizaciones.sql"
      )

      with open(
        f"{carpeta_csvs}/cotizaciones.csv",
        encoding="utf-8"
      ) as archivo:

        for registro in csv.DictReader(
          archivo
        ):

          cotizacion = (
            CotizacionDolarModel(
              valor=float(
                registro["valor"]
              ),
              fecha=datetime.datetime.strptime(
                registro["fecha"],
                "%Y-%m-%d"
              ).date(),
              tipo_id=int(
                registro["tipo_id"]
              )
            )
          )

          session.add(
            cotizacion
          )

          sql = (
            "INSERT INTO cotizaciones "
            "(valor, fecha, tipo_id) "
            f"VALUES ({registro['valor']}, "
            f"'{registro['fecha']}', "
            f"{registro['tipo_id']});"
          )

          escribir_sql(
            ruta_sql,
            sql
          )

      # Inyección complementaria de Cotizaciones en tiempo real desde API externa.

      if API_URL:

        print(
          "Inyectando cotizaciones "
          "actuales desde DolarAPI..."
        )

        response = requests.get(
          API_URL,
          timeout=10
        )

        if response.status_code == 200:

          datos = response.json()

          tipos = (
            session.query(
              TipoCotizacionModel
            ).all()
          )

          for dato in datos:

            nombre_tipo = (
              dato["nombre"]
            )

            tipo_existente = next(
              (
                t for t in tipos
                if t.nombre.lower()
                ==
                nombre_tipo.lower()
              ),
              None
            )

            if tipo_existente:

              cotizacion_api = (
                CotizacionDolarModel(
                  valor=float(
                    dato["venta"]
                  ),
                  fecha=datetime.date.today(),
                  tipo_id=tipo_existente.id
                )
              )

              session.add(
                cotizacion_api
              )

              sql_api = (
                "INSERT INTO cotizaciones "
                "(valor, fecha, tipo_id) "
                f"VALUES ({cotizacion_api.valor}, "
                f"'{cotizacion_api.fecha}', "
                f"{cotizacion_api.tipo_id});"
              )

              escribir_sql(
                ruta_sql,
                sql_api
              )

      # Confirmación de todas las operaciones transaccionales pendientes.
      session.commit()

      print(
        "Migración completada "
        "exitosamente."
      )

    except Exception as error:
      # Se revierte la transacción ante cualquier falla interna detectada.
      session.rollback()

      print(
        f"Error en migración: "
        f"{error}"
      )

    finally:
      # Cierre definitivo de los recursos de sesión.
      session.close()


# =========================================
# CARGA DE DATOS DESDE LOS SCRIPTS SQL
# =========================================

def cargar_datos_desde_sql(
  carpeta_sqls: str
) -> None:
  """
  Carga la base de datos ejecutando los scripts .sql de respaldo.

  Recorre los archivos en un orden seguro respecto de las claves
  foráneas y ejecuta cada sentencia. Las inserciones se convierten a
  "INSERT OR IGNORE" para que el proceso sea idempotente y pueda
  ejecutarse varias veces sin duplicar claves primarias.
  """

  # Orden de ejecución que respeta las dependencias entre tablas.
  orden_archivos: list = [
    "monedas.sql",
    "tipos_cotizacion.sql",
    "categorias.sql",
    "proveedores.sql",
    "precios.sql",
    "productos.sql",
    "stock.sql",
    "cotizaciones.sql"
  ]

  db = ConexionDB()

  insertadas: int = 0
  omitidas: int = 0

  with db.get_engine().connect() as conexion:

    for nombre_archivo in orden_archivos:

      ruta = os.path.join(
        carpeta_sqls,
        nombre_archivo
      )

      if not os.path.exists(ruta):

        print(
          f"Aviso: no existe {ruta}, "
          "se omite."
        )

        continue

      with open(
        ruta,
        encoding="utf-8"
      ) as archivo:

        for linea in archivo:

          sentencia = linea.strip()

          if not sentencia:

            continue

          # Se vuelve idempotente la sentencia para SQLite.
          sentencia = sentencia.replace(
            "INSERT INTO",
            "INSERT OR IGNORE INTO"
          )

          resultado = (
            conexion.exec_driver_sql(
              sentencia
            )
          )

          if resultado.rowcount > 0:

            insertadas += 1

          else:

            omitidas += 1

    # Confirmación de la transacción completa.
    conexion.commit()

  print(
    f"Carga desde SQL finalizada. "
    f"Insertadas: {insertadas} | "
    f"Omitidas (ya existentes): {omitidas}"
  )
