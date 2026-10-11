"""Modelos de SQLAlchemy: definición de las tablas de la base de datos de Book Manager.

Los identificadores (id) los asigna la aplicación, igual que en el Sprint 1, y por eso
las claves primarias no son autoincrementales. Las claves foráneas impiden dejar datos
huérfanos: una editorial, un género, una moneda o un tipo de cotización en uso no se
pueden borrar, y al borrar un libro se borran también sus precios y su stock.
"""
import datetime
from decimal import Decimal

from sqlalchemy import (CheckConstraint, Date, ForeignKey, Numeric, String,
                        UniqueConstraint)
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Clase base de todos los modelos."""


class GeneroModel(Base):
    """Tabla generos: categorías literarias."""

    __tablename__ = "generos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    nombre: Mapped[str] = mapped_column(String(100), unique=True)


class EditorialModel(Base):
    """Tabla editoriales: proveedores de libros."""

    __tablename__ = "editoriales"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    nombre: Mapped[str] = mapped_column(String(100), unique=True)
    pais: Mapped[str] = mapped_column(String(60))


class MonedaModel(Base):
    """Tabla monedas: monedas en las que se expresan los precios."""

    __tablename__ = "monedas"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    codigo: Mapped[str] = mapped_column(String(10), unique=True)
    nombre: Mapped[str] = mapped_column(String(60))
    simbolo: Mapped[str] = mapped_column(String(10))


class TipoCotizacionModel(Base):
    """Tabla tipos_cotizacion: tipos de dólar (oficial, blue, MEP, etc.)."""

    __tablename__ = "tipos_cotizacion"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    nombre: Mapped[str] = mapped_column(String(60), unique=True)


class LibroModel(Base):
    """Tabla libros: catálogo de la librería."""

    __tablename__ = "libros"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    isbn: Mapped[str] = mapped_column(String(13), unique=True)
    titulo: Mapped[str] = mapped_column(String(200))
    autor: Mapped[str] = mapped_column(String(150))
    editorial_id: Mapped[int] = mapped_column(
        ForeignKey("editoriales.id", ondelete="RESTRICT"), index=True)
    genero_id: Mapped[int] = mapped_column(
        ForeignKey("generos.id", ondelete="RESTRICT"), index=True)

    editorial: Mapped[EditorialModel] = relationship(lazy="joined")
    genero: Mapped[GeneroModel] = relationship(lazy="joined")


class PrecioModel(Base):
    """Tabla precios: precio de un libro en una moneda (uno por libro y moneda)."""

    __tablename__ = "precios"
    __table_args__ = (
        UniqueConstraint("libro_id", "moneda_id", name="uq_precios_libro_moneda"),
        CheckConstraint("valor >= 0", name="ck_precios_valor_no_negativo"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    libro_id: Mapped[int] = mapped_column(
        ForeignKey("libros.id", ondelete="CASCADE"), index=True)
    moneda_id: Mapped[int] = mapped_column(
        ForeignKey("monedas.id", ondelete="RESTRICT"), index=True)
    valor: Mapped[Decimal] = mapped_column(Numeric(14, 2))

    libro: Mapped[LibroModel] = relationship(lazy="joined")
    moneda: Mapped[MonedaModel] = relationship(lazy="joined")


class StockModel(Base):
    """Tabla stock: unidades disponibles de cada libro (un registro por libro)."""

    __tablename__ = "stock"
    __table_args__ = (
        CheckConstraint("cantidad >= 0", name="ck_stock_cantidad_no_negativa"),
    )

    libro_id: Mapped[int] = mapped_column(
        ForeignKey("libros.id", ondelete="CASCADE"), primary_key=True, autoincrement=False)
    cantidad: Mapped[int]

    libro: Mapped[LibroModel] = relationship(lazy="joined")


class CotizacionDolarModel(Base):
    """Tabla cotizaciones: histórico del dólar, una fila por tipo y fecha."""

    __tablename__ = "cotizaciones"
    __table_args__ = (
        CheckConstraint("valor_compra >= 0 AND valor_venta >= 0",
                        name="ck_cotizaciones_valores_no_negativos"),
    )

    tipo_id: Mapped[int] = mapped_column(
        ForeignKey("tipos_cotizacion.id", ondelete="RESTRICT"), primary_key=True,
        autoincrement=False)
    fecha: Mapped[datetime.date] = mapped_column(Date, primary_key=True)
    valor_compra: Mapped[Decimal] = mapped_column(Numeric(14, 4))
    valor_venta: Mapped[Decimal] = mapped_column(Numeric(14, 4))

    tipo: Mapped[TipoCotizacionModel] = relationship(lazy="joined")


def crear_tablas(engine: Engine) -> None:
    """Crea las tablas que todavía no existan. No modifica las que ya están creadas."""
    Base.metadata.create_all(engine)


def eliminar_tablas(engine: Engine) -> None:
    """Borra todas las tablas y sus datos. Solo para desarrollo y pruebas."""
    Base.metadata.drop_all(engine)