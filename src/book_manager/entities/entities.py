"""Entidades del dominio de Book Manager."""
import datetime
from decimal import Decimal


def _validar_texto(valor: str, campo: str) -> str:
    """Valida que un valor sea un texto no vacío y lo devuelve sin espacios sobrantes."""
    if not isinstance(valor, str) or not valor.strip():
        raise ValueError(f"{campo} no puede estar vacío.")
    return valor.strip()


def _validar_monto(valor, campo: str) -> Decimal:
    """Convierte a Decimal y valida que el monto no sea negativo."""
    try:
        monto = Decimal(str(valor))
    except Exception as error:
        raise ValueError(f"{campo} debe ser numérico.") from error
    if monto < 0:
        raise ValueError(f"{campo} no puede ser negativo.")
    return monto


class EntidadBase:
    """Clase base de las entidades que se identifican por un ID entero."""

    def __init__(self, id: int) -> None:
        self.id = id

    @property
    def id(self) -> int:
        return self._id

    @id.setter
    def id(self, valor: int) -> None:
        if not isinstance(valor, int) or valor <= 0:
            raise ValueError("El id debe ser un entero positivo.")
        self._id = valor

    def __eq__(self, otro: object) -> bool:
        return type(self) is type(otro) and self._id == otro._id

    def __hash__(self) -> int:
        return hash((type(self).__name__, self._id))


class Genero(EntidadBase):
    """Categoría literaria (novela, ensayo, infantil, técnico, etc.)."""

    def __init__(self, id: int, nombre: str) -> None:
        super().__init__(id)
        self.nombre = nombre

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        self._nombre = _validar_texto(valor, "El nombre del género")

    def __str__(self) -> str:
        return self._nombre


class Editorial(EntidadBase):
    """Proveedor/distribuidora que provee libros a la librería."""

    def __init__(self, id: int, nombre: str, pais: str = "Argentina") -> None:
        super().__init__(id)
        self.nombre = nombre
        self.pais = pais

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        self._nombre = _validar_texto(valor, "El nombre de la editorial")

    @property
    def pais(self) -> str:
        return self._pais

    @pais.setter
    def pais(self, valor: str) -> None:
        self._pais = _validar_texto(valor, "El país")

    def __str__(self) -> str:
        return f"{self._nombre} ({self._pais})"


class Moneda(EntidadBase):
    """Moneda en la que se expresa un precio (ARS, USD, etc.)."""

    def __init__(self, id: int, codigo: str, nombre: str, simbolo: str) -> None:
        super().__init__(id)
        self.codigo = codigo
        self.nombre = nombre
        self.simbolo = simbolo

    @property
    def codigo(self) -> str:
        return self._codigo

    @codigo.setter
    def codigo(self, valor: str) -> None:
        self._codigo = _validar_texto(valor, "El código de moneda").upper()

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        self._nombre = _validar_texto(valor, "El nombre de la moneda")

    @property
    def simbolo(self) -> str:
        return self._simbolo

    @simbolo.setter
    def simbolo(self, valor: str) -> None:
        self._simbolo = _validar_texto(valor, "El símbolo")

    def __str__(self) -> str:
        return f"{self._codigo} ({self._simbolo})"


class TipoCotizacion(EntidadBase):
    """Tipo de cotización del dólar (Oficial, Blue, MEP, etc.)."""

    def __init__(self, id: int, nombre: str) -> None:
        super().__init__(id)
        self.nombre = nombre

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        self._nombre = _validar_texto(valor, "El nombre del tipo de cotización")

    def __str__(self) -> str:
        return self._nombre


class Libro(EntidadBase):
    """Título del catálogo de la librería."""

    def __init__(self, id: int, isbn: str, titulo: str, autor: str,
                 editorial: Editorial, genero: Genero) -> None:
        super().__init__(id)
        self.isbn = isbn
        self.titulo = titulo
        self.autor = autor
        self.editorial = editorial
        self.genero = genero

    @property
    def isbn(self) -> str:
        return self._isbn

    @isbn.setter
    def isbn(self, valor: str) -> None:
        limpio = _validar_texto(valor, "El ISBN").replace("-", "")
        if not limpio.isdigit() or len(limpio) not in (10, 13):
            raise ValueError("El ISBN debe tener 10 o 13 dígitos.")
        self._isbn = limpio

    @property
    def titulo(self) -> str:
        return self._titulo

    @titulo.setter
    def titulo(self, valor: str) -> None:
        self._titulo = _validar_texto(valor, "El título")

    @property
    def autor(self) -> str:
        return self._autor

    @autor.setter
    def autor(self, valor: str) -> None:
        self._autor = _validar_texto(valor, "El autor")

    @property
    def editorial(self) -> Editorial:
        return self._editorial

    @editorial.setter
    def editorial(self, valor: Editorial) -> None:
        if not isinstance(valor, Editorial):
            raise ValueError("La editorial debe ser un objeto Editorial.")
        self._editorial = valor

    @property
    def genero(self) -> Genero:
        return self._genero

    @genero.setter
    def genero(self, valor: Genero) -> None:
        if not isinstance(valor, Genero):
            raise ValueError("El género debe ser un objeto Genero.")
        self._genero = valor

    def __str__(self) -> str:
        return f"{self._titulo} - {self._autor} (ISBN {self._isbn})"


class Precio(EntidadBase):
    """Valor monetario de un libro en una moneda determinada."""

    def __init__(self, id: int, libro: Libro, moneda: Moneda, valor) -> None:
        super().__init__(id)
        self.libro = libro
        self.moneda = moneda
        self.valor = valor

    @property
    def libro(self) -> Libro:
        return self._libro

    @libro.setter
    def libro(self, valor: Libro) -> None:
        if not isinstance(valor, Libro):
            raise ValueError("El libro debe ser un objeto Libro.")
        self._libro = valor

    @property
    def moneda(self) -> Moneda:
        return self._moneda

    @moneda.setter
    def moneda(self, valor: Moneda) -> None:
        if not isinstance(valor, Moneda):
            raise ValueError("La moneda debe ser un objeto Moneda.")
        self._moneda = valor

    @property
    def valor(self) -> Decimal:
        return self._valor

    @valor.setter
    def valor(self, valor) -> None:
        self._valor = _validar_monto(valor, "El valor del precio")

    def __str__(self) -> str:
        return f"{self._moneda.simbolo} {self._valor:.2f}"


class Stock:
    """Cantidad disponible de un libro (un registro por libro)."""

    def __init__(self, libro: Libro, cantidad: int) -> None:
        self.libro = libro
        self.cantidad = cantidad

    @property
    def libro(self) -> Libro:
        return self._libro

    @libro.setter
    def libro(self, valor: Libro) -> None:
        if not isinstance(valor, Libro):
            raise ValueError("El libro debe ser un objeto Libro.")
        self._libro = valor

    @property
    def libro_id(self) -> int:
        return self._libro.id

    @property
    def cantidad(self) -> int:
        return self._cantidad

    @cantidad.setter
    def cantidad(self, valor: int) -> None:
        if not isinstance(valor, int) or valor < 0:
            raise ValueError("La cantidad debe ser un entero mayor o igual a 0.")
        self._cantidad = valor

    def __str__(self) -> str:
        return f"{self._libro.titulo}: {self._cantidad} unidades"


class CotizacionDolar:
    """Registro histórico de la cotización del dólar por tipo y fecha."""

    def __init__(self, tipo: TipoCotizacion, fecha: datetime.date,
                 valor_compra, valor_venta) -> None:
        self.tipo = tipo
        self.fecha = fecha
        self.valor_compra = valor_compra
        self.valor_venta = valor_venta

    @property
    def tipo(self) -> TipoCotizacion:
        return self._tipo

    @tipo.setter
    def tipo(self, valor: TipoCotizacion) -> None:
        if not isinstance(valor, TipoCotizacion):
            raise ValueError("El tipo debe ser un objeto TipoCotizacion.")
        self._tipo = valor

    @property
    def tipo_id(self) -> int:
        return self._tipo.id

    @property
    def fecha(self) -> datetime.date:
        return self._fecha

    @fecha.setter
    def fecha(self, valor: datetime.date) -> None:
        if not isinstance(valor, datetime.date):
            raise ValueError("La fecha debe ser un objeto date.")
        self._fecha = valor

    @property
    def valor_compra(self) -> Decimal:
        return self._valor_compra

    @valor_compra.setter
    def valor_compra(self, valor) -> None:
        self._valor_compra = _validar_monto(valor, "El valor de compra")

    @property
    def valor_venta(self) -> Decimal:
        return self._valor_venta

    @valor_venta.setter
    def valor_venta(self, valor) -> None:
        self._valor_venta = _validar_monto(valor, "El valor de venta")

    def __str__(self) -> str:
        return (f"{self._tipo} {self._fecha}: compra {self._valor_compra} / "
                f"venta {self._valor_venta}")
