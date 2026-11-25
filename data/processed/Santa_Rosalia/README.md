# Estación Santa Rosalia — datos consolidados

Archivo: [`Santa_Rosalia_consolidado.csv`](Santa_Rosalia_consolidado.csv) — 143.340 registros, del 2016-11-16 13:00 al 2025-12-31 23:57.

Generado automáticamente por [`src/consolidar_estaciones.py`](../../../src/consolidar_estaciones.py) a partir de los 6 archivos de [`data/raw/Santa_Rosalia`](../../raw/Santa_Rosalia). Los datos crudos no se modificaron. Para regenerarlo: `python src/consolidar_estaciones.py`.

## Formato del archivo

- Separador `,` (coma), decimales con `.` (punto), codificación UTF-8.
- `fecha_hora` en formato `AAAA-MM-DD HH:MM`, ordenada de la más antigua a la más reciente.
- Celda vacía = dato faltante o descartado.
- Variables: `temperatura_(°C)`, `humedad_(%)`, `radiacion_solar_(W/m2)`, `pres_atmosferica_(hPa)`, `lluvia_(mm)`, `direccion_viento_(°)`, `velocidad_viento_(m/s)`.
- `fuente`: `MAIGRAI` (Excel 2016-2020, un dato por hora) o `MeerKAD` (CSV 2020-2025, un dato cada ~5 min).
- `intervalo_min`: 60 o 5. **Ojo:** la `lluvia_(mm)` de las filas horarias es el acumulado de una hora y la de las filas de 5 min es el acumulado de 5 min. Para comparar años hay que llevar todo a la misma resolución (por ejemplo, sumar la lluvia y promediar el resto por hora o por día).

## Archivos de origen

| Archivo | Fuente | Paso | Registros | Desde | Hasta |
|---|---|---|---|---|---|
| `Santa Rosalia 2016.xlsx` | MAIGRAI | 60 min | 440 | 2016-11-16 13:00 | 2016-12-31 23:00 |
| `Santa Rosalia 2017.xlsx` | MAIGRAI | 60 min | 8.705 | 2017-01-01 00:00 | 2017-12-31 23:00 |
| `Santa Rosalia 2018.xlsx` | MAIGRAI | 60 min | 5.088 | 2018-01-01 00:00 | 2018-07-31 23:00 |
| `Santa_Rosalia_2021.csv` | MeerKAD | 5 min | 4.466 | 2021-08-12 11:27 | 2021-11-02 18:03 |
| `Santa_Rosalia_2024.csv` | MeerKAD | 5 min | 21.329 | 2024-09-27 10:55 | 2024-12-30 14:01 |
| `Santa_Rosalia_2025.csv` | MeerKAD | 5 min | 103.312 | 2025-01-01 00:00 | 2025-12-31 23:57 |

Años sin ningún archivo: **2019, 2020, 2022, 2023**.

## Anomalías encontradas y cómo se corrigieron

1. **Dos formatos distintos.** Los Excel (MAIGRAI) traen la fecha como fecha de Excel y un dato por hora; los CSV (MeerKAD) usan `;` como separador, `,` como decimal, fecha `DD/MM/AAAA H:MM`, codificación Latin-1 (el símbolo `°` aparecía como `�`) y un dato cada ~5 min. Todo se llevó al formato descrito arriba.
2. **Nombres de variables distintos entre años.** Se renombraron así:

   | Nombre original | Nombre estándar | Archivos |
   |---|---|---|
   | `Fecha` | `fecha_hora` | `Santa Rosalia 2016.xlsx`, `Santa Rosalia 2017.xlsx`, `Santa Rosalia 2018.xlsx` |
   | `Temperatura (C)` | `temperatura_(°C)` | `Santa Rosalia 2016.xlsx`, `Santa Rosalia 2017.xlsx`, `Santa Rosalia 2018.xlsx` |
   | `Humedad Relativa (%)` | `humedad_(%)` | `Santa Rosalia 2016.xlsx`, `Santa Rosalia 2017.xlsx`, `Santa Rosalia 2018.xlsx` |
   | `Radiacion Solar (W/m2)` | `radiacion_solar_(W/m2)` | `Santa Rosalia 2016.xlsx`, `Santa Rosalia 2017.xlsx`, `Santa Rosalia 2018.xlsx` |
   | `Presion atmosferica (HPA)` | `pres_atmosferica_(hPa)` | `Santa Rosalia 2016.xlsx`, `Santa Rosalia 2017.xlsx`, `Santa Rosalia 2018.xlsx` |
   | `Lluvia (mm)` | `lluvia_(mm)` | `Santa Rosalia 2016.xlsx`, `Santa Rosalia 2017.xlsx`, `Santa Rosalia 2018.xlsx` |
   | `Direccion Viento (°)` | `direccion_viento_(°)` | `Santa Rosalia 2016.xlsx`, `Santa Rosalia 2017.xlsx`, `Santa Rosalia 2018.xlsx` |
   | `Velocidad Viento (m/s)` | `velocidad_viento_(m/s)` | `Santa Rosalia 2016.xlsx`, `Santa Rosalia 2017.xlsx`, `Santa Rosalia 2018.xlsx` |

3. **Decimales con ruido en los Excel** (p. ej. `0.6599999999999999` o `845.888736`): se redondearon a 3 decimales.
4. **Control de rangos.** Según el PDF de observaciones, los CSV de MeerKAD ya venían depurados (valores fuera de rango → vacío), pero los Excel de MAIGRAI "no tuvieron tratamiento de datos". Para que todo el archivo sea homogéneo se aplicaron los mismos rangos válidos del PDF a todos los años.
   Valores reemplazados por vacío:

   | Variable | Fuente | Valores reemplazados | Ejemplos |
   |---|---|---|---|
   | `pres_atmosferica_(hPa)` | MAIGRAI | 561 | 0 |

5. **Fechas repetidas:** no se encontró ninguna.

No se aplicó a los años de MAIGRAI el filtro de "sensor pegado" (más de 20 valores idénticos seguidos) que describe el PDF, porque con datos horarios ese criterio no equivale al de 5 min. Queda pendiente para la etapa de limpieza.

## Para revisar (no se modificó)

- En 2017 la presión vale 0 en muchas horas (valor de relleno del equipo): se reemplazó por vacío al aplicar el rango válido. La presión de 2016 (~894 hPa) es muy distinta a la de 2018 (~795 hPa) y 2021-2025 (~705-745 hPa); revisar antes de usarla.
- La lluvia de 2017 está vacía. No hay datos de 2019, 2020, 2022 ni 2023.

## Datos disponibles por año

Porcentaje de registros con dato en cada variable (— = sin datos).

| Año | Fuente | Registros | `temperatura_(°C)` | `humedad_(%)` | `radiacion_solar_(W/m2)` | `pres_atmosferica_(hPa)` | `lluvia_(mm)` | `direccion_viento_(°)` | `velocidad_viento_(m/s)` |
|---|---|---|---|---|---|---|---|---|---|
| 2016 | MAIGRAI | 440 | 100 % | 100 % | 52 % | 11 % | 100 % | 100 % | 100 % |
| 2017 | MAIGRAI | 8.705 | 100 % | 100 % | 54 % | 94 % | — | 100 % | 100 % |
| 2018 | MAIGRAI | 5.088 | 91 % | 95 % | 51 % | 100 % | 100 % | 100 % | 100 % |
| 2021 | MeerKAD | 4.466 | 100 % | 100 % | 98 % | 100 % | 100 % | 100 % | 100 % |
| 2024 | MeerKAD | 21.329 | 100 % | 100 % | 95 % | 100 % | 100 % | 100 % | 100 % |
| 2025 | MeerKAD | 103.312 | 100 % | 100 % | 96 % | 100 % | 100 % | 100 % | 100 % |
