# Changelog

# Sprint 2

 [Ejercicio 01] - 11/10/2026 
- Trabajando sobre la rama sprint 2, partinedo de sprint 1. 

[Corrección post-entrega] - 11/10/2026
- Servicios para todas las entidades (Género, Editorial, Moneda, TipoCotización, Libro, Precio, Stock, Cotización).
- Repositorios con persistencia real en CSV y reconstrucción de objetos relacionados.
- eliminar() recibe objetos en lugar de IDs.
- Limpieza de __pycache__ y de la carpeta src/src; agregado de .gitignore.

[Correcciones Finales] - 29/09/2026
- Integración de la entidad Precio y creación de su respectivo RepositorioPrecio para manejar costos base en moneda extranjera.
- Actualización de los datos CSV con cotizaciones reales y actuales del dólar oficial ($1545) y blue ($1560).

[Ejercicio 07] - 28/09/2026
- Creación del archivo de entrada main.py.
- Implementación de inyección de dependencias (repositorios instanciados hacia servicios, y servicios hacia la interfaz).
- Incorporación del parámetro import_default_data en la función main para controlar la ejecución desde entornos externos (Colab).

[Ejercicio 06] - 27/09/2026
- Desarrollo de la interfaz gráfica de línea de comandos (CLI) en console.py.
- Implementación de un sistema de navegación por menús interactivos y limpieza de pantalla.
- Diseño corporativo y formateo tabular para la lectura de datos.
- Integración de las operaciones CRUD (alta, baja, modificación, lectura) consumiendo la capa de servicios.

[Ejercicio 05] - 26/09/2026
- Desarrollo del módulo de precarga de datos en preload_data.py.
- Generación automática de archivos CSV en la ruta migrations/csv cumpliendo con el mínimo de 10 registros por clase.
- Implementación de datos temáticos ( Romance y Deep Learning).
- Funcionalidad para leer los CSV e inyectar los datos en los repositorios correspondientes.

[Ejercicio 04] - 25/09/2026
- Creación de clases de servicio (LibroService, CotizacionService, PrecioService) para encapsular la lógica de negocio.
- Implementación de método para el registro simultáneo de un libro y su stock inicial.
- Desarrollo de la lógica de conversión de precios en tiempo real buscando la cotización más reciente del dólar.

[Ejercicio 03] - 24/09/2026
- Implementación de las interfaces de repositorios según la consigna.
- Desarrollo de las clases concretas de persistencia en memoria (RepositorioLibro, RepositorioGenero, RepositorioEditorial, RepositorioStock, RepositorioCotizacionDolar).
- Incorporación de los métodos CRUD (crear, leer, actualizar, eliminar) para cada repositorio.

[Ejercicio 02] - 23/09/2026
- Creación de clases entidad (Libro, Genero, Editorial, Moneda, TipoCotizacion, Precio, Stock, CotizacionDolar).
- Implementación de encapsulamiento mediante propiedades y atributos privados.
- Aplicación de Type Hints en atributos y métodos.

[Ejercicio 01] - 22/09/2026
- Inicialización y configuración de la herramienta de versionado.
- Creación de la rama "Sprint_1".
- Creación de la estructura de directorios y archivos base.
- Redacción inicial del README.md con el contexto del Sprint 1.

