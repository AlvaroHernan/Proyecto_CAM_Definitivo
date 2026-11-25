# notebooks

Notebooks de Jupyter con la exploración, limpieza, validación y modelado de los datos. Se numeran en el orden en que deben ejecutarse.

## Limpieza e imputación de La Lindosa y Los Micos

| Notebook | Qué hace | Lee | Escribe |
|---|---|---|---|
| [`01_resolucion_horaria.ipynb`](01_resolucion_horaria.ipynb) | Lleva las series a un dato por hora (nivel y temperatura promediados, lluvia sumada), arma la grilla horaria completa y aplica el filtro de sensor pegado | `data/processed/<estación>/<estación>_consolidado.csv` | `data/processed/<estación>/<estación>_horario.csv` |
| [`02_calidad_temporal.ipynb`](02_calidad_temporal.ipynb) | Ítem C del artículo: frecuencia dominante, cobertura y catálogo de huecos (corto / medio / largo) | `..._horario.csv` | `data/clean/<estación>/<estación>_inventario_huecos.csv` |
| [`03_imputacion.ipynb`](03_imputacion.ipynb) | Ítems D y E: prueba de métodos de relleno y cascada REAL → ALTA → MEDIA → BAJA → SIN_DATO con columnas de trazabilidad | `..._horario.csv` | `data/clean/<estación>/<estación>_horario_limpio.csv` |
| [`04_eda_correlacion.ipynb`](04_eda_correlacion.ipynb) | Análisis exploratorio: estadísticas, estacionalidad, eventos extremos, correlaciones y retraso lluvia → nivel | `..._horario_limpio.csv` | — (solo gráficas y tablas) |

Los resultados y las decisiones tomadas están resumidos en [`data/clean/README.md`](../data/clean/README.md).

## Cómo ejecutarlos

Se necesita Python 3.10 o más reciente con estas librerías:

```
pip install pandas numpy scipy matplotlib jupyter
```

Luego, desde la carpeta raíz del repositorio:

```
jupyter notebook notebooks/
```

y ejecutar los notebooks en orden (01 → 04) con *Run All*. Cada uno tarda menos de un minuto. Los parámetros que se pueden ajustar (umbrales de registros por hora, sensor pegado, largo de huecos) están en la primera celda de código de cada notebook.
