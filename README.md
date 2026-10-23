### Sprint 3

En este sprint el sistema obtiene datos de la web: un scraper hecho con Scrapy descarga los precios de la competencia (Cúspide) para los libros del catálogo. Esos precios se comparan con los internos, se generan alertas en CSV y un reporte en Excel, y todas las operaciones del sistema quedan auditadas.

## Sprint 2

# Book Manager - Sprint 1

## Objetivo
El objetivo principal de este proyecto es aplicar los conocimientos adquiridos en programación orientada a objetos, almacenamiento de datos en archivos para su persistencia.

## Introducción y Contexto del problema
Una librería con venta al público necesita modernizar su sistema de gestión de inventario de libros. Debido a la fluctuación en los costos de importación de material bibliográfico, el sistema debe gestionar precios en diferentes monedas y seguir de cerca la cotización del dólar para actualizar sus valores en tiempo real.

El objetivo es desarrollar una aplicación de consola (CLI) robusta en Python que permita gestionar el inventario de una librería, cotizar los libros en tiempo real según el valor del dólar y comparar precios automáticamente con la competencia web.