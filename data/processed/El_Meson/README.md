# Estación El Meson — datos consolidados

Archivo: [`El_Meson_consolidado.csv`](El_Meson_consolidado.csv) — 547.502 registros, del 2017-07-04 18:00 al 2025-12-31 23:58.

Generado automáticamente por [`src/consolidar_estaciones.py`](../../../src/consolidar_estaciones.py) a partir de los 9 archivos de [`data/raw/El_Meson`](../../raw/El_Meson). Los datos crudos no se modificaron. Para regenerarlo: `python src/consolidar_estaciones.py`.

## Formato del archivo

- Separador `,` (coma), decimales con `.` (punto), codificación UTF-8.
- `fecha_hora` en formato `AAAA-MM-DD HH:MM`, ordenada de la más antigua a la más reciente.
- Celda vacía = dato faltante o descartado.
- Variables: `temperatura_(°C)`, `humedad_(%)`, `radiacion_solar_(W/m2)`, `pres_atmosferica_(hPa)`, `lluvia_(mm)`, `direccion_viento_(°)`, `velocidad_viento_(m/s)`, `voltaje_bateria_(VDC)`.
- `fuente`: `MAIGRAI` (Excel 2016-2020, un dato por hora) o `MeerKAD` (CSV 2020-2025, un dato cada ~5 min).
- `intervalo_min`: 60 o 5. **Ojo:** la `lluvia_(mm)` de las filas horarias es el acumulado de una hora y la de las filas de 5 min es el acumulado de 5 min. Para comparar años hay que llevar todo a la misma resolución (por ejemplo, sumar la lluvia y promediar el resto por hora o por día).

## Archivos de origen

| Archivo | Fuente | Paso | Registros | Desde | Hasta |
|---|---|---|---|---|---|
| `El Meson 2017.xlsx` | MAIGRAI | 60 min | 3.433 | 2017-07-04 18:00 | 2017-12-31 23:00 |
| `El Meson 2018.xlsx` | MAIGRAI | 60 min | 8.566 | 2018-01-01 00:00 | 2018-12-31 23:00 |
| `El Meson 2019.xlsx` | MAIGRAI | 60 min | 7.125 | 2019-01-01 00:00 | 2019-12-31 23:00 |
| `El_Meson_2020.csv` | MeerKAD | 5 min | 62.130 | 2020-02-24 12:12 | 2020-12-30 03:05 |
| `El_Meson_2021.csv` | MeerKAD | 5 min | 96.813 | 2021-01-04 08:08 | 2021-12-31 23:59 |
| `El_Meson_2022.csv` | MeerKAD | 5 min | 99.240 | 2022-01-01 00:04 | 2022-12-30 14:00 |
| `El_Meson_2023.csv` | MeerKAD | 5 min | 65.541 | 2023-01-01 00:02 | 2023-12-31 23:58 |
| `El_Meson_2024.csv` | MeerKAD | 5 min | 102.079 | 2024-01-01 00:04 | 2024-12-31 23:56 |
| `El_Meson_2025.csv` | MeerKAD | 5 min | 102.575 | 2025-01-01 00:01 | 2025-12-31 23:58 |

## Anomalías encontradas y cómo se corrigieron

1. **Dos formatos distintos.** Los Excel (MAIGRAI) traen la fecha como fecha de Excel y un dato por hora; los CSV (MeerKAD) usan `;` como separador, `,` como decimal, fecha `DD/MM/AAAA H:MM`, codificación Latin-1 (el símbolo `°` aparecía como `�`) y un dato cada ~5 min. Todo se llevó al formato descrito arriba.
2. **Decimales con ruido en los Excel** (p. ej. `0.6599999999999999` o `845.888736`): se redondearon a 3 decimales.
3. **Control de rangos.** Según el PDF de observaciones, los CSV de MeerKAD ya venían depurados (valores fuera de rango → vacío), pero los Excel de MAIGRAI "no tuvieron tratamiento de datos". Para que todo el archivo sea homogéneo se aplicaron los mismos rangos válidos del PDF a todos los años.
   No se encontró ningún valor fuera de rango.

4. **Fechas repetidas:** no se encontró ninguna.

No se aplicó a los años de MAIGRAI el filtro de "sensor pegado" (más de 20 valores idénticos seguidos) que describe el PDF, porque con datos horarios ese criterio no equivale al de 5 min. Queda pendiente para la etapa de limpieza.

## Para revisar (no se modificó)

- En 2020 el CSV trae `voltaje_bateria_(VDC)` en lugar de `pres_atmosferica_(hPa)`. No es un cambio de nombre: son variables distintas, por eso se dejaron en columnas separadas (la presión queda vacía en 2020 y el voltaje vacío en los demás años).
- La presión de 2017 (Excel) varía entre ~710 y ~901 hPa y la de 2018 baja hasta ~547 hPa, mientras que 2019-2025 está estable en ~810-850 hPa. Son valores dentro del rango válido pero probablemente erróneos; revisar antes de usar la presión de 2017-2018.

## Datos disponibles por año

Porcentaje de registros con dato en cada variable (— = sin datos).

| Año | Fuente | Registros | `temperatura_(°C)` | `humedad_(%)` | `radiacion_solar_(W/m2)` | `pres_atmosferica_(hPa)` | `lluvia_(mm)` | `direccion_viento_(°)` | `velocidad_viento_(m/s)` | `voltaje_bateria_(VDC)` |
|---|---|---|---|---|---|---|---|---|---|---|
| 2017 | MAIGRAI | 3.433 | 55 % | 100 % | 56 % | 89 % | 100 % | 55 % | 55 % | — |
| 2018 | MAIGRAI | 8.566 | 100 % | 100 % | 56 % | 87 % | 100 % | 100 % | 100 % | — |
| 2019 | MAIGRAI | 7.125 | 100 % | 100 % | 56 % | 100 % | 100 % | 100 % | 100 % | — |
| 2020 | MeerKAD | 62.130 | 100 % | 100 % | 100 % | — | 100 % | 97 % | 97 % | 100 % |
| 2021 | MeerKAD | 96.813 | 100 % | 100 % | 100 % | 100 % | 100 % | 100 % | 100 % | — |
| 2022 | MeerKAD | 99.240 | 100 % | 100 % | 100 % | 100 % | 100 % | 100 % | 100 % | — |
| 2023 | MeerKAD | 65.541 | 100 % | 100 % | 99 % | 100 % | 100 % | 100 % | 100 % | — |
| 2024 | MeerKAD | 102.079 | 100 % | 100 % | 71 % | 100 % | 100 % | 100 % | 100 % | — |
| 2025 | MeerKAD | 102.575 | 100 % | 100 % | 49 % | 100 % | 100 % | 100 % | 100 % | — |
