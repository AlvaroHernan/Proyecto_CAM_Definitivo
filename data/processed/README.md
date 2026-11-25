# data/processed

Datos **limpios y validados** en formato `.csv`, listos para el modelado (Objetivo 1, actividades 1.2 a 1.4).

## Datos consolidados por estación

Cada carpeta contiene **un solo archivo CSV con todos los años** de la estación y un `README.md` que explica las anomalías encontradas en los datos crudos y cómo se corrigieron.

| Estación | Archivo | Desde | Hasta |
|---|---|---|---|
| El Batán | [El_Batan_consolidado.csv](El_Batan/) | 2017-01 | 2025-12 |
| El Mesón | [El_Meson_consolidado.csv](El_Meson/) | 2017-07 | 2025-12 |
| La Lindosa | [La_Lindosa_consolidado.csv](La_Lindosa/) | 2017-06 | 2025-12 |
| Las Juntas | [Las_Juntas_consolidado.csv](Las_Juntas/) | 2017-06 | 2025-12 |
| Los Micos | [Los_Micos_consolidado.csv](Los_Micos/) | 2017-06 | 2025-12 |
| Puente Bruselas | [Puente_Bruselas_consolidado.csv](Puente_Bruselas/) | 2017-01 | 2025-12 |
| San Bartolo | [San_Bartolo_consolidado.csv](San_Bartolo/) | 2017-07 | 2025-12 |
| San Benito | [San_Benito_consolidado.csv](San_Benito/) | 2017-01 | 2025-12 |
| Santa Rosalía | [Santa_Rosalia_consolidado.csv](Santa_Rosalia/) | 2016-11 | 2025-12 |

Formato común: separador `,`, decimal `.`, UTF-8, `fecha_hora` como `AAAA-MM-DD HH:MM`. Las columnas `fuente` (MAIGRAI/MeerKAD) e `intervalo_min` (60 o 5) indican de dónde viene cada fila: los años 2016-2020 son horarios y 2020-2025 son cada ~5 minutos.

Se generan con:

```
python src/consolidar_estaciones.py
```

## Series horarias (La Lindosa y Los Micos)

`La_Lindosa/La_Lindosa_horario.csv` y `Los_Micos/Los_Micos_horario.csv` son un paso intermedio: la serie llevada a **un dato por hora** (nivel y temperatura promediados, lluvia sumada), con una fila por cada hora y el filtro de sensor pegado aplicado, pero **todavía con huecos**. Las genera [`notebooks/01_resolucion_horaria.ipynb`](../../notebooks/01_resolucion_horaria.ipynb). Las series ya imputadas y listas para modelar están en [`data/clean/`](../clean/).
