"""Repositorios de persistencia en archivos CSV."""
import abc
import csv
import datetime
import os
from decimal import Decimal
from typing import Dict, Generic, List, Optional, TypeVar

from book_manager.entities.entities import (
    CotizacionDolar, Editorial, EntidadBase, Genero, Libro, Moneda,
    Precio, Stock, TipoCotizacion)

# La ruta se calcula a partir de este archivo, así no depende de la carpeta
# desde la que se ejecute el programa.
RUTA_CSV_DEFECTO = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "migrations", "csv")

T = TypeVar('T', bound=EntidadBase)


class IRepositorio(abc.ABC, Generic[T]):
    """Interfaz para repositorios que manejan entidades con operaciones CRUD básicas."""

    @abc.abstractmethod
    def crear(self, entidad: T) -> T:
        """Crea una nueva entidad. Lanza ValueError si ya existe el ID."""
        pass

    @abc.abstractmethod
    def leer_por_id(self, id: int) -> Optional[T]:
        """Lee una entidad por su ID. Devuelve None si no existe."""
        pass

    @abc.abstractmethod
    def leer_todos(self) -> List[T]:
        """Lee todas las entidades del repositorio."""
        pass

    @abc.abstractmethod
    def actualizar(self, entidad: T) -> T:
        """Actualiza una entidad existente. Lanza ValueError si no existe."""
        pass

    @abc.abstractmethod
    def eliminar(self, id: int) -> bool:
        """Elimina una entidad por ID. Devuelve False si no se encontró."""
        pass


class IRepositorioStock(abc.ABC):
    """Interfaz para repositorios del tipo Stock."""

    @abc.abstractmethod
    def crear(self, stock: Stock) -> Stock:
        """Crea un registro de stock. Lanza ValueError si ya existe para el libro."""
        pass

    @abc.abstractmethod
    def leer_por_libro(self, libro_id: int) -> Optional[Stock]:
        """Lee el stock de un libro. Devuelve None si no existe."""
        pass

    @abc.abstractmethod
    def actualizar(self, stock: Stock) -> Stock:
        """Actualiza un stock existente. Lanza ValueError si no existe."""
        pass

    @abc.abstractmethod
    def eliminar(self, libro_id: int) -> bool:
        """Elimina el stock de un libro. Devuelve False si no se encontró."""
        pass


class IRepositorioCotizacionDolar(abc.ABC):
    """Interfaz para repositorios del tipo CotizacionDolar."""

    @abc.abstractmethod
    def crear(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        """Crea una cotización. Lanza ValueError si ya existe para tipo y fecha."""
        pass

    @abc.abstractmethod
    def leer_por_tipo_y_fecha(
            self, tipo_id: int, fecha: datetime.date) -> Optional[CotizacionDolar]:
        """Lee una cotización por tipo y fecha. Devuelve None si no existe."""
        pass

    @abc.abstractmethod
    def leer_historico_por_tipo(self, tipo_id: int) -> List[CotizacionDolar]:
        """Lee el histórico de cotizaciones de un tipo."""
        pass

    @abc.abstractmethod
    def actualizar(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        """Actualiza una cotización existente. Lanza ValueError si no existe."""
        pass

    @abc.abstractmethod
    def eliminar(self, tipo_id: int, fecha: datetime.date) -> bool:
        """Elimina una cotización por tipo y fecha. Devuelve False si no se encontró."""
        pass


class _ArchivoCsv:
    """Lectura y escritura de filas en un archivo CSV con encabezado."""

    CAMPOS: List[str] = []

    def __init__(self, ruta: str) -> None:
        self._ruta = ruta
        directorio = os.path.dirname(ruta)
        if directorio:
            os.makedirs(directorio, exist_ok=True)
        if not os.path.exists(ruta):
            self._escribir_filas([])

    def _leer_filas(self) -> List[Dict[str, str]]:
        """Devuelve todas las filas del archivo como diccionarios."""
        with open(self._ruta, newline="", encoding="utf-8") as archivo:
            return list(csv.DictReader(archivo))

    def _escribir_filas(self, filas: List[Dict[str, str]]) -> None:
        """Reescribe el archivo completo con el encabezado y las filas dadas."""
        with open(self._ruta, "w", newline="", encoding="utf-8") as archivo:
            escritor = csv.DictWriter(archivo, fieldnames=self.CAMPOS)
            escritor.writeheader()
            escritor.writerows(filas)


class RepositorioCsv(_ArchivoCsv, IRepositorio[T]):
    """CRUD genérico sobre CSV para entidades con id propio."""

    @abc.abstractmethod
    def _a_fila(self, entidad: T) -> Dict[str, str]:
        """Convierte una entidad en una fila de CSV."""

    @abc.abstractmethod
    def _desde_fila(self, fila: Dict[str, str]) -> T:
        """Reconstruye la entidad (con sus objetos relacionados) desde una fila."""

    def siguiente_id(self) -> int:
        """Devuelve el próximo ID libre."""
        ids = [int(fila["id"]) for fila in self._leer_filas()]
        return max(ids, default=0) + 1

    def crear(self, entidad: T) -> T:
        filas = self._leer_filas()
        if any(int(fila["id"]) == entidad.id for fila in filas):
            raise ValueError(f"Ya existe una entidad con id {entidad.id}.")
        filas.append(self._a_fila(entidad))
        self._escribir_filas(filas)
        return entidad

    def leer_por_id(self, id: int) -> Optional[T]:
        for fila in self._leer_filas():
            if int(fila["id"]) == id:
                return self._desde_fila(fila)
        return None

    def leer_todos(self) -> List[T]:
        return [self._desde_fila(fila) for fila in self._leer_filas()]

    def actualizar(self, entidad: T) -> T:
        filas = self._leer_filas()
        for posicion, fila in enumerate(filas):
            if int(fila["id"]) == entidad.id:
                filas[posicion] = self._a_fila(entidad)
                self._escribir_filas(filas)
                return entidad
        raise ValueError(f"No existe una entidad con id {entidad.id}.")

    def eliminar(self, id: int) -> bool:
        filas = self._leer_filas()
        restantes = [fila for fila in filas if int(fila["id"]) != id]
        if len(restantes) == len(filas):
            return False
        self._escribir_filas(restantes)
        return True


class RepositorioGenero(RepositorioCsv[Genero]):
    """Persistencia de géneros."""

    CAMPOS = ["id", "nombre"]

    def __init__(self, ruta: str = os.path.join(RUTA_CSV_DEFECTO, "generos.csv")) -> None:
        super().__init__(ruta)

    def _a_fila(self, entidad: Genero) -> Dict[str, str]:
        return {"id": entidad.id, "nombre": entidad.nombre}

    def _desde_fila(self, fila: Dict[str, str]) -> Genero:
        return Genero(int(fila["id"]), fila["nombre"])


class RepositorioEditorial(RepositorioCsv[Editorial]):
    """Persistencia de editoriales."""

    CAMPOS = ["id", "nombre", "pais"]

    def __init__(self, ruta: str = os.path.join(RUTA_CSV_DEFECTO, "editoriales.csv")) -> None:
        super().__init__(ruta)

    def _a_fila(self, entidad: Editorial) -> Dict[str, str]:
        return {"id": entidad.id, "nombre": entidad.nombre, "pais": entidad.pais}

    def _desde_fila(self, fila: Dict[str, str]) -> Editorial:
        return Editorial(int(fila["id"]), fila["nombre"], fila["pais"])


class RepositorioMoneda(RepositorioCsv[Moneda]):
    """Persistencia de monedas."""

    CAMPOS = ["id", "codigo", "nombre", "simbolo"]

    def __init__(self, ruta: str = os.path.join(RUTA_CSV_DEFECTO, "monedas.csv")) -> None:
        super().__init__(ruta)

    def _a_fila(self, entidad: Moneda) -> Dict[str, str]:
        return {"id": entidad.id, "codigo": entidad.codigo,
                "nombre": entidad.nombre, "simbolo": entidad.simbolo}

    def _desde_fila(self, fila: Dict[str, str]) -> Moneda:
        return Moneda(int(fila["id"]), fila["codigo"], fila["nombre"], fila["simbolo"])


class RepositorioTipoCotizacion(RepositorioCsv[TipoCotizacion]):
    """Persistencia de tipos de cotización."""

    CAMPOS = ["id", "nombre"]

    def __init__(self, ruta: str = os.path.join(RUTA_CSV_DEFECTO, "tipos_cotizacion.csv")) -> None:
        super().__init__(ruta)

    def _a_fila(self, entidad: TipoCotizacion) -> Dict[str, str]:
        return {"id": entidad.id, "nombre": entidad.nombre}

    def _desde_fila(self, fila: Dict[str, str]) -> TipoCotizacion:
        return TipoCotizacion(int(fila["id"]), fila["nombre"])


class RepositorioLibro(RepositorioCsv[Libro]):
    """Persistencia de libros. Guarda IDs y reconstruye Editorial y Genero como objetos."""

    CAMPOS = ["id", "isbn", "titulo", "autor", "editorial_id", "genero_id"]

    def __init__(self, repo_editorial: RepositorioEditorial, repo_genero: RepositorioGenero,
                 ruta: str = os.path.join(RUTA_CSV_DEFECTO, "libros.csv")) -> None:
        super().__init__(ruta)
        self._repo_editorial = repo_editorial
        self._repo_genero = repo_genero

    def _a_fila(self, entidad: Libro) -> Dict[str, str]:
        return {"id": entidad.id, "isbn": entidad.isbn, "titulo": entidad.titulo,
                "autor": entidad.autor, "editorial_id": entidad.editorial.id,
                "genero_id": entidad.genero.id}

    def _desde_fila(self, fila: Dict[str, str]) -> Libro:
        editorial = self._repo_editorial.leer_por_id(int(fila["editorial_id"]))
        genero = self._repo_genero.leer_por_id(int(fila["genero_id"]))
        if editorial is None or genero is None:
            raise ValueError(f"El libro {fila['id']} referencia una editorial o género inexistente.")
        return Libro(int(fila["id"]), fila["isbn"], fila["titulo"], fila["autor"],
                     editorial, genero)


class RepositorioPrecio(RepositorioCsv[Precio]):
    """Persistencia de precios. Reconstruye Libro y Moneda como objetos."""

    CAMPOS = ["id", "libro_id", "moneda_id", "valor"]

    def __init__(self, repo_libro: RepositorioLibro, repo_moneda: RepositorioMoneda,
                 ruta: str = os.path.join(RUTA_CSV_DEFECTO, "precios.csv")) -> None:
        super().__init__(ruta)
        self._repo_libro = repo_libro
        self._repo_moneda = repo_moneda

    def _a_fila(self, entidad: Precio) -> Dict[str, str]:
        return {"id": entidad.id, "libro_id": entidad.libro.id,
                "moneda_id": entidad.moneda.id, "valor": str(entidad.valor)}

    def _desde_fila(self, fila: Dict[str, str]) -> Precio:
        libro = self._repo_libro.leer_por_id(int(fila["libro_id"]))
        moneda = self._repo_moneda.leer_por_id(int(fila["moneda_id"]))
        if libro is None or moneda is None:
            raise ValueError(f"El precio {fila['id']} referencia un libro o moneda inexistente.")
        return Precio(int(fila["id"]), libro, moneda, Decimal(fila["valor"]))


class RepositorioStock(_ArchivoCsv, IRepositorioStock):
    """Persistencia de stock, un registro por libro."""

    CAMPOS = ["libro_id", "cantidad"]

    def __init__(self, repo_libro: RepositorioLibro,
                 ruta: str = os.path.join(RUTA_CSV_DEFECTO, "stock.csv")) -> None:
        super().__init__(ruta)
        self._repo_libro = repo_libro

    def _a_fila(self, stock: Stock) -> Dict[str, str]:
        return {"libro_id": stock.libro_id, "cantidad": stock.cantidad}

    def _desde_fila(self, fila: Dict[str, str]) -> Stock:
        libro = self._repo_libro.leer_por_id(int(fila["libro_id"]))
        if libro is None:
            raise ValueError(f"El stock referencia el libro inexistente {fila['libro_id']}.")
        return Stock(libro, int(fila["cantidad"]))

    def crear(self, stock: Stock) -> Stock:
        filas = self._leer_filas()
        if any(int(fila["libro_id"]) == stock.libro_id for fila in filas):
            raise ValueError(f"Ya existe stock para el libro {stock.libro_id}.")
        filas.append(self._a_fila(stock))
        self._escribir_filas(filas)
        return stock

    def leer_por_libro(self, libro_id: int) -> Optional[Stock]:
        for fila in self._leer_filas():
            if int(fila["libro_id"]) == libro_id:
                return self._desde_fila(fila)
        return None

    def leer_todos(self) -> List[Stock]:
        """Lee todos los registros de stock (ampliación sobre la interfaz)."""
        return [self._desde_fila(fila) for fila in self._leer_filas()]

    def actualizar(self, stock: Stock) -> Stock:
        filas = self._leer_filas()
        for posicion, fila in enumerate(filas):
            if int(fila["libro_id"]) == stock.libro_id:
                filas[posicion] = self._a_fila(stock)
                self._escribir_filas(filas)
                return stock
        raise ValueError(f"No existe stock para el libro {stock.libro_id}.")

    def eliminar(self, libro_id: int) -> bool:
        filas = self._leer_filas()
        restantes = [fila for fila in filas if int(fila["libro_id"]) != libro_id]
        if len(restantes) == len(filas):
            return False
        self._escribir_filas(restantes)
        return True


class RepositorioCotizacionDolar(_ArchivoCsv, IRepositorioCotizacionDolar):
    """Persistencia del histórico de cotizaciones, identificadas por tipo y fecha."""

    CAMPOS = ["tipo_id", "fecha", "valor_compra", "valor_venta"]

    def __init__(self, repo_tipo: RepositorioTipoCotizacion,
                 ruta: str = os.path.join(RUTA_CSV_DEFECTO, "cotizaciones.csv")) -> None:
        super().__init__(ruta)
        self._repo_tipo = repo_tipo

    def _a_fila(self, cotizacion: CotizacionDolar) -> Dict[str, str]:
        return {"tipo_id": cotizacion.tipo_id, "fecha": cotizacion.fecha.isoformat(),
                "valor_compra": str(cotizacion.valor_compra),
                "valor_venta": str(cotizacion.valor_venta)}

    def _desde_fila(self, fila: Dict[str, str]) -> CotizacionDolar:
        tipo = self._repo_tipo.leer_por_id(int(fila["tipo_id"]))
        if tipo is None:
            raise ValueError(f"La cotización referencia el tipo inexistente {fila['tipo_id']}.")
        return CotizacionDolar(tipo, datetime.date.fromisoformat(fila["fecha"]),
                               Decimal(fila["valor_compra"]), Decimal(fila["valor_venta"]))

    @staticmethod
    def _coincide(fila: Dict[str, str], tipo_id: int, fecha: datetime.date) -> bool:
        return int(fila["tipo_id"]) == tipo_id and fila["fecha"] == fecha.isoformat()

    def crear(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        filas = self._leer_filas()
        if any(self._coincide(f, cotizacion.tipo_id, cotizacion.fecha) for f in filas):
            raise ValueError("Ya existe una cotización para ese tipo y fecha.")
        filas.append(self._a_fila(cotizacion))
        self._escribir_filas(filas)
        return cotizacion

    def leer_por_tipo_y_fecha(
            self, tipo_id: int, fecha: datetime.date) -> Optional[CotizacionDolar]:
        for fila in self._leer_filas():
            if self._coincide(fila, tipo_id, fecha):
                return self._desde_fila(fila)
        return None

    def leer_historico_por_tipo(self, tipo_id: int) -> List[CotizacionDolar]:
        historico = [self._desde_fila(f) for f in self._leer_filas()
                     if int(f["tipo_id"]) == tipo_id]
        return sorted(historico, key=lambda cotizacion: cotizacion.fecha)

    def leer_todos(self) -> List[CotizacionDolar]:
        """Lee todas las cotizaciones (ampliación sobre la interfaz)."""
        return [self._desde_fila(fila) for fila in self._leer_filas()]

    def actualizar(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        filas = self._leer_filas()
        for posicion, fila in enumerate(filas):
            if self._coincide(fila, cotizacion.tipo_id, cotizacion.fecha):
                filas[posicion] = self._a_fila(cotizacion)
                self._escribir_filas(filas)
                return cotizacion
        raise ValueError("No existe una cotización para ese tipo y fecha.")

    def eliminar(self, tipo_id: int, fecha: datetime.date) -> bool:
        filas = self._leer_filas()
        restantes = [f for f in filas if not self._coincide(f, tipo_id, fecha)]
        if len(restantes) == len(filas):
            return False
        self._escribir_filas(restantes)
        return True
