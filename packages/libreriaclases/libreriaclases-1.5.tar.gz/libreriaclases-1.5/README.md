HEAD
# PBLgrupo6
# Libreria preproceso PBL grupo 6

### Prerequisitos

Se requiere las siguientes librerias:
 - numpy
 - pandas
 - scipy
 - sys
 - time

### Como usar

Estos son tus pasos a seguir para hacer tu limpieza de dataset:

1. Introduce tu ruta en la clase. --> ex:  Variable = libreria.DataAnalisis(ruta).
2. Lee tus datos con pandas:
- CSV: usa la función Variable.csv().
- Excel: usa la función Variable.excel().
3. Inicia la limpieza del dataset usando el método Variable.analisis().

Si quieres ver esta información mientras ejecutas usa la función Varable.info().

Extra: se pueden cambiar los siguientes criterios de anlalisis;

- variable 1 = Porcentaje de datos vacios para recomendar borrar columna (0.3 por defecto).
- variable 2 = Desplazamiento de la distribución normal para asumir distribución sesgada (0.05 por defecto).
Para ello crear un fichero 'valores.txt' con los valores separados con comas. Ejemplo: '0.3,0.05'

## Ejemplo de código:

import libreriaclases as lb

Data1=lb.DataAnalisis('ejemplo.csv')

Data1.csv()

Data1.analizar()
231ae43 (Primer commit)
