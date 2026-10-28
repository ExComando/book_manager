"""Repositorios de persistencia en base de datos (SQLAlchemy).

Cada repositorio traduce entre las entidades del dominio y los modelos (tablas) de la
base. Hacia afuera siguen recibiendo y devolviendo entidades con sus objetos
relacionados, igual que en el Sprint 1: los servicios y la consola no saben que el
almacenamiento cambió de archivos CSV a una base de datos.
"""
import abc
import datetime
from typing import Callable, Generic, List, Optional, TypeVar

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from book_manager.database.connection import ConexionDB
from book_manager.entities.entities import (
    Auditoria, CotizacionDolar, Editorial, EntidadBase, Genero, Libro, Moneda,
    Precio, PrecioWeb, Stock, TipoCotizacion)
from book_manager.models.models import (
    AuditoriaModel, CotizacionDolarModel, EditorialModel, GeneroModel, LibroModel, MonedaModel,
    PrecioModel, PrecioWebModel, StockModel, TipoCotizacionModel)

T = TypeVar('T', bound=EntidadBase)
R = TypeVar('R')


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


# ---------------------------------------------------------------- modelo -> entidad
def _a_genero(modelo: GeneroModel) -> Genero:
    """Convierte el modelo de la tabla generos en la entidad Genero."""
    return Genero(modelo.id, modelo.nombre)


def _a_editorial(modelo: EditorialModel) -> Editorial:
    """Convierte el modelo de la tabla editoriales en la entidad Editorial."""
    return Editorial(modelo.id, modelo.nombre, modelo.pais)


def _a_moneda(modelo: MonedaModel) -> Moneda:
    """Convierte el modelo de la tabla monedas en la entidad Moneda."""
    return Moneda(modelo.id, modelo.codigo, modelo.nombre, modelo.simbolo)


def _a_tipo(modelo: TipoCotizacionModel) -> TipoCotizacion:
    """Convierte el modelo de la tabla tipos_cotizacion en la entidad TipoCotizacion."""
    return TipoCotizacion(modelo.id, modelo.nombre)


def _a_libro(modelo: LibroModel) -> Libro:
    """Convierte el modelo de la tabla libros en un Libro, con su editorial y su género."""
    return Libro(modelo.id, modelo.isbn, modelo.titulo, modelo.autor,
                 _a_editorial(modelo.editorial), _a_genero(modelo.genero))


def _a_precio(modelo: PrecioModel) -> Precio:
    """Convierte el modelo de la tabla precios en un Precio, con su libro y su moneda."""
    return Precio(modelo.id, _a_libro(modelo.libro), _a_moneda(modelo.moneda), modelo.valor)


def _a_precio_web(modelo: PrecioWebModel) -> PrecioWeb:
    """Reconstruye un PrecioWeb (con su Libro) desde el modelo de la tabla precios_web."""
    return PrecioWeb(modelo.id, _a_libro(modelo.libro), modelo.titulo_web, modelo.isbn_web,
                     modelo.url, modelo.precio, modelo.url_imagen, modelo.formas_pago,
                     modelo.descripcion, modelo.posicion, modelo.coincide_isbn,
                     modelo.fecha_extraccion)


def _a_stock(modelo: StockModel) -> Stock:
    """Convierte el modelo de la tabla stock en un Stock, con su libro."""
    return Stock(_a_libro(modelo.libro), modelo.cantidad)


def _a_cotizacion(modelo: CotizacionDolarModel) -> CotizacionDolar:
    """Convierte el modelo de la tabla cotizaciones en una CotizacionDolar, con su tipo."""
    return CotizacionDolar(_a_tipo(modelo.tipo), modelo.fecha,
                           modelo.valor_compra, modelo.valor_venta)


# ---------------------------------------------------------------- manejo de errores
# Códigos de error de PostgreSQL (SQLSTATE) que se traducen a mensajes claros.
_MENSAJES_ERROR = {
    "23505": "Ya existe un registro con esos datos (valor duplicado).",
    "23503": "El registro está relacionado con otros datos (referencia inexistente o en uso).",
    "23514": "Un valor no cumple las restricciones permitidas (por ejemplo, un monto negativo).",
}


def _traducir_error(error: IntegrityError) -> ValueError:
    """Convierte un error de integridad de la base en un ValueError con un mensaje claro."""
    codigo = getattr(error.orig, "pgcode", None)
    return ValueError(_MENSAJES_ERROR.get(
        codigo, "La operación viola una restricción de la base de datos."))


class _RepositorioBase:
    """Ejecuta las operaciones de un repositorio dentro de una transacción."""

    def __init__(self, conexion: ConexionDB) -> None:
        """Guarda la conexión a la base de datos que usa el repositorio."""
        self._conexion = conexion

    def _ejecutar(self, operacion: Callable[[Session], R]) -> R:
        """Corre la operación en una transacción. Los errores de integridad de la base
        se informan como ValueError, igual que los demás errores de validación."""
        try:
            with self._conexion.transaccion() as sesion:
                return operacion(sesion)
        except IntegrityError as error:
            raise _traducir_error(error) from error


class RepositorioDB(_RepositorioBase, IRepositorio[T]):
    """CRUD genérico sobre la base de datos para entidades con id propio."""

    _MODELO: type

    @abc.abstractmethod
    def _a_entidad(self, modelo) -> T:
        """Reconstruye la entidad (con sus objetos relacionados) desde un modelo."""

    @abc.abstractmethod
    def _a_modelo(self, entidad: T):
        """Crea un modelo nuevo a partir de una entidad."""

    @abc.abstractmethod
    def _copiar(self, modelo, entidad: T) -> None:
        """Copia los datos de la entidad a un modelo existente."""

    def siguiente_id(self) -> int:
        """Devuelve el próximo ID libre."""
        consulta = select(func.coalesce(func.max(self._MODELO.id), 0) + 1)
        return self._ejecutar(lambda sesion: sesion.scalar(consulta))

    def crear(self, entidad: T) -> T:
        """Guarda una entidad nueva; falla si ya existe una con el mismo id."""
        def operacion(sesion: Session) -> T:
            """Inserta el modelo de la entidad dentro de la transacción."""
            if sesion.get(self._MODELO, entidad.id) is not None:
                raise ValueError(f"Ya existe una entidad con id {entidad.id}.")
            sesion.add(self._a_modelo(entidad))
            sesion.flush()
            return entidad
        return self._ejecutar(operacion)

    def leer_por_id(self, id: int) -> Optional[T]:
        """Devuelve la entidad con ese id, o None si no existe."""
        def operacion(sesion: Session) -> Optional[T]:
            """Busca el modelo por id y lo convierte en entidad."""
            modelo = sesion.get(self._MODELO, id)
            return None if modelo is None else self._a_entidad(modelo)
        return self._ejecutar(operacion)

    def leer_todos(self) -> List[T]:
        """Devuelve todas las entidades, ordenadas por id."""
        def operacion(sesion: Session) -> List[T]:
            """Lee todos los modelos, ordenados por id."""
            modelos = sesion.scalars(select(self._MODELO).order_by(self._MODELO.id)).all()
            return [self._a_entidad(modelo) for modelo in modelos]
        return self._ejecutar(operacion)

    def actualizar(self, entidad: T) -> T:
        """Actualiza una entidad existente; falla si no existe."""
        def operacion(sesion: Session) -> T:
            """Copia los datos de la entidad al modelo guardado."""
            modelo = sesion.get(self._MODELO, entidad.id)
            if modelo is None:
                raise ValueError(f"No existe una entidad con id {entidad.id}.")
            self._copiar(modelo, entidad)
            sesion.flush()
            return entidad
        return self._ejecutar(operacion)

    def eliminar(self, id: int) -> bool:
        """Elimina la entidad con ese id. Devuelve False si no existía."""
        def operacion(sesion: Session) -> bool:
            """Borra el modelo si existe."""
            modelo = sesion.get(self._MODELO, id)
            if modelo is None:
                return False
            sesion.delete(modelo)
            sesion.flush()
            return True
        return self._ejecutar(operacion)


class RepositorioGenero(RepositorioDB[Genero]):
    """Persistencia de géneros."""

    _MODELO = GeneroModel

    def _a_entidad(self, modelo: GeneroModel) -> Genero:
        """Convierte el modelo de la tabla en la entidad Genero."""
        return _a_genero(modelo)

    def _a_modelo(self, entidad: Genero) -> GeneroModel:
        """Crea un modelo nuevo a partir de la entidad."""
        return GeneroModel(id=entidad.id, nombre=entidad.nombre)

    def _copiar(self, modelo: GeneroModel, entidad: Genero) -> None:
        """Copia los datos de la entidad a un modelo existente."""
        modelo.nombre = entidad.nombre


class RepositorioEditorial(RepositorioDB[Editorial]):
    """Persistencia de editoriales."""

    _MODELO = EditorialModel

    def _a_entidad(self, modelo: EditorialModel) -> Editorial:
        """Convierte el modelo de la tabla en la entidad Editorial."""
        return _a_editorial(modelo)

    def _a_modelo(self, entidad: Editorial) -> EditorialModel:
        """Crea un modelo nuevo a partir de la entidad."""
        return EditorialModel(id=entidad.id, nombre=entidad.nombre, pais=entidad.pais)

    def _copiar(self, modelo: EditorialModel, entidad: Editorial) -> None:
        """Copia los datos de la entidad a un modelo existente."""
        modelo.nombre = entidad.nombre
        modelo.pais = entidad.pais


class RepositorioMoneda(RepositorioDB[Moneda]):
    """Persistencia de monedas."""

    _MODELO = MonedaModel

    def _a_entidad(self, modelo: MonedaModel) -> Moneda:
        """Convierte el modelo de la tabla en la entidad Moneda."""
        return _a_moneda(modelo)

    def _a_modelo(self, entidad: Moneda) -> MonedaModel:
        """Crea un modelo nuevo a partir de la entidad."""
        return MonedaModel(id=entidad.id, codigo=entidad.codigo, nombre=entidad.nombre,
                           simbolo=entidad.simbolo)

    def _copiar(self, modelo: MonedaModel, entidad: Moneda) -> None:
        """Copia los datos de la entidad a un modelo existente."""
        modelo.codigo = entidad.codigo
        modelo.nombre = entidad.nombre
        modelo.simbolo = entidad.simbolo


class RepositorioTipoCotizacion(RepositorioDB[TipoCotizacion]):
    """Persistencia de tipos de cotización."""

    _MODELO = TipoCotizacionModel

    def _a_entidad(self, modelo: TipoCotizacionModel) -> TipoCotizacion:
        """Convierte el modelo de la tabla en la entidad TipoCotizacion."""
        return _a_tipo(modelo)

    def _a_modelo(self, entidad: TipoCotizacion) -> TipoCotizacionModel:
        """Crea un modelo nuevo a partir de la entidad."""
        return TipoCotizacionModel(id=entidad.id, nombre=entidad.nombre)

    def _copiar(self, modelo: TipoCotizacionModel, entidad: TipoCotizacion) -> None:
        """Copia los datos de la entidad a un modelo existente."""
        modelo.nombre = entidad.nombre


class RepositorioLibro(RepositorioDB[Libro]):
    """Persistencia de libros. Reconstruye Editorial y Genero como objetos."""

    _MODELO = LibroModel

    def _a_entidad(self, modelo: LibroModel) -> Libro:
        """Convierte el modelo de la tabla en la entidad Libro."""
        return _a_libro(modelo)

    def _a_modelo(self, entidad: Libro) -> LibroModel:
        """Crea un modelo nuevo a partir de la entidad."""
        return LibroModel(id=entidad.id, isbn=entidad.isbn, titulo=entidad.titulo,
                          autor=entidad.autor, editorial_id=entidad.editorial.id,
                          genero_id=entidad.genero.id)

    def _copiar(self, modelo: LibroModel, entidad: Libro) -> None:
        """Copia los datos de la entidad a un modelo existente."""
        modelo.isbn = entidad.isbn
        modelo.titulo = entidad.titulo
        modelo.autor = entidad.autor
        modelo.editorial_id = entidad.editorial.id
        modelo.genero_id = entidad.genero.id


class RepositorioPrecio(RepositorioDB[Precio]):
    """Persistencia de precios. Reconstruye Libro y Moneda como objetos."""

    _MODELO = PrecioModel

    def _a_entidad(self, modelo: PrecioModel) -> Precio:
        """Convierte el modelo de la tabla en la entidad Precio."""
        return _a_precio(modelo)

    def _a_modelo(self, entidad: Precio) -> PrecioModel:
        """Crea un modelo nuevo a partir de la entidad."""
        return PrecioModel(id=entidad.id, libro_id=entidad.libro.id,
                           moneda_id=entidad.moneda.id, valor=entidad.valor)

    def _copiar(self, modelo: PrecioModel, entidad: Precio) -> None:
        """Copia los datos de la entidad a un modelo existente."""
        modelo.libro_id = entidad.libro.id
        modelo.moneda_id = entidad.moneda.id
        modelo.valor = entidad.valor


class RepositorioPrecioWeb(RepositorioDB[PrecioWeb]):
    """Persistencia de los precios web obtenidos por el scraper. Reconstruye el Libro."""

    _MODELO = PrecioWebModel

    def _a_entidad(self, modelo: PrecioWebModel) -> PrecioWeb:
        """Convierte el modelo de la tabla en la entidad PrecioWeb."""
        return _a_precio_web(modelo)

    def _a_modelo(self, entidad: PrecioWeb) -> PrecioWebModel:
        """Crea un modelo nuevo a partir de la entidad."""
        return PrecioWebModel(
            id=entidad.id, libro_id=entidad.libro.id, titulo_web=entidad.titulo_web,
            isbn_web=entidad.isbn_web, url=entidad.url, precio=entidad.precio,
            url_imagen=entidad.url_imagen, formas_pago=entidad.formas_pago,
            descripcion=entidad.descripcion, posicion=entidad.posicion,
            coincide_isbn=entidad.coincide_isbn, fecha_extraccion=entidad.fecha_extraccion)

    def leer_por_extraccion(self, fecha: Optional[datetime.datetime] = None) -> List[PrecioWeb]:
        """Devuelve los precios de una corrida del scraper, ordenados por libro y posición.

        Args:
            fecha: fecha y hora de la corrida. Si no se indica, la más reciente.
        """
        def operacion(sesion: Session) -> List[PrecioWeb]:
            """Lee los precios web de la corrida pedida (o la más reciente)."""
            objetivo = fecha
            if objetivo is None:
                objetivo = sesion.scalar(select(func.max(PrecioWebModel.fecha_extraccion)))
            if objetivo is None:
                return []
            consulta = (select(PrecioWebModel)
                        .where(PrecioWebModel.fecha_extraccion == objetivo)
                        .order_by(PrecioWebModel.libro_id, PrecioWebModel.posicion))
            return [self._a_entidad(modelo) for modelo in sesion.scalars(consulta).all()]
        return self._ejecutar(operacion)

    def _copiar(self, modelo: PrecioWebModel, entidad: PrecioWeb) -> None:
        """Copia los datos de la entidad a un modelo existente."""
        modelo.libro_id = entidad.libro.id
        modelo.titulo_web = entidad.titulo_web
        modelo.isbn_web = entidad.isbn_web
        modelo.url = entidad.url
        modelo.precio = entidad.precio
        modelo.url_imagen = entidad.url_imagen
        modelo.formas_pago = entidad.formas_pago
        modelo.descripcion = entidad.descripcion
        modelo.posicion = entidad.posicion
        modelo.coincide_isbn = entidad.coincide_isbn
        modelo.fecha_extraccion = entidad.fecha_extraccion


class RepositorioAuditoria(RepositorioDB[Auditoria]):
    """Persistencia del historial de auditoría."""

    _MODELO = AuditoriaModel

    def _a_entidad(self, modelo: AuditoriaModel) -> Auditoria:
        """Convierte el modelo de la tabla en la entidad Auditoria."""
        return Auditoria(modelo.id, modelo.accion, modelo.fecha, modelo.detalles)

    def _a_modelo(self, entidad: Auditoria) -> AuditoriaModel:
        """Crea un modelo nuevo a partir de la entidad."""
        return AuditoriaModel(id=entidad.id, accion=entidad.accion, fecha=entidad.fecha,
                              detalles=entidad.detalles)

    def _copiar(self, modelo: AuditoriaModel, entidad: Auditoria) -> None:
        """Copia los datos de la entidad a un modelo existente."""
        modelo.accion = entidad.accion
        modelo.fecha = entidad.fecha
        modelo.detalles = entidad.detalles

    def leer_recientes(self, limite: Optional[int] = None) -> List[Auditoria]:
        """Devuelve las operaciones registradas, de la más reciente a la más antigua.

        Args:
            limite: cantidad máxima de registros. Si no se indica, devuelve todos.
        """
        def operacion(sesion: Session) -> List[Auditoria]:
            """Lee los registros de auditoría, los más recientes primero."""
            consulta = select(AuditoriaModel).order_by(
                AuditoriaModel.fecha.desc(), AuditoriaModel.id.desc())
            if limite is not None:
                consulta = consulta.limit(limite)
            return [self._a_entidad(modelo) for modelo in sesion.scalars(consulta).all()]
        return self._ejecutar(operacion)


class RepositorioStock(_RepositorioBase, IRepositorioStock):
    """Persistencia de stock, un registro por libro (el id del registro es el del libro)."""

    def crear(self, stock: Stock) -> Stock:
        """Guarda el stock de un libro; falla si ese libro ya tiene stock."""
        def operacion(sesion: Session) -> Stock:
            """Inserta el registro de stock dentro de la transacción."""
            if sesion.get(StockModel, stock.libro_id) is not None:
                raise ValueError(f"Ya existe stock para el libro {stock.libro_id}.")
            sesion.add(StockModel(libro_id=stock.libro_id, cantidad=stock.cantidad))
            sesion.flush()
            return stock
        return self._ejecutar(operacion)

    def leer_por_libro(self, libro_id: int) -> Optional[Stock]:
        """Devuelve el stock de un libro, o None si no tiene."""
        def operacion(sesion: Session) -> Optional[Stock]:
            """Busca el stock por id de libro y lo convierte en entidad."""
            modelo = sesion.get(StockModel, libro_id)
            return None if modelo is None else _a_stock(modelo)
        return self._ejecutar(operacion)

    def leer_por_id(self, id: int) -> Optional[Stock]:
        """Lee un stock por su ID, que coincide con el ID del libro."""
        return self.leer_por_libro(id)

    def leer_todos(self) -> List[Stock]:
        """Devuelve el stock de todos los libros, ordenado por libro."""
        def operacion(sesion: Session) -> List[Stock]:
            """Lee todos los registros de stock, ordenados por libro."""
            modelos = sesion.scalars(select(StockModel).order_by(StockModel.libro_id)).all()
            return [_a_stock(modelo) for modelo in modelos]
        return self._ejecutar(operacion)

    def actualizar(self, stock: Stock) -> Stock:
        """Actualiza la cantidad en stock de un libro; falla si no hay stock cargado."""
        def operacion(sesion: Session) -> Stock:
            """Guarda la nueva cantidad en el registro de stock."""
            modelo = sesion.get(StockModel, stock.libro_id)
            if modelo is None:
                raise ValueError(f"No existe stock para el libro {stock.libro_id}.")
            modelo.cantidad = stock.cantidad
            sesion.flush()
            return stock
        return self._ejecutar(operacion)

    def eliminar(self, libro_id: int) -> bool:
        """Elimina el stock de un libro. Devuelve False si no existía."""
        def operacion(sesion: Session) -> bool:
            """Borra el registro de stock si existe."""
            modelo = sesion.get(StockModel, libro_id)
            if modelo is None:
                return False
            sesion.delete(modelo)
            sesion.flush()
            return True
        return self._ejecutar(operacion)


class RepositorioCotizacionDolar(_RepositorioBase, IRepositorioCotizacionDolar):
    """Persistencia del histórico de cotizaciones, identificadas por tipo y fecha."""

    def crear(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        """Guarda una cotización nueva; falla si ya hay una para ese tipo y fecha."""
        def operacion(sesion: Session) -> CotizacionDolar:
            """Inserta la cotización dentro de la transacción."""
            if sesion.get(CotizacionDolarModel,
                          (cotizacion.tipo_id, cotizacion.fecha)) is not None:
                raise ValueError("Ya existe una cotización para ese tipo y fecha.")
            sesion.add(CotizacionDolarModel(
                tipo_id=cotizacion.tipo_id, fecha=cotizacion.fecha,
                valor_compra=cotizacion.valor_compra, valor_venta=cotizacion.valor_venta))
            sesion.flush()
            return cotizacion
        return self._ejecutar(operacion)

    def leer_por_tipo_y_fecha(
            self, tipo_id: int, fecha: datetime.date) -> Optional[CotizacionDolar]:
        """Devuelve la cotización de un tipo en una fecha, o None si no existe."""
        def operacion(sesion: Session) -> Optional[CotizacionDolar]:
            """Busca la cotización por tipo y fecha y la convierte en entidad."""
            modelo = sesion.get(CotizacionDolarModel, (tipo_id, fecha))
            return None if modelo is None else _a_cotizacion(modelo)
        return self._ejecutar(operacion)

    def leer_por_id(self, tipo_id: int, fecha: datetime.date) -> Optional[CotizacionDolar]:
        """Lee una cotización por su ID, que es compuesto: el tipo y la fecha."""
        return self.leer_por_tipo_y_fecha(tipo_id, fecha)

    def leer_historico_por_tipo(self, tipo_id: int) -> List[CotizacionDolar]:
        """Devuelve todas las cotizaciones de un tipo, de la más antigua a la más nueva."""
        def operacion(sesion: Session) -> List[CotizacionDolar]:
            """Lee las cotizaciones del tipo, ordenadas por fecha."""
            consulta = (select(CotizacionDolarModel)
                        .where(CotizacionDolarModel.tipo_id == tipo_id)
                        .order_by(CotizacionDolarModel.fecha))
            return [_a_cotizacion(modelo) for modelo in sesion.scalars(consulta).all()]
        return self._ejecutar(operacion)

    def leer_todos(self) -> List[CotizacionDolar]:
        """Devuelve todas las cotizaciones, ordenadas por tipo y fecha."""
        def operacion(sesion: Session) -> List[CotizacionDolar]:
            """Lee todas las cotizaciones, ordenadas por tipo y fecha."""
            consulta = select(CotizacionDolarModel).order_by(
                CotizacionDolarModel.tipo_id, CotizacionDolarModel.fecha)
            return [_a_cotizacion(modelo) for modelo in sesion.scalars(consulta).all()]
        return self._ejecutar(operacion)

    def actualizar(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        """Actualiza los valores de compra y venta de una cotización existente."""
        def operacion(sesion: Session) -> CotizacionDolar:
            """Guarda los nuevos valores en la cotización existente."""
            modelo = sesion.get(CotizacionDolarModel, (cotizacion.tipo_id, cotizacion.fecha))
            if modelo is None:
                raise ValueError("No existe una cotización para ese tipo y fecha.")
            modelo.valor_compra = cotizacion.valor_compra
            modelo.valor_venta = cotizacion.valor_venta
            sesion.flush()
            return cotizacion
        return self._ejecutar(operacion)

    def eliminar(self, tipo_id: int, fecha: datetime.date) -> bool:
        """Elimina la cotización de un tipo en una fecha. Devuelve False si no existía."""
        def operacion(sesion: Session) -> bool:
            """Borra la cotización si existe."""
            modelo = sesion.get(CotizacionDolarModel, (tipo_id, fecha))
            if modelo is None:
                return False
            sesion.delete(modelo)
            sesion.flush()
            return True
        return self._ejecutar(operacion)
