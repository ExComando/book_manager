from datetime import date
from typing import Optional

class Genero:
    def __init__(self, id_genero: int, nombre: str):
        self._id_genero = id_genero
        self._nombre = nombre

    @property
    def id_genero(self) -> int:
        return self._id_genero

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str):
        self._nombre = valor


class Editorial:
    def __init__(self, id_editorial: int, nombre: str):
        self._id_editorial = id_editorial
        self._nombre = nombre

    @property
    def id_editorial(self) -> int:
        return self._id_editorial

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str):
        self._nombre = valor


class Moneda:
    def __init__(self, id_moneda: int, codigo: str, simbolo: str):
        self._id_moneda = id_moneda
        self._codigo = codigo  # Ej: 'USD', 'ARS'
        self._simbolo = simbolo

    @property
    def id_moneda(self) -> int:
        return self._id_moneda

    @property
    def codigo(self) -> str:
        return self._codigo

    @property
    def simbolo(self) -> str:
        return self._simbolo


class TipoCotizacion:
    def __init__(self, id_tipo: int, nombre: str):
        self._id_tipo = id_tipo
        self._nombre = nombre  # Ej: 'Oficial', 'Blue', 'MEP'

    @property
    def id_tipo(self) -> int:
        return self._id_tipo

    @property
    def nombre(self) -> str:
        return self._nombre


class CotizacionDolar:
    def __init__(self, tipo_cotizacion: TipoCotizacion, fecha: date, valor_venta: float):
        self._tipo_cotizacion = tipo_cotizacion
        self._fecha = fecha
        self._valor_venta = valor_venta

    @property
    def tipo_cotizacion(self) -> TipoCotizacion:
        return self._tipo_cotizacion

    @property
    def fecha(self) -> date:
        return self._fecha

    @property
    def valor_venta(self) -> float:
        return self._valor_venta

    @valor_venta.setter
    def valor_venta(self, valor: float):
        self._valor_venta = valor


class Libro:
    def __init__(self, isbn: str, titulo: str, autor: str, editorial: Editorial, genero: Genero):
        self._isbn = isbn
        self._titulo = titulo
        self._autor = autor
        self._editorial = editorial
        self._genero = genero

    @property
    def isbn(self) -> str:
        return self._isbn

    @property
    def titulo(self) -> str:
        return self._titulo

    @titulo.setter
    def titulo(self, valor: str):
        self._titulo = valor

    @property
    def autor(self) -> str:
        return self._autor

    @property
    def editorial(self) -> Editorial:
        return self._editorial

    @property
    def genero(self) -> Genero:
        return self._genero


class Precio:
    def __init__(self, libro: Libro, moneda: Moneda, monto: float):
        self._libro = libro
        self._moneda = moneda
        self._monto = monto

    @property
    def libro(self) -> Libro:
        return self._libro

    @property
    def moneda(self) -> Moneda:
        return self._moneda

    @property
    def monto(self) -> float:
        return self._monto

    @monto.setter
    def monto(self, valor: float):
        if valor < 0:
            raise ValueError("El precio no puede ser negativo")
        self._monto = valor


class Stock:
    def __init__(self, libro: Libro, cantidad: int):
        self._libro = libro
        self._cantidad = cantidad

    @property
    def libro(self) -> Libro:
        return self._libro

    @property
    def cantidad(self) -> int:
        return self._cantidad

    @cantidad.setter
    def cantidad(self, valor: int):
        if valor < 0:
            raise ValueError("El stock no puede ser negativo")
        self._cantidad = valor