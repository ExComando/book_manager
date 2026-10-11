"""Migración de los datos del Sprint 1 (archivos CSV) a la base de datos.

El proceso tiene dos pasos: generar un archivo .sql por tabla a partir de los CSV y
ejecutar esos archivos dentro de una única transacción. Las sentencias usan
"ON CONFLICT DO NOTHING", así que la migración se puede repetir sin duplicar datos.
"""
import csv
import datetime
import os
from decimal import Decimal, InvalidOperation
from typing import List, Tuple

from book_manager.database.connection import ConexionDB
from book_manager.models.models import crear_tablas

_BASE = os.path.dirname(os.path.abspath(__file__))
CARPETA_CSV_DEFECTO = os.path.join(_BASE, "csv")
CARPETA_SQL_DEFECTO = os.path.join(_BASE, "sql")

# Tabla y tipo de cada columna. El orden respeta las dependencias entre tablas:
# primero las que son referenciadas por claves foráneas. El CSV de cada tabla se
# llama igual que la tabla.
TABLAS: List[Tuple[str, List[Tuple[str, str]]]] = [
    ("generos", [("id", "entero"), ("nombre", "texto")]),
    ("editoriales", [("id", "entero"), ("nombre", "texto"), ("pais", "texto")]),
    ("monedas", [("id", "entero"), ("codigo", "texto"), ("nombre", "texto"),
                 ("simbolo", "texto")]),
    ("tipos_cotizacion", [("id", "entero"), ("nombre", "texto")]),
    ("libros", [("id", "entero"), ("isbn", "texto"), ("titulo", "texto"),
                ("autor", "texto"), ("editorial_id", "entero"), ("genero_id", "entero")]),
    ("precios", [("id", "entero"), ("libro_id", "entero"), ("moneda_id", "entero"),
                 ("valor", "decimal")]),
    ("stock", [("libro_id", "entero"), ("cantidad", "entero")]),
    ("cotizaciones", [("tipo_id", "entero"), ("fecha", "fecha"),
                      ("valor_compra", "decimal"), ("valor_venta", "decimal")]),
]


def _literal(valor: str, tipo: str) -> str:
    """Convierte un valor del CSV en un literal SQL, validando su tipo.

    Los números y fechas se validan y se reescriben, y en los textos se duplican
    las comillas simples, de modo que ningún dato puede alterar la sentencia.
    """
    try:
        if tipo == "entero":
            return str(int(valor))
        if tipo == "decimal":
            return str(Decimal(valor))
        if tipo == "fecha":
            return "'" + datetime.date.fromisoformat(valor).isoformat() + "'"
    except (ValueError, InvalidOperation) as error:
        raise ValueError(f"Valor inválido para un campo {tipo}: '{valor}'.") from error
    if "\n" in valor or "\r" in valor:
        raise ValueError(f"El texto '{valor[:30]}...' tiene saltos de línea.")
    return "'" + valor.replace("'", "''") + "'"


def _generar_archivo(tabla: str, columnas: List[Tuple[str, str]],
                     ruta_csv: str, ruta_sql: str) -> int:
    """Escribe el .sql de una tabla a partir de su CSV. Devuelve la cantidad de filas."""
    if not os.path.exists(ruta_csv):
        raise FileNotFoundError(f"No se encontró el archivo {ruta_csv}.")
    nombres = ", ".join(nombre for nombre, _ in columnas)
    sentencias = []
    with open(ruta_csv, newline="", encoding="utf-8") as archivo:
        for fila in csv.DictReader(archivo):
            valores = ", ".join(_literal(fila[nombre], tipo) for nombre, tipo in columnas)
            sentencias.append(
                f"INSERT INTO {tabla} ({nombres}) VALUES ({valores}) ON CONFLICT DO NOTHING;")
    with open(ruta_sql, "w", encoding="utf-8", newline="\n") as archivo:
        archivo.write(f"-- Datos de la tabla {tabla}, generados desde {tabla}.csv\n")
        archivo.write("\n".join(sentencias) + ("\n" if sentencias else ""))
    return len(sentencias)


def generar_sqls(carpeta_csvs: str, carpeta_sqls: str) -> List[str]:
    """Genera un archivo .sql por tabla (numerados según el orden de ejecución).

    Args:
        carpeta_csvs: carpeta con los CSV de origen.
        carpeta_sqls: carpeta donde se escriben los .sql.

    Returns:
        Las rutas de los archivos generados, en orden de ejecución.
    """
    os.makedirs(carpeta_sqls, exist_ok=True)
    rutas = []
    for numero, (tabla, columnas) in enumerate(TABLAS, start=1):
        ruta_sql = os.path.join(carpeta_sqls, f"{numero:02d}_{tabla}.sql")
        _generar_archivo(tabla, columnas, os.path.join(carpeta_csvs, f"{tabla}.csv"), ruta_sql)
        rutas.append(ruta_sql)
    return rutas


def _sentencias(texto: str) -> List[str]:
    """Separa las sentencias de un .sql (una por línea) sin comentarios ni líneas vacías."""
    return [linea.strip() for linea in texto.splitlines()
            if linea.strip() and not linea.lstrip().startswith("--")]


def ejecutar_sqls(carpeta_sqls: str, conexion: ConexionDB) -> int:
    """Ejecuta los .sql de la carpeta, en orden, dentro de una única transacción.

    Si alguna sentencia falla se revierte todo y no queda nada a medias.

    Returns:
        La cantidad de sentencias ejecutadas.
    """
    archivos = sorted(nombre for nombre in os.listdir(carpeta_sqls) if nombre.endswith(".sql"))
    total = 0
    with conexion.transaccion() as sesion:
        conexion_sql = sesion.connection()
        for nombre in archivos:
            with open(os.path.join(carpeta_sqls, nombre), encoding="utf-8") as archivo:
                sentencias = _sentencias(archivo.read())
            if not sentencias:
                continue
            opciones = {"no_parameters": True}  # evita que % o : en los datos se interpreten
            if conexion.engine.dialect.name == "postgresql":
                # Un solo envío por tabla: reduce los viajes de red a la base remota.
                conexion_sql.exec_driver_sql("\n".join(sentencias), execution_options=opciones)
            else:
                for sentencia in sentencias:
                    conexion_sql.exec_driver_sql(sentencia, execution_options=opciones)
            total += len(sentencias)
    return total


def migrar_con_conexion(carpeta_csvs: str, carpeta_sqls: str, conexion: ConexionDB) -> None:
    """Migra los datos usando la conexión indicada.

    Crea las tablas que falten, genera los archivos sql a partir de los csv y los
    ejecuta en una única transacción. Se puede repetir sin duplicar datos.

    Args:
        carpeta_csvs (str): Carpeta donde se encuentran los archivos csv de origen.
        carpeta_sqls (str): Carpeta donde se deben guardar los archivos sql generados.
        conexion (ConexionDB): Conexión a la base de datos de destino.
    """
    crear_tablas(conexion.engine)
    rutas = generar_sqls(carpeta_csvs, carpeta_sqls)
    sentencias = ejecutar_sqls(carpeta_sqls, conexion)
    print(f"Migración completa: {len(rutas)} archivos SQL, {sentencias} sentencias ejecutadas.")


def migrar_datos(carpeta_csvs: str, carpeta_sqls: str):
    """ Función encargada de la migración de datos de csv a sql.
    Se encarga de leer los archivos csv y crear los archivos sql
    para la inserción en la base de datos.

    Args:
        carpeta_csvs (str): Carpeta donde se encuentran los archivos csv de origen.
        carpeta_sqls (str): Carpeta donde se deben guardar los archivos sql generados.
    """
    conexion = ConexionDB()
    try:
        migrar_con_conexion(carpeta_csvs, carpeta_sqls, conexion)
    finally:
        conexion.cerrar()