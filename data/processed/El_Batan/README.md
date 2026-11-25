# Estación El Batan — datos consolidados

Archivo: [`El_Batan_consolidado.csv`](El_Batan_consolidado.csv) — 457.908 registros, del 2017-01-01 00:00 al 2025-12-31 23:58.

Generado automáticamente por [`src/consolidar_estaciones.py`](../../../src/consolidar_estaciones.py) a partir de los 8 archivos de [`data/raw/El_Batan`](../../raw/El_Batan). Los datos crudos no se modificaron. Para regenerarlo: `python src/consolidar_estaciones.py`.

## Formato del archivo

- Separador `,` (coma), decimales con `.` (punto), codificación UTF-8.
- `fecha_hora` en formato `AAAA-MM-DD HH:MM`, ordenada de la más antigua a la más reciente.
- Celda vacía = dato faltante o descartado.
- Variables: `nivel_(m)`, `temperatura_(°C)`, `humedad_(%)`, `radiacion_solar_(W/m2)`, `rad_u_(W/m2)`, `pres_atmosferica_(hPa)`, `lluvia_(mm)`, `direccion_viento_(°)`, `velocidad_viento_(m/s)`.
- `fuente`: `MAIGRAI` (Excel 2016-2020, un dato por hora) o `MeerKAD` (CSV 2020-2025, un dato cada ~5 min).
- `intervalo_min`: 60 o 5. **Ojo:** la `lluvia_(mm)` de las filas horarias es el acumulado de una hora y la de las filas de 5 min es el acumulado de 5 min. Para comparar años hay que llevar todo a la misma resolución (por ejemplo, sumar la lluvia y promediar el resto por hora o por día).

## Archivos de origen

| Archivo | Fuente | Paso | Registros | Desde | Hasta |
|---|---|---|---|---|---|
| `Batan_2017.xlsx` | MAIGRAI | 60 min | 8.760 | 2017-01-01 00:00 | 2017-12-31 23:00 |
| `Batan_2018.xlsx` | MAIGRAI | 60 min | 1.259 | 2018-01-01 00:00 | 2018-02-22 10:00 |
| `Batan_2020.csv` | MeerKAD | 5 min | 3.688 | 2020-12-14 09:10 | 2020-12-31 23:55 |
| `Batan_2021.csv` | MeerKAD | 5 min | 85.618 | 2021-01-01 00:00 | 2021-12-30 12:41 |
| `Batan_2022.csv` | MeerKAD | 5 min | 58.026 | 2022-01-01 00:00 | 2022-12-30 05:44 |
| `Batan_2023.csv` | MeerKAD | 5 min | 100.222 | 2023-01-01 00:01 | 2023-12-31 23:58 |
| `Batan_2024.csv` | MeerKAD | 5 min | 98.492 | 2024-01-01 00:03 | 2024-12-31 23:59 |
| `Batan_2025.csv` | MeerKAD | 5 min | 101.843 | 2025-01-01 00:04 | 2025-12-31 23:58 |

Años sin ningún archivo: **2019**.

## Anomalías encontradas y cómo se corrigieron

1. **Dos formatos distintos.** Los Excel (MAIGRAI) traen la fecha como fecha de Excel y un dato por hora; los CSV (MeerKAD) usan `;` como separador, `,` como decimal, fecha `DD/MM/AAAA H:MM`, codificación Latin-1 (el símbolo `°` aparecía como `�`) y un dato cada ~5 min. Todo se llevó al formato descrito arriba.
2. **Nombres de variables distintos entre años.** Se renombraron así:

   | Nombre original | Nombre estándar | Archivos |
   |---|---|---|
   | `Presion Atmosferica (HPa)` | `pres_atmosferica_(hPa)` | `Batan_2017.xlsx`, `Batan_2018.xlsx` |
   | `Rad,_U (W/m2)` | `rad_u_(W/m2)` | `Batan_2020.csv`, `Batan_2021.csv`, `Batan_2022.csv`, `Batan_2023.csv`, `Batan_2024.csv`, `Batan_2025.csv` |

3. **Decimales con ruido en los Excel** (p. ej. `0.6599999999999999` o `845.888736`): se redondearon a 3 decimales.
4. **Control de rangos.** Según el PDF de observaciones, los CSV de MeerKAD ya venían depurados (valores fuera de rango → vacío), pero los Excel de MAIGRAI "no tuvieron tratamiento de datos". Para que todo el archivo sea homogéneo se aplicaron los mismos rangos válidos del PDF a todos los años.
   No se encontró ningún valor fuera de rango.

5. **Fechas repetidas:** no se encontró ninguna.

No se aplicó a los años de MAIGRAI el filtro de "sensor pegado" (más de 20 valores idénticos seguidos) que describe el PDF, porque con datos horarios ese criterio no equivale al de 5 min. Queda pendiente para la etapa de limpieza.

## Para revisar (no se modificó)

- Los CSV de MeerKAD traen una columna `Rad,_U (W/m2)` (valores entre 0,03 y 0,39) que no aparece en los Excel ni en el PDF de observaciones. Se conservó con el nombre `rad_u_(W/m2)`; **confirmar con el proveedor qué mide** (posiblemente radiación UV).
- La presión atmosférica solo existe en 2017-2018 (Excel). Los CSV 2020-2025 no traen esa variable.
- La lluvia está vacía en 2020, 2021 y 2022 y parcialmente en 2023.

## Datos disponibles por año

Porcentaje de registros con dato en cada variable (— = sin datos).

| Año | Fuente | Registros | `nivel_(m)` | `temperatura_(°C)` | `humedad_(%)` | `radiacion_solar_(W/m2)` | `rad_u_(W/m2)` | `pres_atmosferica_(hPa)` | `lluvia_(mm)` | `direccion_viento_(°)` | `velocidad_viento_(m/s)` |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2017 | MAIGRAI | 8.760 | 88 % | 92 % | 92 % | 50 % | — | 94 % | 100 % | 100 % | 100 % |
| 2018 | MAIGRAI | 1.259 | 100 % | 100 % | 100 % | 54 % | — | 100 % | 100 % | 85 % | 100 % |
| 2020 | MeerKAD | 3.688 | 71 % | 97 % | 97 % | 49 % | 100 % | — | — | 100 % | 97 % |
| 2021 | MeerKAD | 85.618 | 24 % | 100 % | 100 % | 48 % | 100 % | — | — | 100 % | 100 % |
| 2022 | MeerKAD | 58.026 | 92 % | 99 % | 100 % | 43 % | 100 % | — | — | 98 % | 98 % |
| 2023 | MeerKAD | 100.222 | 59 % | 100 % | 100 % | 49 % | 100 % | — | 84 % | 98 % | 98 % |
| 2024 | MeerKAD | 98.492 | 82 % | 100 % | 100 % | 47 % | 100 % | — | 100 % | 98 % | 98 % |
| 2025 | MeerKAD | 101.843 | 93 % | 100 % | 100 % | 49 % | 100 % | — | 100 % | 96 % | 96 % |
