# Changelog

[Ejercicio 05]
- Desarrollo del módulo de precarga de datos en `preload_data.py`.
- Generación automática de archivos CSV en la ruta `migrations/csv` cumpliendo con el mínimo de 10 registros por clase.
- Implementación de datos temáticos (fusión de Romance y Deep Learning).
- Funcionalidad para leer los CSV e inyectar los datos en los repositorios correspondientes.

[Ejercicio 04]
- Creación de clases de servicio (`LibroService`, `CotizacionService`, `PrecioService`) para encapsular la lógica de negocio.
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

