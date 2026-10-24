# Changelog

[Ejercicio 02]

- Función cargar_datos_desde_sql() en migrations/migrations.py: carga los datos desde un archivo .sql o desde todos los .sql de una carpeta.
- Ejecución en una única transacción y repetible sin duplicar datos.
- main.py usa la nueva función para la carga inicial.

# Sprint 3

[Ejercicio 01]

- Rama Sprint_3 creada a partir de Sprint_2.
- Servicios renombrados a la convención Servicio* (ServicioGenero, ServicioEditorial, ServicioMoneda, ServicioTipoCotizacion, ServicioLibro, ServicioPrecio, ServicioStock).
- Carpetas scraper/ y reportes/ agregadas a la estructura.
- README actualizado al Sprint 3.

# Sprint 2

[Ejercicio 08]

- Nuevas opciones en el menú principal: obtener cotizaciones por API, lista de precios bimonetaria y exportación de precios a CSV.
- Lista bimonetaria: precio en pesos (con la última cotización del dólar elegido) y en otra moneda seleccionada.
- Exportación a CSV de los precios de todas las monedas (una fila por libro, una columna por moneda).
- Lógica en PrecioService: lista_bimonetaria, monedas_con_precio y exportar_precios_csv.

[Ejercicio 07]

- Servicio ServicioCotizacionDolar (reemplaza a CotizacionService) con la función obtener_cotizaciones().
- Descarga de las cotizaciones desde la API configurada en API_URL (.env) y registro en la base.
- Registro repetible: actualiza si ya existe la cotización del tipo y fecha, y crea los tipos que falten.
- Validación de la respuesta antes de escribir en la base.
- Actualización de main.py y console.py para usar el nuevo servicio.

[Ejercicio 06] 

- Repositorios reescritos para usar la base de datos con SQLAlchemy (repositories.py).
- Traducción de errores de integridad de la base a ValueError.
- Métodos leer_por_id y leer_todos en los repositorios de Stock y CotizacionDolar.
- main.py crea las tablas y carga los datos iniciales si la base está vacía.
- preload_data.py genera los CSV de origen sin depender de los repositorios.

[Ejercicio 05]
- Función migrar_datos() en migrations/migrations.py: lee los CSV del Sprint 1, genera los .sql y puebla la base.
- Archivos .sql por tabla (migrations/sql) numerados según el orden de dependencias.
- Ejecución en una única transacción y repetible sin duplicar datos (ON CONFLICT DO NOTHING).
- Validación y escape de los valores antes de armar las sentencias.

[Ejercicio 04] 

- Modelos SQLAlchemy (models/models.py) para las 8 tablas del sistema.
- Tipos de dato definidos, claves primarias y foráneas con restricciones de borrado.
- Restricciones de unicidad (ISBN, nombres, precio por libro y moneda) y valores no negativos.
- Funciones crear_tablas() y eliminar_tablas().

[Ejercicio 03]

- Context manager transaccion() en ConexionDB para manejar transacciones.
- Commit automático al terminar el bloque y rollback ante cualquier excepción.
- Cierre de la sesión en todos los casos.

[Ejercicio 02] 

- Clase ConexionDB (database/connection.py) con SQLAlchemy.
- Lectura de DATABASE_URL desde .env.local, .env o variable de entorno.
- Normalización del driver de Postgres (psycopg2) y ocultamiento de la contraseña al mostrar la URL.
- Dependencias: sqlalchemy, psycopg2-binary y python-dotenv.

 [Ejercicio 01] 

- Trabajando sobre la rama sprint 2, partinedo de sprint 1. 

# Sprint 1

[Corrección post-entrega]

- Servicios para todas las entidades (Género, Editorial, Moneda, TipoCotización, Libro, Precio, Stock, Cotización).
- Repositorios con persistencia real en CSV y reconstrucción de objetos relacionados.
- eliminar() recibe objetos en lugar de IDs.
- Limpieza de __pycache__ y de la carpeta src/src; agregado de .gitignore.

[Correcciones Finales] 

- Integración de la entidad Precio y creación de su respectivo RepositorioPrecio para manejar costos base en moneda extranjera.
- Actualización de los datos CSV con cotizaciones reales y actuales del dólar oficial ($1545) y blue ($1560).

[Ejercicio 07] 

- Creación del archivo de entrada main.py.
- Implementación de inyección de dependencias (repositorios instanciados hacia servicios, y servicios hacia la interfaz).
- Incorporación del parámetro import_default_data en la función main para controlar la ejecución desde entornos externos (Colab).

[Ejercicio 06] 

- Desarrollo de la interfaz gráfica de línea de comandos (CLI) en console.py.
- Implementación de un sistema de navegación por menús interactivos y limpieza de pantalla.
- Diseño corporativo y formateo tabular para la lectura de datos.
- Integración de las operaciones CRUD (alta, baja, modificación, lectura) consumiendo la capa de servicios.

[Ejercicio 05]

- Desarrollo del módulo de precarga de datos en preload_data.py.
- Generación automática de archivos CSV en la ruta migrations/csv cumpliendo con el mínimo de 10 registros por clase.
- Implementación de datos temáticos ( Romance y Deep Learning).
- Funcionalidad para leer los CSV e inyectar los datos en los repositorios correspondientes.

[Ejercicio 04]

- Creación de clases de servicio (LibroService, CotizacionService, PrecioService) para encapsular la lógica de negocio.
- Implementación de método para el registro simultáneo de un libro y su stock inicial.
- Desarrollo de la lógica de conversión de precios en tiempo real buscando la cotización más reciente del dólar.

[Ejercicio 03] 

- Implementación de las interfaces de repositorios según la consigna.
- Desarrollo de las clases concretas de persistencia en memoria (RepositorioLibro, RepositorioGenero, RepositorioEditorial, RepositorioStock, RepositorioCotizacionDolar).
- Incorporación de los métodos CRUD (crear, leer, actualizar, eliminar) para cada repositorio.

[Ejercicio 02] 

- Creación de clases entidad (Libro, Genero, Editorial, Moneda, TipoCotizacion, Precio, Stock, CotizacionDolar).
- Implementación de encapsulamiento mediante propiedades y atributos privados.
- Aplicación de Type Hints en atributos y métodos.

[Ejercicio 01] 

- Inicialización y configuración de la herramienta de versionado.
- Creación de la rama "Sprint_1".
- Creación de la estructura de directorios y archivos base.
- Redacción inicial del README.md con el contexto del Sprint 1.

