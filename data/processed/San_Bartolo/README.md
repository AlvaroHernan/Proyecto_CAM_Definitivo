# Estación San Bartolo — datos consolidados

Archivo: [`San_Bartolo_consolidado.csv`](San_Bartolo_consolidado.csv) — 416.894 registros, del 2017-07-04 17:00 al 2025-12-31 17:55.

Generado automáticamente por [`src/consolidar_estaciones.py`](../../../src/consolidar_estaciones.py) a partir de los 9 archivos de [`data/raw/San_Bartolo`](../../raw/San_Bartolo). Los datos crudos no se modificaron. Para regenerarlo: `python src/consolidar_estaciones.py`.

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
| `San Bartolo 2017.xlsx` | MAIGRAI | 60 min | 3.526 | 2017-07-04 17:00 | 2017-12-31 23:00 |
| `San Bartolo 2018.xlsx` | MAIGRAI | 60 min | 5.938 | 2018-01-01 00:00 | 2018-09-13 11:00 |
| `San Bartolo 2019.xlsx` | MAIGRAI | 60 min | 6.615 | 2019-01-14 12:00 | 2019-12-31 23:00 |
| `San_Bartolo_2020.csv` | MeerKAD | 5 min | 62.496 | 2020-02-12 15:19 | 2020-12-31 23:58 |
| `San_Bartolo_2021.csv` | MeerKAD | 5 min | 68.428 | 2021-01-01 00:03 | 2021-12-31 23:57 |
| `San_Bartolo_2022.csv` | MeerKAD | 5 min | 58.196 | 2022-01-01 00:02 | 2022-12-31 18:25 |
| `San_Bartolo_2023.csv` | MeerKAD | 5 min | 48.479 | 2023-01-01 07:06 | 2023-12-31 23:58 |
| `San_Bartolo_2024.csv` | MeerKAD | 6 min | 70.484 | 2024-01-01 00:04 | 2024-12-31 23:58 |
| `San_Bartolo_2025.csv` | MeerKAD | 6 min | 92.732 | 2025-01-01 00:04 | 2025-12-31 17:55 |

## Anomalías encontradas y cómo se corrigieron

1. **Dos formatos distintos.** Los Excel (MAIGRAI) traen la fecha como fecha de Excel y un dato por hora; los CSV (MeerKAD) usan `;` como separador, `,` como decimal, fecha `DD/MM/AAAA H:MM`, codificación Latin-1 (el símbolo `°` aparecía como `�`) y un dato cada ~5 min. Todo se llevó al formato descrito arriba.
2. **Nombres de variables distintos entre años.** Se renombraron así:

   | Nombre original | Nombre estándar | Archivos |
   |---|---|---|
   | `Velocidad_viento_(m/s)` | `velocidad_viento_(m/s)` | `San Bartolo 2017.xlsx`, `San Bartolo 2018.xlsx`, `San Bartolo 2019.xlsx` |
   | `Direccion_viento_(m/s)` | `direccion_viento_(°)` | `San Bartolo 2017.xlsx`, `San Bartolo 2018.xlsx`, `San Bartolo 2019.xlsx` |

3. **Decimales con ruido en los Excel** (p. ej. `0.6599999999999999` o `845.888736`): se redondearon a 3 decimales.
4. **Control de rangos.** Según el PDF de observaciones, los CSV de MeerKAD ya venían depurados (valores fuera de rango → vacío), pero los Excel de MAIGRAI "no tuvieron tratamiento de datos". Para que todo el archivo sea homogéneo se aplicaron los mismos rangos válidos del PDF a todos los años.
   No se encontró ningún valor fuera de rango.

5. **Fechas repetidas:** no se encontró ninguna.

No se aplicó a los años de MAIGRAI el filtro de "sensor pegado" (más de 20 valores idénticos seguidos) que describe el PDF, porque con datos horarios ese criterio no equivale al de 5 min. Queda pendiente para la etapa de limpieza.

## Para revisar (no se modificó)

- En los Excel 2017-2019 las columnas de viento se llamaban `Velocidad_viento_(m/s)` y `Direccion_viento_(m/s)`. La dirección tenía la unidad equivocada (m/s en vez de °); por sus valores (0-360) es dirección en grados y se renombró a `direccion_viento_(°)`. Los CSV 2020-2025 no traen viento.
- La presión cambia de nivel entre periodos: ~765-900 hPa (2017), ~750-780 hPa (2018-2019), ~780-810 hPa (2021) y ~680-720 hPa (2022-2025). Puede deberse a un cambio de sensor, de calibración o de ubicación; **revisar antes de usar la presión**. En 2020 hay valores hasta 1099,94 hPa (dentro del rango válido pero poco realistas).
- La lluvia está vacía en 2019 y 2023. En 2024-2025 el registro es cada ~6 min en vez de 5 min.

## Datos disponibles por año

Porcentaje de registros con dato en cada variable (— = sin datos).

| Año | Fuente | Registros | `temperatura_(°C)` | `humedad_(%)` | `radiacion_solar_(W/m2)` | `pres_atmosferica_(hPa)` | `lluvia_(mm)` | `direccion_viento_(°)` | `velocidad_viento_(m/s)` |
|---|---|---|---|---|---|---|---|---|---|
| 2017 | MAIGRAI | 3.526 | 99 % | 100 % | 56 % | 100 % | 100 % | 100 % | 57 % |
| 2018 | MAIGRAI | 5.938 | 100 % | 89 % | 49 % | 89 % | 100 % | 89 % | 89 % |
| 2019 | MAIGRAI | 6.615 | 58 % | 58 % | 33 % | 58 % | — | 58 % | 58 % |
| 2020 | MeerKAD | 62.496 | 29 % | 40 % | 17 % | 62 % | 98 % | — | — |
| 2021 | MeerKAD | 68.428 | 96 % | 93 % | 99 % | 96 % | 100 % | — | — |
| 2022 | MeerKAD | 58.196 | 78 % | 6 % | 89 % | 79 % | 65 % | — | — |
| 2023 | MeerKAD | 48.479 | 74 % | 59 % | 79 % | 80 % | — | — | — |
| 2024 | MeerKAD | 70.484 | 67 % | 64 % | 54 % | 67 % | 72 % | — | — |
| 2025 | MeerKAD | 92.732 | 77 % | 77 % | 40 % | 77 % | 45 % | — | — |
