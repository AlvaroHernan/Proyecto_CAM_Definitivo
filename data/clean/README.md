# data/clean

Series de tiempo **horarias, limpias y sin huecos** de las estaciones **La Lindosa** y **Los Micos**, listas para el modelado de predicción de nivel (Objetivo 2).

Se eligieron estas dos estaciones porque son las más aptas para predicción (ver [`docs/aptitud_estaciones_nivel.md`](../../docs/aptitud_estaciones_nivel.md)). El proceso sigue los ítems **C, D y E** de la metodología del artículo *"A Multi-Stage ETL Framework for Hydrometeorological Data Quality Management in Flood-Prone Watersheds"* (caso río Las Ceibas), adaptados a resolución horaria.

## Archivos

| Archivo | Contenido | Filas |
|---|---|---|
| [`La_Lindosa/La_Lindosa_horario_limpio.csv`](La_Lindosa/La_Lindosa_horario_limpio.csv) | Serie horaria imputada, 2017-06-23 10:00 a 2025-12-31 23:00 | 74.726 |
| [`La_Lindosa/La_Lindosa_inventario_huecos.csv`](La_Lindosa/La_Lindosa_inventario_huecos.csv) | Catálogo de los 430 huecos encontrados antes de imputar | 430 |
| [`Los_Micos/Los_Micos_horario_limpio.csv`](Los_Micos/Los_Micos_horario_limpio.csv) | Serie horaria imputada, 2017-06-23 17:00 a 2025-12-31 20:00 | 74.716 |
| [`Los_Micos/Los_Micos_inventario_huecos.csv`](Los_Micos/Los_Micos_inventario_huecos.csv) | Catálogo de los 877 huecos encontrados antes de imputar | 877 |

Formato: separador `,`, decimal `.`, UTF-8, `fecha_hora` como `AAAA-MM-DD HH:MM`. Cada fila es **la hora que empieza** en `fecha_hora` (por ejemplo, `14:00` = de 14:00 a 14:59).

### Columnas de `<estación>_horario_limpio.csv`

Para cada variable `X` (`nivel_m`, `temperatura_c`, `lluvia_mm`):

| Columna | Qué contiene |
|---|---|
| `X` | **Valor final** (observado o imputado). Es la columna que se usa para modelar. |
| `X_original` | Valor observado antes de imputar; vacío si no había dato. |
| `X_imputado` | `1` si el valor final fue imputado, `0` si es observado. |
| `X_calidad` | Etiqueta de confianza: `REAL`, `ALTA`, `MEDIA`, `BAJA` o `SIN_DATO` (ver abajo). |
| `X_hueco` | Si la hora estaba vacía, tamaño del hueco: `corto` (≤ 6 h), `medio` (6-24 h) o `largo` (> 24 h). |

Además:

- `fuente`: `MAIGRAI` (2017 - feb 2020, dato horario), `MeerKAD` (feb 2020 - 2025, agregado desde 5 min) `MeerKAD+MAIGRAI` (una sola hora, La Lindosa 2020-02-26 14:00, en el cambio de sistema; se usó el dato MeerKAD) o `sin_registro` (hora sin ningún dato).
- `nivel_pegado`: `True` si el nivel original de esa hora se anuló por "sensor pegado" (ver paso 1).

### Etiquetas de calidad

| Etiqueta | Origen del valor | ¿Usar para entrenar? |
|---|---|---|
| `REAL` | Observado por el sensor | Sí |
| `ALTA` | Interpolación lineal en un hueco corto (nivel: hasta 24 h; temperatura: hasta 6 h) | Sí |
| `MEDIA` | Promedio histórico de la misma fecha y hora (o del mismo mes y hora) en otros años | No; solo exploración |
| `BAJA` | Spline cúbico de último recurso | No (no se necesitó: 0 %) |
| `SIN_DATO` | No se pudo rellenar | No (no quedó ninguno: 0 %) |

Para usar solo lo confiable sin romper la continuidad horaria:

```python
import pandas as pd
df = pd.read_csv("data/clean/La_Lindosa/La_Lindosa_horario_limpio.csv", parse_dates=["fecha_hora"])
# No borrar filas: se pegarían horas separadas por un hueco. Mejor dejar vacío lo no confiable
# y descartar después las ventanas de entrenamiento que tengan algún vacío.
df["nivel_confiable"] = df.nivel_m.where(df.nivel_m_calidad.isin(["REAL", "ALTA"]))
```

## Resultado

Porcentaje de horas de cada serie según su etiqueta:

| Estación | Variable | REAL | ALTA | MEDIA | BAJA | SIN_DATO |
|---|---|---|---|---|---|---|
| La Lindosa | nivel | 93,0 % | 1,1 % | 5,9 % | 0 % | 0 % |
| La Lindosa | temperatura | 86,9 % | 0,1 % | 13,1 % | 0 % | 0 % |
| La Lindosa | lluvia | 94,5 % | — | 5,5 % | — | 0 % |
| Los Micos | nivel | 90,0 % | 2,6 % | 7,4 % | 0 % | 0 % |
| Los Micos | temperatura | 92,5 % | 0,2 % | 7,3 % | 0 % | 0 % |
| Los Micos | lluvia | 91,7 % | — | 8,3 % | — | 0 % |

El nivel queda con **94,1 % (La Lindosa) y 92,6 % (Los Micos) de horas REAL o ALTA**. Los valores observados no se modificaron (se verificó en el notebook 03).

## Qué se hizo, paso a paso

Todo está explicado y se puede volver a ejecutar en orden con los notebooks de [`notebooks/`](../../notebooks):

### 1. Resolución horaria — [`01_resolucion_horaria.ipynb`](../../notebooks/01_resolucion_horaria.ipynb)

- Los datos MeerKAD (cada ~5 min) se redondearon al múltiplo de 5 min más cercano y los duplicados se fusionaron (primer valor no nulo), como indica el artículo. Luego se agregaron por hora: **nivel y temperatura promediados, lluvia sumada**. Una hora solo vale si tiene al menos 6 de 12 registros (nivel, temperatura) o 10 de 12 (lluvia, para no subestimarla).
- Los datos MAIGRAI (2017-2020) ya eran horarios y se unieron tal cual.
- Se construyó una grilla con **una fila por cada hora**, aunque no haya dato.
- **Filtro de sensor pegado** (pendiente desde la consolidación): se anuló el nivel en rachas de más de 24 h con el mismo valor **solo si** al terminar o empezar la racha el nivel salta 5 cm o más, o si durante la racha llovió 10 mm o más sin respuesta. Así se anularon 693 h en La Lindosa y 152 h en Los Micos, todas en 2017-2019. No se anularon las demás rachas largas porque casi todas terminan con un cambio de 1 cm: son recesiones lentas registradas con resolución de 1 cm, no fallas.
- Salida intermedia: `data/processed/<estación>/<estación>_horario.csv`.

### 2. Calidad temporal (ítem C) — [`02_calidad_temporal.ipynb`](../../notebooks/02_calidad_temporal.ipynb)

- Frecuencia dominante (moda de las diferencias entre registros): 60 min en ambas.
- Cobertura bruta de nivel: 93,0 % (La Lindosa) y 90,0 % (Los Micos).
- Catálogo de huecos por variable con inicio, fin, horas faltantes y categoría. **Adaptación:** el artículo llama "corto" a ≤ 60 min porque trabaja a 5 min (12 registros); a resolución horaria eso sería 1 solo dato, así que se usó corto ≤ 6 h, medio 6-24 h, largo > 24 h.

### 3. Imputación escalonada (ítems D y E) — [`03_imputacion.ipynb`](../../notebooks/03_imputacion.ipynb)

Cascada del artículo: REAL → interpolación lineal (ALTA) → promedio de la misma fecha y hora en otros años, con al menos 2 valores (MEDIA) → promedio del mismo mes y hora en otros años (MEDIA) → spline cúbico (BAJA) → SIN_DATO. La lluvia **nunca se interpola** (ítem E): solo promedio histórico.

**Ajuste por variable, decidido con una prueba sobre los propios datos:** se borraron a propósito 300 tramos con dato de cada largo (1 a 72 h) y se compararon ambos métodos.

| Hueco | Nivel: error lineal | Nivel: error histórico | Temperatura: error lineal | Temperatura: error histórico |
|---|---|---|---|---|
| 6 h | 1-2 cm | ~13 cm | 1,2-1,4 °C | 1,5-1,7 °C |
| 24 h | 2-3 cm | ~11-13 cm | 3,6-4,1 °C | 1,6-1,8 °C |

- **Nivel:** la interpolación es mucho mejor que el promedio histórico incluso con huecos de 24 h, porque el nivel cambia mucho de un año a otro. Se interpola hasta **24 h**; el promedio histórico queda para huecos largos.
- **Temperatura:** la interpolación solo gana hasta ~6 h; después borra el ciclo día-noche. Se interpola hasta **6 h**.

### 4. EDA y correlación — [`04_eda_correlacion.ipynb`](../../notebooks/04_eda_correlacion.ipynb)

Hallazgos principales. El nivel y la temperatura se analizan solo con valores REAL. **Excepción:** los totales de lluvia (anuales, mensuales) y las ventanas de lluvia acumulada usan la lluvia final, que incluye valores imputados (5,5 % en La Lindosa y 8,3 % en Los Micos), porque una suma con horas vacías quedaría cortada; la lluvia hora a hora de la matriz de correlación sí es solo REAL.

- **Lluvia bimodal**: picos en marzo y noviembre; julio-agosto es lo más seco.
- **Correlación lluvia-nivel hora a hora débil** (r ≈ 0,1), igual que en el artículo. Con **lluvia acumulada de las 24-168 h previas sube a r ≈ 0,25-0,31**. El cambio de nivel responde a la lluvia de la misma hora o la anterior (respuesta rápida). Para predecir, el modelo debe recibir acumulados de lluvia de varias ventanas, no solo la lluvia actual.
- La temperatura casi no se relaciona con el nivel (|r| < 0,15).
- Las dos estaciones reciben lluvias parecidas (lluvia diaria r ≈ 0,67) y sus niveles cambian casi a la vez (Los Micos igual o 1 h después).

## Limitaciones y puntos para confirmar con la CAM

- **Valores MEDIA:** son un "comportamiento típico" de esa fecha, no lo que pasó ese año (error promedio ~12 cm en nivel). Si una crecida ocurrió dentro de un hueco, no aparece en la serie. En la lluvia, MEDIA reparte una lluvia promedio pequeña en todas las horas del hueco.
- **Cambios de nivel de base:** Los Micos baja en 2021-2022 y tiene un escalón de ~0,24 m el 22-dic-2023; La Lindosa baja en 2023-2025. Puede ser el cauce o un cambio de referencia del sensor.
- **Lluvia dudosa:** Los Micos 2025 registra solo ~410 mm en el año (frente a 900-1.350 mm en otros años); La Lindosa 2018-2020 registra 600-730 mm frente a 1.100-1.400 mm desde 2021; hay rachas de 0,1 mm/h durante 10-18 h seguidas (¿llovizna o goteo del pluviómetro?). No se modificaron.
- Todos los umbrales (registros mínimos por hora, sensor pegado, largo de huecos) son parámetros al inicio de cada notebook; si se cambian, basta con ejecutar los notebooks 01 a 04 en orden.
