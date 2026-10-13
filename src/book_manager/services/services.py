"""Servicios con la lógica de negocio de Book Manager."""
import abc
import datetime
import os
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from typing import Dict, Generic, List, Optional, Tuple, TypeVar

import requests

from book_manager.database.connection import cargar_variables_entorno
from book_manager.entities.entities import (
    CotizacionDolar, Editorial, EntidadBase, Genero, Libro, Moneda,
    Precio, Stock, TipoCotizacion)
from book_manager.repositories.repositories import (
    RepositorioCotizacionDolar, RepositorioDB, RepositorioEditorial,
    RepositorioGenero, RepositorioLibro, RepositorioMoneda, RepositorioPrecio,
    RepositorioStock, RepositorioTipoCotizacion)

T = TypeVar('T', bound=EntidadBase)

CODIGO_ARS = "ARS"
CODIGO_USD = "USD"


class ServicioBase(Generic[T]):
    """CRUD común a los servicios de entidades con id propio."""

    def __init__(self, repositorio: RepositorioDB[T]) -> None:
        self._repositorio = repositorio

    def listar(self) -> List[T]:
        """Devuelve todas las entidades."""
        return self._repositorio.leer_todos()

    def _obtener_por_id(self, id: int) -> T:
        """Uso interno: devuelve la entidad o lanza ValueError si no existe."""
        entidad = self._repositorio.leer_por_id(id)
        if entidad is None:
            raise ValueError(f"No existe la entidad con id {id}.")
        return entidad

    def modificar(self, entidad: T) -> T:
        """Persiste los cambios de una entidad existente."""
        self._obtener_por_id(entidad.id)
        return self._repositorio.actualizar(entidad)

    def eliminar(self, entidad: T) -> None:
        """Elimina la entidad si ninguna otra la está usando."""
        self._obtener_por_id(entidad.id)
        self._validar_eliminacion(entidad)
        self._repositorio.eliminar(entidad.id)

    def _validar_eliminacion(self, entidad: T) -> None:
        """Punto de extensión: lanza ValueError si la entidad no puede borrarse."""

    def _validar_nombre_unico(self, nombre: str, id_actual: Optional[int] = None) -> None:
        """Evita nombres repetidos (sin distinguir mayúsculas)."""
        for existente in self._repositorio.leer_todos():
            if existente.nombre.lower() == nombre.strip().lower() and existente.id != id_actual:
                raise ValueError(f"Ya existe '{nombre}'.")


class GeneroService(ServicioBase[Genero]):
    """Lógica de géneros literarios."""

    def __init__(self, repositorio: RepositorioGenero, repo_libro: RepositorioLibro) -> None:
        super().__init__(repositorio)
        self._repo_libro = repo_libro

    def crear(self, nombre: str) -> Genero:
        self._validar_nombre_unico(nombre)
        genero = Genero(self._repositorio.siguiente_id(), nombre)
        return self._repositorio.crear(genero)

    def modificar(self, genero: Genero) -> Genero:
        self._validar_nombre_unico(genero.nombre, genero.id)
        return super().modificar(genero)

    def _validar_eliminacion(self, entidad: Genero) -> None:
        if any(libro.genero == entidad for libro in self._repo_libro.leer_todos()):
            raise ValueError("No se puede eliminar: hay libros con este género.")


class EditorialService(ServicioBase[Editorial]):
    """Lógica de editoriales."""

    def __init__(self, repositorio: RepositorioEditorial, repo_libro: RepositorioLibro) -> None:
        super().__init__(repositorio)
        self._repo_libro = repo_libro

    def crear(self, nombre: str, pais: str = "Argentina") -> Editorial:
        self._validar_nombre_unico(nombre)
        editorial = Editorial(self._repositorio.siguiente_id(), nombre, pais)
        return self._repositorio.crear(editorial)

    def modificar(self, editorial: Editorial) -> Editorial:
        self._validar_nombre_unico(editorial.nombre, editorial.id)
        return super().modificar(editorial)

    def _validar_eliminacion(self, entidad: Editorial) -> None:
        if any(libro.editorial == entidad for libro in self._repo_libro.leer_todos()):
            raise ValueError("No se puede eliminar: hay libros de esta editorial.")


class MonedaService(ServicioBase[Moneda]):
    """Lógica de monedas."""

    def __init__(self, repositorio: RepositorioMoneda, repo_precio: RepositorioPrecio) -> None:
        super().__init__(repositorio)
        self._repo_precio = repo_precio

    def crear(self, codigo: str, nombre: str, simbolo: str) -> Moneda:
        for existente in self._repositorio.leer_todos():
            if existente.codigo == codigo.strip().upper():
                raise ValueError(f"Ya existe la moneda {codigo}.")
        moneda = Moneda(self._repositorio.siguiente_id(), codigo, nombre, simbolo)
        return self._repositorio.crear(moneda)

    def obtener_por_codigo(self, codigo: str) -> Moneda:
        """Busca una moneda por su código (ARS, USD...)."""
        for moneda in self._repositorio.leer_todos():
            if moneda.codigo == codigo.upper():
                return moneda
        raise ValueError(f"No existe la moneda {codigo}.")

    def _validar_eliminacion(self, entidad: Moneda) -> None:
        if any(precio.moneda == entidad for precio in self._repo_precio.leer_todos()):
            raise ValueError("No se puede eliminar: hay precios en esta moneda.")


class TipoCotizacionService(ServicioBase[TipoCotizacion]):
    """Lógica de tipos de cotización del dólar."""

    def __init__(self, repositorio: RepositorioTipoCotizacion,
                 repo_cotizacion: RepositorioCotizacionDolar) -> None:
        super().__init__(repositorio)
        self._repo_cotizacion = repo_cotizacion

    def crear(self, nombre: str) -> TipoCotizacion:
        self._validar_nombre_unico(nombre)
        tipo = TipoCotizacion(self._repositorio.siguiente_id(), nombre)
        return self._repositorio.crear(tipo)

    def modificar(self, tipo: TipoCotizacion) -> TipoCotizacion:
        self._validar_nombre_unico(tipo.nombre, tipo.id)
        return super().modificar(tipo)

    def _validar_eliminacion(self, entidad: TipoCotizacion) -> None:
        if self._repo_cotizacion.leer_historico_por_tipo(entidad.id):
            raise ValueError("No se puede eliminar: tiene cotizaciones registradas.")


class LibroService(ServicioBase[Libro]):
    """Lógica de libros."""

    def __init__(self, repositorio: RepositorioLibro, repo_precio: RepositorioPrecio,
                 repo_stock: RepositorioStock) -> None:
        super().__init__(repositorio)
        self._repo_precio = repo_precio
        self._repo_stock = repo_stock

    def _validar_isbn_unico(self, isbn: str, id_actual: Optional[int] = None) -> None:
        limpio = isbn.replace("-", "").strip()
        for existente in self._repositorio.leer_todos():
            if existente.isbn == limpio and existente.id != id_actual:
                raise ValueError(f"Ya existe un libro con el ISBN {isbn}.")

    def crear(self, isbn: str, titulo: str, autor: str,
              editorial: Editorial, genero: Genero) -> Libro:
        self._validar_isbn_unico(isbn)
        libro = Libro(self._repositorio.siguiente_id(), isbn, titulo, autor, editorial, genero)
        return self._repositorio.crear(libro)

    def modificar(self, libro: Libro) -> Libro:
        self._validar_isbn_unico(libro.isbn, libro.id)
        return super().modificar(libro)

    def buscar(self, texto: str) -> List[Libro]:
        """Busca libros por título o autor (sin distinguir mayúsculas)."""
        texto = texto.strip().lower()
        return [libro for libro in self._repositorio.leer_todos()
                if texto in libro.titulo.lower() or texto in libro.autor.lower()]

    def eliminar(self, libro: Libro) -> None:
        """Elimina el libro junto con sus precios y su stock."""
        self._obtener_por_id(libro.id)
        for precio in self._repo_precio.leer_todos():
            if precio.libro == libro:
                self._repo_precio.eliminar(precio.id)
        self._repo_stock.eliminar(libro.id)
        self._repositorio.eliminar(libro.id)


class IProveedorCotizacion(abc.ABC):
    """Fuente externa de cotizaciones del dólar."""

    @abc.abstractmethod
    def obtener_todas(self) -> List[Dict[str, object]]:
        """Devuelve todas las cotizaciones disponibles.

        Cada una es un diccionario con las claves 'casa', 'nombre', 'compra', 'venta' y
        'fechaActualizacion'.
        """


class DolarApiProveedor(IProveedorCotizacion):
    """Obtiene las cotizaciones en tiempo real desde la API configurada en el .env."""

    def __init__(self, url: Optional[str] = None) -> None:
        """Args:
            url: dirección de la API. Si no se indica, se lee API_URL del .env.
        """
        self._url = url

    def _direccion(self) -> str:
        cargar_variables_entorno()
        url = self._url or os.getenv("API_URL")
        if not url:
            raise ValueError("Falta API_URL: definila en el archivo .env.")
        return url

    def obtener_todas(self) -> List[Dict[str, object]]:
        respuesta = requests.get(self._direccion(), timeout=10)
        respuesta.raise_for_status()
        datos = respuesta.json()
        if not isinstance(datos, list):
            raise ValueError("La API devolvió un formato inesperado.")
        return datos


class ServicioCotizacionDolar:
    """Lógica de cotizaciones del dólar."""

    # Identificador que usa la API ("casa") -> nombre del tipo de cotización en el sistema.
    TIPOS_POR_CASA = {
        "oficial": "Oficial", "blue": "Blue", "bolsa": "MEP", "contadoconliqui": "CCL",
        "mayorista": "Mayorista", "tarjeta": "Tarjeta", "cripto": "Cripto"}

    # Argentina no tiene horario de verano: la hora local es siempre UTC-3.
    _ZONA_ARGENTINA = datetime.timezone(datetime.timedelta(hours=-3))

    def __init__(self, repositorio: RepositorioCotizacionDolar,
                 repo_tipo: RepositorioTipoCotizacion,
                 proveedor: IProveedorCotizacion) -> None:
        self._repositorio = repositorio
        self._repo_tipo = repo_tipo
        self._proveedor = proveedor

    def registrar(self, tipo: TipoCotizacion, fecha: datetime.date,
                  valor_compra, valor_venta) -> CotizacionDolar:
        """Registra manualmente una cotización."""
        cotizacion = CotizacionDolar(tipo, fecha, valor_compra, valor_venta)
        return self._repositorio.crear(cotizacion)

    def modificar(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        return self._repositorio.actualizar(cotizacion)

    def eliminar(self, tipo: TipoCotizacion, fecha: datetime.date) -> bool:
        return self._repositorio.eliminar(tipo.id, fecha)

    def historico(self, tipo: TipoCotizacion) -> List[CotizacionDolar]:
        """Cotizaciones de un tipo, de la más antigua a la más reciente."""
        return self._repositorio.leer_historico_por_tipo(tipo.id)

    def listar(self) -> List[CotizacionDolar]:
        return self._repositorio.leer_todos()

    def ultima(self, tipo: TipoCotizacion) -> Optional[CotizacionDolar]:
        """Cotización más reciente de un tipo, o None si no hay."""
        historico = self.historico(tipo)
        return historico[-1] if historico else None

    @classmethod
    def _fecha_de(cls, texto: object) -> datetime.date:
        """Fecha local (Argentina) de la actualización. Si no se puede leer, la de hoy."""
        try:
            momento = datetime.datetime.fromisoformat(str(texto).replace("Z", "+00:00"))
        except ValueError:
            return datetime.date.today()
        if momento.tzinfo is None:
            return momento.date()
        return momento.astimezone(cls._ZONA_ARGENTINA).date()

    @classmethod
    def _interpretar(cls, dato: Dict[str, object]) -> Tuple[str, datetime.date, Decimal, Decimal]:
        """Convierte un elemento de la respuesta en (tipo, fecha, compra, venta).

        Si la API no informa el valor de compra, se toma el de venta.
        """
        try:
            casa = str(dato["casa"]).lower()
            nombre = cls.TIPOS_POR_CASA.get(casa) or str(dato.get("nombre") or casa)
            venta = Decimal(str(dato["venta"]))
            compra = venta if dato.get("compra") is None else Decimal(str(dato["compra"]))
        except (KeyError, TypeError, InvalidOperation) as error:
            raise ValueError(
                f"La API devolvió una cotización con formato inesperado: {dato}") from error
        if compra < 0 or venta < 0:
            raise ValueError(f"La API devolvió una cotización con valores negativos: {dato}")
        return nombre, cls._fecha_de(dato.get("fechaActualizacion")), compra, venta

    def obtener_cotizaciones(self) -> List[CotizacionDolar]:
        """Busca las cotizaciones del dólar en la API, las descarga y las registra en la base.

        Por cada cotización recibida: si ya hay una para ese tipo y fecha, se actualiza; si
        no, se crea. Si el tipo de cotización no existe, también se crea. Se puede repetir
        sin duplicar registros. Los datos se validan todos antes de escribir en la base.

        Returns:
            Las cotizaciones registradas.

        Raises:
            requests.RequestException: si falla la conexión con la API.
            ValueError: si falta API_URL o la respuesta no es válida.
        """
        datos = [self._interpretar(dato) for dato in self._proveedor.obtener_todas()]
        if not datos:
            raise ValueError("La API no devolvió cotizaciones.")
        tipos = {tipo.nombre.lower(): tipo for tipo in self._repo_tipo.leer_todos()}
        registradas = []
        for nombre, fecha, compra, venta in datos:
            tipo = tipos.get(nombre.lower())
            if tipo is None:
                tipo = self._repo_tipo.crear(
                    TipoCotizacion(self._repo_tipo.siguiente_id(), nombre))
                tipos[nombre.lower()] = tipo
            existente = self._repositorio.leer_por_tipo_y_fecha(tipo.id, fecha)
            if existente is None:
                registradas.append(
                    self._repositorio.crear(CotizacionDolar(tipo, fecha, compra, venta)))
            else:
                existente.valor_compra = compra
                existente.valor_venta = venta
                registradas.append(self._repositorio.actualizar(existente))
        return registradas


class PrecioService(ServicioBase[Precio]):
    """Lógica de precios y cotización de libros."""

    def __init__(self, repositorio: RepositorioPrecio,
                 servicio_cotizacion: ServicioCotizacionDolar) -> None:
        super().__init__(repositorio)
        self._servicio_cotizacion = servicio_cotizacion

    def precios_de_libro(self, libro: Libro) -> List[Precio]:
        """Todos los precios cargados para un libro."""
        return [precio for precio in self._repositorio.leer_todos() if precio.libro == libro]

    def crear(self, libro: Libro, moneda: Moneda, valor) -> Precio:
        if any(precio.moneda == moneda for precio in self.precios_de_libro(libro)):
            raise ValueError(f"El libro ya tiene un precio en {moneda.codigo}.")
        precio = Precio(self._repositorio.siguiente_id(), libro, moneda, valor)
        return self._repositorio.crear(precio)

    def cotizar_en_pesos(self, libro: Libro, tipo: TipoCotizacion) -> Decimal:
        """Precio del libro en ARS. Si está en USD lo convierte con la última venta del tipo."""
        precios = self.precios_de_libro(libro)
        en_usd = next((p for p in precios if p.moneda.codigo == CODIGO_USD), None)
        if en_usd is not None:
            cotizacion = self._servicio_cotizacion.ultima(tipo)
            if cotizacion is None:
                raise ValueError(f"No hay cotización registrada para {tipo.nombre}.")
            pesos = en_usd.valor * cotizacion.valor_venta
            return pesos.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        en_ars = next((p for p in precios if p.moneda.codigo == CODIGO_ARS), None)
        if en_ars is not None:
            return en_ars.valor
        raise ValueError(f"El libro '{libro.titulo}' no tiene precio en USD ni en ARS.")


class StockService:
    """Lógica de stock, un registro por libro."""

    def __init__(self, repositorio: RepositorioStock) -> None:
        self._repositorio = repositorio

    def crear(self, libro: Libro, cantidad: int) -> Stock:
        return self._repositorio.crear(Stock(libro, cantidad))

    def listar(self) -> List[Stock]:
        return self._repositorio.leer_todos()

    def obtener(self, libro: Libro) -> Stock:
        stock = self._repositorio.leer_por_libro(libro.id)
        if stock is None:
            raise ValueError(f"El libro '{libro.titulo}' no tiene stock cargado.")
        return stock

    def modificar(self, stock: Stock) -> Stock:
        return self._repositorio.actualizar(stock)

    def ajustar(self, libro: Libro, delta: int) -> Stock:
        """Suma o resta unidades; no permite quedar con stock negativo."""
        stock = self.obtener(libro)
        if stock.cantidad + delta < 0:
            raise ValueError(f"Stock insuficiente: hay {stock.cantidad} unidades.")
        stock.cantidad = stock.cantidad + delta
        return self._repositorio.actualizar(stock)

    def eliminar(self, libro: Libro) -> bool:
        return self._repositorio.eliminar(libro.id)

    def con_stock_bajo(self, umbral: int = 5) -> List[Stock]:
        """Libros con una cantidad menor o igual al umbral."""
        return [stock for stock in self._repositorio.leer_todos() if stock.cantidad <= umbral]
