import abc
from typing import TypeVar, Generic, List, Optional, Dict
import datetime
from book_manager.entities.entities import (
    Libro, Genero, Editorial, Moneda, 
    TipoCotizacion, CotizacionDolar, Precio, Stock
)

# --- Base abstracta (proveída en la consigna) ---
T = TypeVar('T')

class IRepositorio(abc.ABC, Generic[T]):
    @abc.abstractmethod
    def crear(self, entidad: T) -> T:
        pass

    @abc.abstractmethod
    def leer_por_id(self, id) -> Optional[T]:
        pass

    @abc.abstractmethod
    def leer_todos(self) -> List[T]:
        pass

    @abc.abstractmethod
    def actualizar(self, entidad: T) -> T:
        pass

    @abc.abstractmethod
    def eliminar(self, id) -> bool:
        pass


class IRepositorioStock(abc.ABC):
    @abc.abstractmethod
    def crear(self, stock: Stock) -> Stock:
        pass

    @abc.abstractmethod
    def leer_por_libro(self, libro_id: str) -> Optional[Stock]:
        pass

    @abc.abstractmethod
    def actualizar(self, stock: Stock) -> Stock:
        pass

    @abc.abstractmethod
    def eliminar(self, libro_id: str) -> bool:
        pass


class IRepositorioCotizacionDolar(abc.ABC):
    @abc.abstractmethod
    def crear(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        pass

    @abc.abstractmethod
    def leer_por_tipo_y_fecha(self, tipo_id: int, fecha: datetime.date) -> Optional[CotizacionDolar]:
        pass

    @abc.abstractmethod
    def leer_historico_por_tipo(self, tipo_id: int) -> List[CotizacionDolar]:
        pass

    @abc.abstractmethod
    def actualizar(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        pass

    @abc.abstractmethod
    def eliminar(self, tipo_id: int, fecha: datetime.date) -> bool:
        pass


# --- Implementaciones Concretas (CRUD) ---

class RepositorioLibro(IRepositorio[Libro]):
    def __init__(self):
        self._datos: Dict[str, Libro] = {}

    def crear(self, entidad: Libro) -> Libro:
        if entidad.isbn in self._datos:
            raise ValueError("Ya existe un libro con ese ISBN.")
        self._datos[entidad.isbn] = entidad
        return entidad

    def leer_por_id(self, id: str) -> Optional[Libro]:
        return self._datos.get(id)

    def leer_todos(self) -> List[Libro]:
        return list(self._datos.values())

    def actualizar(self, entidad: Libro) -> Libro:
        if entidad.isbn not in self._datos:
            raise ValueError("Libro no encontrado.")
        self._datos[entidad.isbn] = entidad
        return entidad

    def eliminar(self, id: str) -> bool:
        if id in self._datos:
            del self._datos[id]
            return True
        return False


class RepositorioGenero(IRepositorio[Genero]):
    def __init__(self):
        self._datos: Dict[int, Genero] = {}

    def crear(self, entidad: Genero) -> Genero:
        if entidad.id_genero in self._datos:
            raise ValueError("Ya existe un género con ese ID.")
        self._datos[entidad.id_genero] = entidad
        return entidad

    def leer_por_id(self, id: int) -> Optional[Genero]:
        return self._datos.get(id)

    def leer_todos(self) -> List[Genero]:
        return list(self._datos.values())

    def actualizar(self, entidad: Genero) -> Genero:
        if entidad.id_genero not in self._datos:
            raise ValueError("Género no encontrado.")
        self._datos[entidad.id_genero] = entidad
        return entidad

    def eliminar(self, id: int) -> bool:
        if id in self._datos:
            del self._datos[id]
            return True
        return False


class RepositorioEditorial(IRepositorio[Editorial]):
    def __init__(self):
        self._datos: Dict[int, Editorial] = {}

    def crear(self, entidad: Editorial) -> Editorial:
        if entidad.id_editorial in self._datos:
            raise ValueError("Ya existe una editorial con ese ID.")
        self._datos[entidad.id_editorial] = entidad
        return entidad

    def leer_por_id(self, id: int) -> Optional[Editorial]:
        return self._datos.get(id)

    def leer_todos(self) -> List[Editorial]:
        return list(self._datos.values())

    def actualizar(self, entidad: Editorial) -> Editorial:
        if entidad.id_editorial not in self._datos:
            raise ValueError("Editorial no encontrada.")
        self._datos[entidad.id_editorial] = entidad
        return entidad

    def eliminar(self, id: int) -> bool:
        if id in self._datos:
            del self._datos[id]
            return True
        return False


class RepositorioStock(IRepositorioStock):
    def __init__(self):
        self._datos: Dict[str, Stock] = {}

    def crear(self, stock: Stock) -> Stock:
        if stock.libro.isbn in self._datos:
            raise ValueError("Ya existe stock registrado para este libro.")
        self._datos[stock.libro.isbn] = stock
        return stock

    def leer_por_libro(self, libro_id: str) -> Optional[Stock]:
        return self._datos.get(libro_id)

    def actualizar(self, stock: Stock) -> Stock:
        if stock.libro.isbn not in self._datos:
            raise ValueError("Registro de stock no encontrado.")
        self._datos[stock.libro.isbn] = stock
        return stock

    def eliminar(self, libro_id: str) -> bool:
        if libro_id in self._datos:
            del self._datos[libro_id]
            return True
        return False


class RepositorioCotizacionDolar(IRepositorioCotizacionDolar):
    def __init__(self):
        # Clave compuesta: "tipo_id|fecha"
        self._datos: Dict[str, CotizacionDolar] = {}

    def _generar_clave(self, tipo_id: int, fecha: datetime.date) -> str:
        return f"{tipo_id}|{fecha.isoformat()}"

    def crear(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        clave = self._generar_clave(cotizacion.tipo_cotizacion.id_tipo, cotizacion.fecha)
        if clave in self._datos:
            raise ValueError("Ya existe una cotización para ese tipo y fecha.")
        self._datos[clave] = cotizacion
        return cotizacion

    def leer_por_tipo_y_fecha(self, tipo_id: int, fecha: datetime.date) -> Optional[CotizacionDolar]:
        clave = self._generar_clave(tipo_id, fecha)
        return self._datos.get(clave)

    def leer_historico_por_tipo(self, tipo_id: int) -> List[CotizacionDolar]:
        return [c for c in self._datos.values() if c.tipo_cotizacion.id_tipo == tipo_id]

    def actualizar(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        clave = self._generar_clave(cotizacion.tipo_cotizacion.id_tipo, cotizacion.fecha)
        if clave not in self._datos:
            raise ValueError("Cotización no encontrada para actualizar.")
        self._datos[clave] = cotizacion
        return cotizacion

    def eliminar(self, tipo_id: int, fecha: datetime.date) -> bool:
        clave = self._generar_clave(tipo_id, fecha)
        if clave in self._datos:
            del self._datos[clave]
            return True
        return False

class IRepositorioPrecio(abc.ABC):
    @abc.abstractmethod
    def crear(self, precio: Precio) -> Precio:
        pass

    @abc.abstractmethod
    def leer_por_libro(self, isbn: str) -> Optional[Precio]:
        pass

    @abc.abstractmethod
    def actualizar(self, precio: Precio) -> Precio:
        pass

class RepositorioPrecio(IRepositorioPrecio):
    def __init__(self):
        self._datos: Dict[str, Precio] = {}

    def crear(self, precio: Precio) -> Precio:
        if precio.libro.isbn in self._datos:
            raise ValueError("Ya existe un precio registrado para este libro.")
        self._datos[precio.libro.isbn] = precio
        return precio

    def leer_por_libro(self, isbn: str) -> Optional[Precio]:
        return self._datos.get(isbn)

    def actualizar(self, precio: Precio) -> Precio:
        if precio.libro.isbn not in self._datos:
            raise ValueError("Precio no encontrado para actualizar.")
        self._datos[precio.libro.isbn] = precio
        return precio    