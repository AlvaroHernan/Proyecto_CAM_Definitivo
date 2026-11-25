# src

Scripts de Python reutilizables (funciones de carga, limpieza, validación y entrenamiento) que usan los notebooks.

## Scripts

- `consolidar_estaciones.py`: une los archivos anuales de cada estación de `data/raw/` en un solo CSV por estación en `data/processed/<estacion>/` y escribe un README con las anomalías corregidas. Requiere `pandas` y `openpyxl`. Ejecutar desde la raíz del repositorio: `python src/consolidar_estaciones.py`.
