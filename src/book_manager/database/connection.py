"""Conexión a la base de datos mediante SQLAlchemy."""
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Optional

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL, Engine, make_url
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

# Raíz del proyecto: .../book_manager/src/book_manager/database/connection.py -> .../book_manager
RAIZ_PROYECTO = Path(__file__).resolve().parents[3]


def cargar_variables_entorno() -> None:
    """Carga las variables de entorno desde .env.local y luego desde .env.

    Una variable que ya esté definida (por ejemplo, desde un secret de Colab) no se
    pisa, y .env.local tiene prioridad sobre .env.
    """
    load_dotenv(RAIZ_PROYECTO / ".env.local")
    load_dotenv(RAIZ_PROYECTO / ".env")


def normalizar_url(url: str) -> URL:
    """Convierte la URL en un objeto URL de SQLAlchemy con el driver explícito.

    Las URL de Postgres que entrega Supabase empiezan con "postgresql://", sin driver.
    Según la versión de SQLAlchemy el driver por defecto cambia (psycopg2 o psycopg),
    así que se fija psycopg2 para que el resultado no dependa de la versión instalada.
    """
    url_sqlalchemy = make_url(url)
    if url_sqlalchemy.drivername in ("postgres", "postgresql"):
        url_sqlalchemy = url_sqlalchemy.set(drivername="postgresql+psycopg2")
    return url_sqlalchemy


class ConexionDB:
    """Administra el motor (engine) y las sesiones de SQLAlchemy."""

    def __init__(self, url: Optional[str] = None) -> None:
        """Crea la conexión.

        Args:
            url: URL de conexión. Si no se indica, se lee DATABASE_URL del entorno.

        Raises:
            ValueError: si no hay ninguna URL disponible.
        """
        cargar_variables_entorno()
        url = url or os.getenv("DATABASE_URL")
        if not url:
            raise ValueError(
                "Falta DATABASE_URL: definila en .env.local (o como variable de entorno).")
        self._engine: Engine = create_engine(normalizar_url(url), pool_pre_ping=True)
        self._fabrica_sesiones = sessionmaker(bind=self._engine, expire_on_commit=False)

    @property
    def engine(self) -> Engine:
        """Motor de SQLAlchemy asociado a la base."""
        return self._engine

    def descripcion(self) -> str:
        """URL de conexión con la contraseña oculta, segura para mostrar o registrar."""
        return self._engine.url.render_as_string(hide_password=True)

    def crear_sesion(self) -> Session:
        """Devuelve una sesión nueva. Quien la pide debe cerrarla."""
        return self._fabrica_sesiones()

    @contextmanager
    def transaccion(self) -> Iterator[Session]:
        """Context manager que ejecuta un bloque de trabajo como una transacción.

        Si el bloque termina bien, confirma los cambios (commit). Si ocurre cualquier
        excepción, los revierte (rollback) y la vuelve a lanzar. En ambos casos la
        sesión se cierra al salir.

        Ejemplo:
            with conexion.transaccion() as sesion:
                sesion.add(objeto)
        """
        sesion = self.crear_sesion()
        try:
            yield sesion
            sesion.commit()
        except Exception:
            sesion.rollback()
            raise
        finally:
            sesion.close()

    def probar_conexion(self) -> bool:
        """Indica si se puede ejecutar una consulta simple contra la base."""
        try:
            with self._engine.connect() as conexion:
                conexion.execute(text("SELECT 1"))
            return True
        except SQLAlchemyError:
            return False

    def cerrar(self) -> None:
        """Libera las conexiones abiertas del motor."""
        self._engine.dispose()