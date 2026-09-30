import os
from book_manager.services.services import LibroService, CotizacionService, PrecioService

class ConsoleUI:
    def __init__(self, libro_service: LibroService, cotizacion_service: CotizacionService, precio_service: PrecioService):
        self.libro_service = libro_service
        self.cotizacion_service = cotizacion_service
        self.precio_service = precio_service

    def limpiar_pantalla(self):
        """Limpia la consola para dar un aspecto de aplicación fluida."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def imprimir_encabezado(self, titulo: str):
        self.limpiar_pantalla()
        print("=" * 80)
        print(f" CUSPIDE - SISTEMA DE GESTIÓN BIBLIOGRÁFICA ".center(80, "="))
        print(f" {titulo} ".center(80, " "))
        print("=" * 80)
        print()

    def iniciar(self):
        while True:
            self.imprimir_encabezado("MENÚ PRINCIPAL")
            print("  [1] Gestión de Inventario (Libros y Stock)")
            print("  [2] Consultar Cotizaciones en Tiempo Real")
            print("  [0] Salir del Sistema")
            print("-" * 80)
            
            opcion = input("Seleccione una opción: ")

            if opcion == '1':
                self.menu_libros()
            elif opcion == '2':
                self.menu_cotizaciones()
            elif opcion == '0':
                print("\nCerrando el sistema. ¡Que tenga un excelente día!")
                break
            else:
                input("\nOpción no válida. Presione Enter para reintentar...")

    def menu_libros(self):
        while True:
            self.imprimir_encabezado("MÓDULO DE INVENTARIO")
            print("  [1] Listar todos los libros con stock (Lectura)")
            print("  [2] Registrar nuevo libro (Alta)")
            print("  [3] Actualizar stock de un libro (Modificación)")
            print("  [4] Eliminar un libro del catálogo (Baja)")
            print("  [0] Volver al Menú Principal")
            print("-" * 80)
            
            opcion = input("Seleccione una opción: ")

            if opcion == '1':
                self._listar_libros()
            elif opcion == '2':
                self._alta_libro()
            elif opcion == '3':
                self._modificar_stock()
            elif opcion == '4':
                self._baja_libro()
            elif opcion == '0':
                break
            else:
                input("\nOpción no válida. Presione Enter para reintentar...")

    def _listar_libros(self):
        self.imprimir_encabezado("CATÁLOGO DE LIBROS Y STOCK (Cálculo a Dólar Blue)")
        libros_stock = self.libro_service.listar_libros_con_stock()
        
        if not libros_stock:
            print("El catálogo está vacío.")
        else:
            print(f"{'ISBN':<15} | {'TÍTULO':<35} | {'STOCK':<5} | {'PRECIO ARS':<15}")
            print("-" * 80)
            for libro, cantidad in libros_stock:
                titulo_corto = (libro.titulo[:32] + '...') if len(libro.titulo) > 35 else libro.titulo
                
                # Obtenemos precio y calculamos ARS
                precio_base = self.precio_service.obtener_precio_base(libro.isbn)
                precio_str = "N/A"
                if precio_base:
                    try:
                        # Cotiza usando el Dólar Blue (ID 2 = $1560)
                        precio_ars = self.precio_service.calcular_precio_ars(precio_base, 2)
                        precio_str = f"$ {precio_ars:,.2f}"
                    except ValueError:
                        pass

                print(f"{libro.isbn:<15} | {titulo_corto:<35} | {cantidad:<5} | {precio_str:<15}")
        
        input("\nPresione Enter para continuar...")

    def _alta_libro(self):
        self.imprimir_encabezado("REGISTRO DE NUEVO LIBRO")
        print("Funcionalidad en desarrollo para el próximo sprint (requiere inyectar repositorios de Género y Editorial).")
        input("\nPresione Enter para volver...")

    def _modificar_stock(self):
        self.imprimir_encabezado("ACTUALIZACIÓN DE STOCK")
        isbn = input("Ingrese el ISBN del libro: ")
        try:
            nueva_cantidad = int(input("Ingrese la nueva cantidad de stock: "))
            self.libro_service.actualizar_stock(isbn, nueva_cantidad)
            print("\n¡Stock actualizado con éxito!")
        except ValueError as e:
            print(f"\nError: {e}")
        input("\nPresione Enter para continuar...")

    def _baja_libro(self):
        self.imprimir_encabezado("ELIMINAR LIBRO")
        isbn = input("Ingrese el ISBN del libro a eliminar: ")
        if self.libro_service.repo_libro.eliminar(isbn):
            self.libro_service.repo_stock.eliminar(isbn)
            print("\nLibro y su stock asociado eliminados correctamente.")
        else:
            print("\nError: No se encontró el libro especificado.")
        input("\nPresione Enter para continuar...")

    def menu_cotizaciones(self):
        self.imprimir_encabezado("COTIZACIONES DEL DÓLAR")
        cotizacion_blue = self.cotizacion_service.obtener_cotizacion_actual(2) # 2 = Dólar Blue
        cotizacion_oficial = self.cotizacion_service.obtener_cotizacion_actual(1) # 1 = Oficial
        
        print("VALORES ACTUALIZADOS EN TIEMPO REAL:")
        print("-" * 40)
        if cotizacion_oficial:
            print(f"Dólar Oficial : $ {cotizacion_oficial.valor_venta:.2f} (Fecha: {cotizacion_oficial.fecha})")
        if cotizacion_blue:
            print(f"Dólar Blue    : $ {cotizacion_blue.valor_venta:.2f} (Fecha: {cotizacion_blue.fecha})")
        print("-" * 40)
        
        input("\nPresione Enter para volver...")