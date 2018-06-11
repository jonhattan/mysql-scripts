# Description

Los scripts están escritos en python y leen credenciales de ~/.my.cnf. No he hecho el esfuerzo final de dejarlos pulidos para su uso out-of-the-box, quizás lo haga en un rato libre, o cuando vuelva a necesitar usarlos. Algunos de ellos son interactivos y en otros es necesario editar el fichero para establecer ciertos parámetros.

# Scripts

## Charset Fix

Busca y reemplaza caracteres raros en todos los campos de todas las tablas de una base de datos. Fuerza bruta de último recurso útil en el caso de que el charset se haya hecho un lío tras una migración o actualización. Este script lo necesité para desenredar tras actualizar varios sitios a drupal 6 (esta versión de drupal empezó a forzar el uso de UTF8).

## Collation Fix

Cambia el collation de todos los campos de todas las tablas de una base de datos. Útil en el caso de que se creara la base de datos sin prestar atención al collation y acabase hecha un lío.

## Massive search

Busca una cadena de texto en todos los campos de todas las tablas de una base de datos. Es la misma funcionalidad de búsqueda global que proporciona phpmyadmin.

## Mysql cleanup

Recorre todas las tablas de todas las bases de datos y las optimiza (borra residuos). Adicionalmente puede hacer check-and-repair y notificar de todas las tablas que sobrepasan un umbral de tamaño.

