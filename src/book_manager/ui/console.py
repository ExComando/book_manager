"""Interfaz de consola (CLI) de Book Manager."""
import datetime
from decimal import Decimal, InvalidOperation
from typing import Callable, Dict, Optional, Sequence, Tuple, TypeVar

import requests

from book_manager.entities.entities import CotizacionDolar, Libro, Precio, Stock
from book_manager.services.services import (
    ServicioAuditoria, ServicioCotizacionDolar, ServicioEditorial, ServicioGenero,
    ServicioLibro, ServicioMoneda, ServicioPrecio, ServicioScraping, ServicioStock,
    ServicioTipoCotizacion, auditar)

T = TypeVar("T")
Opcion = Tuple[str, Callable[[], object]]
LIMITE_HISTORIAL = 100  # cuántas operaciones muestra "Ver historial de auditoría"


# ---------------------------------------------------------------- entrada de datos
def pedir_texto(mensaje: str, actual: Optional[str] = None) -> str:
    """Pide un texto no vacío. Si hay valor actual, Enter lo conserva."""
    sufijo = f" [{actual}]" if actual is not None else ""
    while True:
        valor = input(f"{mensaje}{sufijo}: ").strip()
        if valor:
            return valor
        if actual is not None:
            return actual
        print("El valor no puede estar vacío.")


def pedir_entero(mensaje: str, actual: Optional[int] = None,
                 minimo: Optional[int] = 0) -> int:
    """Pide un entero. Si hay valor actual, Enter lo conserva."""
    sufijo = f" [{actual}]" if actual is not None else ""
    while True:
        valor = input(f"{mensaje}{sufijo}: ").strip()
        if not valor and actual is not None:
            return actual
        try:
            numero = int(valor)
        except ValueError:
            print("Ingresá un número entero.")
            continue
        if minimo is not None and numero < minimo:
            print(f"Debe ser mayor o igual a {minimo}.")
            continue
        return numero


def pedir_decimal(mensaje: str, actual: Optional[Decimal] = None) -> Decimal:
    """Pide un monto decimal no negativo. Si hay valor actual, Enter lo conserva."""
    sufijo = f" [{actual}]" if actual is not None else ""
    while True:
        valor = input(f"{mensaje}{sufijo}: ").strip().replace(",", ".")
        if not valor and actual is not None:
            return actual
        try:
            monto = Decimal(valor)
        except InvalidOperation:
            print("Ingresá un número (ej. 1450.50).")
            continue
        if monto < 0:
            print("No puede ser negativo.")
            continue
        return monto


def pedir_fecha(mensaje: str, por_defecto: datetime.date) -> datetime.date:
    """Pide una fecha AAAA-MM-DD. Enter usa el valor por defecto."""
    while True:
        valor = input(f"{mensaje} (AAAA-MM-DD) [{por_defecto}]: ").strip()
        if not valor:
            return por_defecto
        try:
            return datetime.date.fromisoformat(valor)
        except ValueError:
            print("Formato inválido. Ejemplo: 2026-10-07.")


def confirmar(mensaje: str) -> bool:
    """Pide confirmación (s/n)."""
    return input(f"{mensaje} (s/n): ").strip().lower() in ("s", "si", "sí")


def elegir(titulo: str, opciones: Sequence[T], describir: Callable[[T], str]) -> T:
    """Muestra una lista numerada y devuelve el objeto elegido (0 cancela)."""
    if not opciones:
        raise ValueError(f"No hay {titulo.lower()} cargados.")
    print(f"\nElegí {titulo.lower()}:")
    for posicion, opcion in enumerate(opciones, start=1):
        print(f"  {posicion}. {describir(opcion)}")
    while True:
        numero = pedir_entero("Número (0 para cancelar)")
        if numero == 0:
            raise ValueError("Operación cancelada.")
        if numero <= len(opciones):
            return opciones[numero - 1]
        print("Número fuera de rango.")


# ---------------------------------------------------------------- descripciones
def _describir_libro(libro: Libro) -> str:
    """Resume un libro en una línea: título, autor, editorial, género e ISBN."""
    return (f"{libro.titulo} - {libro.autor} | {libro.editorial.nombre} | "
            f"{libro.genero.nombre} | ISBN {libro.isbn}")


def _describir_precio(precio: Precio) -> str:
    """Resume un precio en una línea: libro, símbolo, valor y código de moneda."""
    return (f"{precio.libro.titulo}: {precio.moneda.simbolo} {precio.valor:,.2f} "
            f"({precio.moneda.codigo})")


def _describir_stock(stock: Stock) -> str:
    """Resume el stock en una línea: libro y unidades disponibles."""
    return f"{stock.libro.titulo}: {stock.cantidad} unidades"


def _describir_cotizacion(cotizacion: CotizacionDolar) -> str:
    """Resume una cotización en una línea: tipo, fecha, compra y venta."""
    return (f"{cotizacion.tipo.nombre} {cotizacion.fecha}: "
            f"compra ${cotizacion.valor_compra:,.2f} / venta ${cotizacion.valor_venta:,.2f}")


class Consola:
    """Menús de consola que operan el CRUD de cada entidad a través de los servicios."""

    def __init__(self, generos: ServicioGenero, editoriales: ServicioEditorial,
                 monedas: ServicioMoneda, tipos: ServicioTipoCotizacion,
                 libros: ServicioLibro, precios: ServicioPrecio,
                 stock: ServicioStock, cotizaciones: ServicioCotizacionDolar,
                 scraping: ServicioScraping, auditoria: ServicioAuditoria) -> None:
        """Guarda los servicios con los que el menú realiza todas las operaciones."""
        self._generos = generos
        self._editoriales = editoriales
        self._monedas = monedas
        self._tipos = tipos
        self._libros = libros
        self._precios = precios
        self._stock = stock
        self._cotizaciones = cotizaciones
        self._scraping = scraping
        self._auditoria = auditoria

    # ------------------------------------------------------------ menús
    @staticmethod
    def _menu(titulo: str, opciones: Sequence[Opcion], salir: str = "Volver") -> None:
        """Muestra un menú y ejecuta la opción elegida hasta que se elige salir."""
        while True:
            print(f"\n=== {titulo} ===")
            for numero, (texto, _) in enumerate(opciones, start=1):
                print(f"{numero}. {texto}")
            print(f"0. {salir}")
            eleccion = input("Opción: ").strip()
            if eleccion == "0":
                return
            if not (eleccion.isdigit() and 1 <= int(eleccion) <= len(opciones)):
                print("Opción inválida.")
                continue
            try:
                opciones[int(eleccion) - 1][1]()
            except ValueError as error:
                print(f"Aviso: {error}")
            except requests.RequestException as error:
                print(f"Aviso: no se pudo consultar la cotización ({error}).")

    def ejecutar(self) -> None:
        """Menú principal."""
        self._menu("BOOK MANAGER", [
            ("Libros", self._menu_libros),
            ("Géneros", self._menu_generos),
            ("Editoriales", self._menu_editoriales),
            ("Monedas", self._menu_monedas),
            ("Tipos de cotización", self._menu_tipos),
            ("Precios", self._menu_precios),
            ("Stock", self._menu_stock),
            ("Cotizaciones del dólar", self._menu_cotizaciones),
            ("Reportes", self._menu_reportes),
            ("Obtener las cotizaciones por API", self._actualizar_cotizacion),
            ("Lista de precios bimonetaria", self._lista_bimonetaria),
            ("Exportar los precios a CSV", self._exportar_precios),
            ("Ejecutar scraping", self._ejecutar_scraping),
            ("Generar reporte", self._generar_reporte),
            ("Ver historial de auditoría", self._ver_historial),
        ], salir="Salir")
        print("¡Hasta luego!")

    @staticmethod
    @auditar("Listar {titulo}",
             detalle=lambda argumentos, resultado: f"{len(argumentos['items'])} registros")
    def _listar(titulo: str, items: Sequence[T], describir: Callable[[T], str]) -> None:
        """Imprime un listado numerado."""
        print(f"\n--- {titulo} ({len(items)}) ---")
        for posicion, item in enumerate(items, start=1):
            print(f"{posicion}. {describir(item)}")

    def _baja(self, servicio, titulo: str, describir: Callable[[T], str]) -> None:
        """Baja genérica: elige una entidad, confirma y elimina."""
        entidad = elegir(titulo, servicio.listar(), describir)
        if confirmar(f"¿Eliminar '{describir(entidad)}'?"):
            servicio.eliminar(entidad)
            print("Eliminado.")

    # ------------------------------------------------------------ géneros
    def _menu_generos(self) -> None:
        """Submenú de géneros: listar, alta, modificación y baja."""
        self._menu("GÉNEROS", [
            ("Listar", lambda: self._listar("Géneros", self._generos.listar(), str)),
            ("Alta", self._alta_genero),
            ("Modificar", self._modificar_genero),
            ("Baja", lambda: self._baja(self._generos, "Géneros", str)),
        ])

    def _alta_genero(self) -> None:
        """Pide el nombre y da de alta un género."""
        genero = self._generos.crear(pedir_texto("Nombre del género"))
        print(f"Creado: {genero}")

    def _modificar_genero(self) -> None:
        """Elige un género y modifica su nombre."""
        genero = elegir("Géneros", self._generos.listar(), str)
        genero.nombre = pedir_texto("Nombre", genero.nombre)
        self._generos.modificar(genero)
        print("Modificado.")

    # ------------------------------------------------------------ editoriales
    def _menu_editoriales(self) -> None:
        """Submenú de editoriales: listar, alta, modificación y baja."""
        self._menu("EDITORIALES", [
            ("Listar", lambda: self._listar("Editoriales", self._editoriales.listar(), str)),
            ("Alta", self._alta_editorial),
            ("Modificar", self._modificar_editorial),
            ("Baja", lambda: self._baja(self._editoriales, "Editoriales", str)),
        ])

    def _alta_editorial(self) -> None:
        """Pide el nombre y el país y da de alta una editorial."""
        nombre = pedir_texto("Nombre de la editorial")
        pais = pedir_texto("País", "Argentina")
        print(f"Creada: {self._editoriales.crear(nombre, pais)}")

    def _modificar_editorial(self) -> None:
        """Elige una editorial y modifica su nombre y su país."""
        editorial = elegir("Editoriales", self._editoriales.listar(), str)
        editorial.nombre = pedir_texto("Nombre", editorial.nombre)
        editorial.pais = pedir_texto("País", editorial.pais)
        self._editoriales.modificar(editorial)
        print("Modificada.")

    # ------------------------------------------------------------ monedas
    def _menu_monedas(self) -> None:
        """Submenú de monedas: listar, alta, modificación y baja."""
        self._menu("MONEDAS", [
            ("Listar", lambda: self._listar("Monedas", self._monedas.listar(),
                                            lambda m: f"{m} - {m.nombre}")),
            ("Alta", self._alta_moneda),
            ("Modificar", self._modificar_moneda),
            ("Baja", lambda: self._baja(self._monedas, "Monedas", str)),
        ])

    def _alta_moneda(self) -> None:
        """Pide código, nombre y símbolo y da de alta una moneda."""
        codigo = pedir_texto("Código (ej. USD)")
        nombre = pedir_texto("Nombre")
        simbolo = pedir_texto("Símbolo")
        print(f"Creada: {self._monedas.crear(codigo, nombre, simbolo)}")

    def _modificar_moneda(self) -> None:
        """Elige una moneda y modifica su nombre y su símbolo (el código no se cambia)."""
        moneda = elegir("Monedas", self._monedas.listar(), str)
        moneda.nombre = pedir_texto("Nombre", moneda.nombre)
        moneda.simbolo = pedir_texto("Símbolo", moneda.simbolo)
        self._monedas.modificar(moneda)
        print("Modificada. (El código no se modifica.)")

    # ------------------------------------------------------------ tipos de cotización
    def _menu_tipos(self) -> None:
        """Submenú de tipos de cotización: listar, alta, modificación y baja."""
        self._menu("TIPOS DE COTIZACIÓN", [
            ("Listar", lambda: self._listar("Tipos de cotización", self._tipos.listar(), str)),
            ("Alta", self._alta_tipo),
            ("Modificar", self._modificar_tipo),
            ("Baja", lambda: self._baja(self._tipos, "Tipos de cotización", str)),
        ])

    def _alta_tipo(self) -> None:
        """Pide el nombre y da de alta un tipo de cotización."""
        print(f"Creado: {self._tipos.crear(pedir_texto('Nombre del tipo'))}")

    def _modificar_tipo(self) -> None:
        """Elige un tipo de cotización y modifica su nombre."""
        tipo = elegir("Tipos de cotización", self._tipos.listar(), str)
        tipo.nombre = pedir_texto("Nombre", tipo.nombre)
        self._tipos.modificar(tipo)
        print("Modificado.")

    # ------------------------------------------------------------ libros
    def _menu_libros(self) -> None:
        """Submenú de libros: listar, alta, modificación, baja y búsqueda por título o autor."""
        self._menu("LIBROS", [
            ("Listar", lambda: self._listar("Libros", self._libros.listar(), _describir_libro)),
            ("Alta", self._alta_libro),
            ("Modificar", self._modificar_libro),
            ("Baja (borra también precios y stock)",
             lambda: self._baja(self._libros, "Libros", _describir_libro)),
            ("Buscar por título o autor", self._buscar_libro),
        ])

    def _alta_libro(self) -> None:
        """Pide ISBN, título, autor, editorial y género, y da de alta un libro."""
        isbn = pedir_texto("ISBN (10 o 13 dígitos)")
        titulo = pedir_texto("Título")
        autor = pedir_texto("Autor")
        editorial = elegir("Editoriales", self._editoriales.listar(), str)
        genero = elegir("Géneros", self._generos.listar(), str)
        print(f"Creado: {self._libros.crear(isbn, titulo, autor, editorial, genero)}")

    def _modificar_libro(self) -> None:
        """Elige un libro y modifica sus datos; cambia editorial y género solo si se confirma."""
        libro = elegir("Libros", self._libros.listar(), _describir_libro)
        libro.isbn = pedir_texto("ISBN", libro.isbn)
        libro.titulo = pedir_texto("Título", libro.titulo)
        libro.autor = pedir_texto("Autor", libro.autor)
        if confirmar(f"¿Cambiar la editorial ({libro.editorial.nombre})?"):
            libro.editorial = elegir("Editoriales", self._editoriales.listar(), str)
        if confirmar(f"¿Cambiar el género ({libro.genero.nombre})?"):
            libro.genero = elegir("Géneros", self._generos.listar(), str)
        self._libros.modificar(libro)
        print("Modificado.")

    def _buscar_libro(self) -> None:
        """Busca libros por título o autor y muestra los resultados."""
        resultados = self._libros.buscar(pedir_texto("Texto a buscar"))
        self._listar("Resultados", resultados, _describir_libro)

    # ------------------------------------------------------------ precios
    def _menu_precios(self) -> None:
        """Submenú de precios: listar, alta, modificación y baja."""
        self._menu("PRECIOS", [
            ("Listar", lambda: self._listar("Precios", self._precios.listar(), _describir_precio)),
            ("Alta", self._alta_precio),
            ("Modificar", self._modificar_precio),
            ("Baja", lambda: self._baja(self._precios, "Precios", _describir_precio)),
        ])

    def _alta_precio(self) -> None:
        """Elige un libro y una moneda, pide el valor y da de alta el precio."""
        libro = elegir("Libros", self._libros.listar(), _describir_libro)
        moneda = elegir("Monedas", self._monedas.listar(), str)
        valor = pedir_decimal(f"Precio en {moneda.codigo}")
        print(f"Creado: {self._precios.crear(libro, moneda, valor)}")

    def _modificar_precio(self) -> None:
        """Elige un precio y modifica su valor."""
        precio = elegir("Precios", self._precios.listar(), _describir_precio)
        precio.valor = pedir_decimal("Nuevo valor", precio.valor)
        self._precios.modificar(precio)
        print("Modificado.")

    # ------------------------------------------------------------ stock
    def _menu_stock(self) -> None:
        """Submenú de stock: listar, alta, modificación, ajuste y baja."""
        self._menu("STOCK", [
            ("Listar", lambda: self._listar("Stock", self._stock.listar(), _describir_stock)),
            ("Alta", self._alta_stock),
            ("Modificar cantidad", self._modificar_stock),
            ("Ajustar (sumar o restar unidades)", self._ajustar_stock),
            ("Baja", self._baja_stock),
        ])

    def _alta_stock(self) -> None:
        """Elige un libro y da de alta su stock con la cantidad inicial."""
        libro = elegir("Libros", self._libros.listar(), _describir_libro)
        cantidad = pedir_entero("Cantidad inicial")
        print(f"Creado: {self._stock.crear(libro, cantidad)}")

    def _modificar_stock(self) -> None:
        """Elige un registro de stock y modifica su cantidad."""
        stock = elegir("Stock", self._stock.listar(), _describir_stock)
        stock.cantidad = pedir_entero("Nueva cantidad", stock.cantidad)
        self._stock.modificar(stock)
        print("Modificado.")

    def _ajustar_stock(self) -> None:
        """Elige un registro de stock y le suma o le resta unidades."""
        stock = elegir("Stock", self._stock.listar(), _describir_stock)
        delta = pedir_entero("Unidades a sumar (negativo para restar)", minimo=None)
        print(f"Resultado: {self._stock.ajustar(stock.libro, delta)}")

    def _baja_stock(self) -> None:
        """Elige un registro de stock y lo elimina si se confirma."""
        stock = elegir("Stock", self._stock.listar(), _describir_stock)
        if confirmar(f"¿Eliminar el stock de '{stock.libro.titulo}'?"):
            self._stock.eliminar(stock.libro)
            print("Eliminado.")

    # ------------------------------------------------------------ cotizaciones
    def _menu_cotizaciones(self) -> None:
        """Submenú de cotizaciones: listar, alta manual, modificación, baja y obtención por API."""
        self._menu("COTIZACIONES DEL DÓLAR", [
            ("Listar", lambda: self._listar("Cotizaciones", self._cotizaciones.listar(),
                                            _describir_cotizacion)),
            ("Alta manual", self._alta_cotizacion),
            ("Modificar", self._modificar_cotizacion),
            ("Baja", self._baja_cotizacion),
            ("Obtener cotizaciones por API (dolarapi.com)", self._actualizar_cotizacion),
        ])

    def _alta_cotizacion(self) -> None:
        """Pide tipo, fecha, compra y venta y registra una cotización a mano."""
        tipo = elegir("Tipos de cotización", self._tipos.listar(), str)
        fecha = pedir_fecha("Fecha", datetime.date.today())
        compra = pedir_decimal("Valor de compra")
        venta = pedir_decimal("Valor de venta")
        print(f"Creada: {self._cotizaciones.registrar(tipo, fecha, compra, venta)}")

    def _modificar_cotizacion(self) -> None:
        """Elige una cotización y modifica sus valores de compra y venta."""
        cotizacion = elegir("Cotizaciones", self._cotizaciones.listar(), _describir_cotizacion)
        cotizacion.valor_compra = pedir_decimal("Compra", cotizacion.valor_compra)
        cotizacion.valor_venta = pedir_decimal("Venta", cotizacion.valor_venta)
        self._cotizaciones.modificar(cotizacion)
        print("Modificada.")

    def _baja_cotizacion(self) -> None:
        """Elige una cotización y la elimina si se confirma."""
        cotizacion = elegir("Cotizaciones", self._cotizaciones.listar(), _describir_cotizacion)
        if confirmar(f"¿Eliminar '{_describir_cotizacion(cotizacion)}'?"):
            self._cotizaciones.eliminar(cotizacion.tipo, cotizacion.fecha)
            print("Eliminada.")

    def _actualizar_cotizacion(self) -> None:
        """Obtiene las cotizaciones de la API, las registra y muestra las obtenidas."""
        registradas = self._cotizaciones.obtener_cotizaciones()
        self._listar("Cotizaciones obtenidas de la API", registradas, _describir_cotizacion)

    # ------------------------------------------------------------ precios: lista y exportación
    def _lista_bimonetaria(self) -> None:
        """Muestra cada libro con su precio en pesos (según el dólar elegido) y en otra moneda."""
        monedas = self._precios.monedas_con_precio(excluir_codigo="ARS")
        if not monedas:
            raise ValueError("No hay precios en otra moneda además de pesos.")
        if len(monedas) == 1:
            moneda = monedas[0]
            print(f"\nOtra moneda: {moneda.nombre} ({moneda.codigo})")
        else:
            moneda = elegir("Otra moneda", monedas, lambda m: f"{m} - {m.nombre}")
        tipo = elegir("Tipo de dólar para calcular los pesos", self._tipos.listar(), str)
        filas = self._precios.lista_bimonetaria(tipo, moneda)
        ancho = 42
        print(f"\n--- Precios en pesos (dólar {tipo.nombre}) y en {moneda.codigo} "
              f"({len(filas)} libros) ---")
        print(f"{'Libro':<{ancho}} {'Pesos ($)':>16} {moneda.codigo:>14}")
        for fila in filas:
            titulo = fila.libro.titulo
            titulo = titulo if len(titulo) <= ancho else titulo[:ancho - 3] + "..."
            pesos = "-" if fila.pesos is None else f"{fila.pesos:,.2f}"
            otra = "-" if fila.otra_moneda is None else f"{fila.otra_moneda:,.2f}"
            print(f"{titulo:<{ancho}} {pesos:>16} {otra:>14}")

    def _exportar_precios(self) -> None:
        """Exporta los precios de todos los libros, en todas las monedas, a un CSV."""
        nombre = input("Nombre del archivo [precios.csv]: ").strip() or "precios.csv"
        ruta, cantidad = self._precios.exportar_precios_csv(nombre)
        print(f"Se exportaron los precios de {cantidad} libros en todas las monedas.")
        print(f"Archivo: {ruta}")

    # ------------------------------------------------------------ scraping y alertas
    def _ejecutar_scraping(self) -> None:
        """Pide la diferencia de precios, ejecuta el scraper y genera el CSV de alertas."""
        print("\n--- Ejecutar scraping de Cúspide ---")
        diferencia = pedir_decimal("Diferencia de precios (en pesos) que dispara una alerta")
        tipo = elegir("Tipo de dólar para calcular los pesos", self._tipos.listar(), str)
        print("\nEjecutando el scraper (puede tardar unos minutos)...")
        resultado = self._scraping.ejecutar(diferencia, tipo)
        print(f"\nLibros comparados: {resultado.comparados} "
              f"(sin coincidencia en Cúspide: {resultado.sin_coincidencia})")
        print(f"Alertas generadas (diferencia de ${diferencia:,.2f} o más): "
              f"{resultado.alertas}")
        print(f"Archivo: {resultado.ruta}")

    def _generar_reporte(self) -> None:
        """Genera el reporte en Excel con los precios de la última extracción."""
        print("\n--- Generar reporte de precios (Excel) ---")
        tipo = elegir("Tipo de dólar para calcular los pesos", self._tipos.listar(), str)
        resultado = self._scraping.generar_reporte_excel(tipo)
        print(f"\nReporte de {resultado.libros} libros, extracción del "
              f"{resultado.fecha_extraccion:%d/%m/%Y %H:%M} "
              f"(sin coincidencia en Cúspide: {resultado.sin_coincidencia}).")
        print(f"Archivo: {resultado.ruta}")

    def _ver_historial(self) -> None:
        """Muestra las últimas operaciones registradas en la auditoría."""
        registros = self._auditoria.historial(LIMITE_HISTORIAL)
        print(f"\n--- Historial de auditoría (últimas {LIMITE_HISTORIAL}, "
              "más recientes primero) ---")
        if not registros:
            print("Todavía no hay operaciones registradas.")
        for registro in registros:
            print(f"{registro.fecha:%d/%m/%Y %H:%M:%S}  {registro.accion}")
            if registro.detalles:
                print(f"    {registro.detalles}")

    # ------------------------------------------------------------ reportes
    def _menu_reportes(self) -> None:
        """Submenú de reportes: stock bajo, cotización de un libro y catálogo cotizado."""
        self._menu("REPORTES", [
            ("Libros con stock bajo", self._reporte_stock_bajo),
            ("Cotizar un libro en pesos", self._reporte_cotizar_libro),
            ("Catálogo cotizado y valorización del inventario", self._reporte_catalogo),
        ])

    def _reporte_stock_bajo(self) -> None:
        """Muestra los libros con stock menor o igual al umbral indicado."""
        umbral = pedir_entero("Mostrar libros con stock menor o igual a", 5)
        self._listar("Stock bajo", self._stock.con_stock_bajo(umbral), _describir_stock)

    @auditar("Reporte: cotizar un libro en pesos",
             detalle=lambda argumentos, resultado: resultado)
    def _reporte_cotizar_libro(self) -> str:
        """Muestra el precio en pesos de un libro según el dólar elegido.

        Devuelve un resumen del resultado, que se guarda en la auditoría.
        """
        libro = elegir("Libros", self._libros.listar(), _describir_libro)
        tipo = elegir("Tipos de cotización", self._tipos.listar(), str)
        pesos = self._precios.cotizar_en_pesos(libro, tipo)
        print(f"\n'{libro.titulo}' cotizado al dólar {tipo.nombre}: ${pesos:,.2f}")
        return f"'{libro.titulo}' al dólar {tipo.nombre}: ${pesos:,.2f}"

    @auditar("Reporte: catálogo cotizado e inventario",
             detalle=lambda argumentos, resultado: resultado)
    def _reporte_catalogo(self) -> str:
        """Muestra el catálogo cotizado en pesos y calcula el valor total del inventario.

        Devuelve un resumen del resultado, que se guarda en la auditoría.
        """
        tipo = elegir("Tipos de cotización", self._tipos.listar(), str)
        cantidades: Dict[int, int] = {s.libro_id: s.cantidad for s in self._stock.listar()}
        total = Decimal("0")
        cotizados = 0
        print(f"\n--- Catálogo cotizado al dólar {tipo.nombre} ---")
        for libro in self._libros.listar():
            try:
                pesos = self._precios.cotizar_en_pesos(libro, tipo)
            except ValueError:
                print(f"- {libro.titulo}: sin precio o sin cotización")
                continue
            cantidad = cantidades.get(libro.id, 0)
            total += pesos * cantidad
            cotizados += 1
            print(f"- {libro.titulo}: ${pesos:,.2f} x {cantidad} u.")
        print(f"\nValor total del inventario: ${total:,.2f}")
        return (f"dólar {tipo.nombre}: {cotizados} libros cotizados, "
                f"inventario valuado en ${total:,.2f}")
