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

## Modelos de predicción de nivel

Un notebook por estación, con la misma estructura. Cada uno entrena **SARIMAX, XGBoost, LSTM y Prophet**, los compara con la **persistencia** (suponer que el nivel no cambia) en el año de prueba 2025 y termina diciendo cuál modelo conviene en esa estación. El horizonte principal es **6 horas** (también se evalúan 1, 3 y 12 h); la justificación está en la sección 2 de cada notebook.

| Notebook | Estación | Lee | Escribe |
|---|---|---|---|
| [`05_modelos_La_Lindosa.ipynb`](05_modelos_La_Lindosa.ipynb) | La Lindosa | `data/clean/La_Lindosa/La_Lindosa_horario_limpio.csv` | `models/La_Lindosa/metricas_prueba_2025.csv` |
| [`06_modelos_Los_Micos.ipynb`](06_modelos_Los_Micos.ipynb) | Los Micos | `data/clean/Los_Micos/Los_Micos_horario_limpio.csv` | `models/Los_Micos/metricas_prueba_2025.csv` |

Partición: entrenamiento 2018-2023, validación 2024, prueba 2025. Solo se usa el nivel `REAL` o `ALTA` (las horas `MEDIA` se dejan vacías).

## Cómo ejecutarlos

Se necesita Python 3.10 o más reciente con estas librerías:

```
pip install pandas numpy scipy matplotlib jupyter
```

Para los notebooks de modelos (05 y 06) se necesitan además:

```
pip install statsmodels xgboost prophet torch
```

(`torch` es PyTorch, para la LSTM; la versión normal funciona sin tarjeta gráfica.)

Luego, desde la carpeta raíz del repositorio:

```
jupyter notebook notebooks/
```

y ejecutar los notebooks en orden (01 → 04) con *Run All*. Cada uno tarda menos de un minuto. Los notebooks 05 y 06 solo necesitan las series limpias que ya están en `data/clean/` y tardan unos 5 a 10 minutos cada uno. Los parámetros que se pueden ajustar (umbrales de registros por hora, sensor pegado, largo de huecos) están en la primera celda de código de cada notebook.
