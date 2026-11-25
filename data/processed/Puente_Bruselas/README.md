# Estación Puente Bruselas — datos consolidados

Archivo: [`Puente_Bruselas_consolidado.csv`](Puente_Bruselas_consolidado.csv) — 208.355 registros, del 2017-01-01 00:00 al 2025-12-31 23:57.

Generado automáticamente por [`src/consolidar_estaciones.py`](../../../src/consolidar_estaciones.py) a partir de los 7 archivos de [`data/raw/Puente_Bruselas`](../../raw/Puente_Bruselas). Los datos crudos no se modificaron. Para regenerarlo: `python src/consolidar_estaciones.py`.

## Formato del archivo

- Separador `,` (coma), decimales con `.` (punto), codificación UTF-8.
- `fecha_hora` en formato `AAAA-MM-DD HH:MM`, ordenada de la más antigua a la más reciente.
- Celda vacía = dato faltante o descartado.
- Variables: `nivel_(m)`, `velocidad_agua_(m/s)`, `lluvia_(mm)`.
- `fuente`: `MAIGRAI` (Excel 2016-2020, un dato por hora) o `MeerKAD` (CSV 2020-2025, un dato cada ~5 min).
- `intervalo_min`: 60 o 5. **Ojo:** la `lluvia_(mm)` de las filas horarias es el acumulado de una hora y la de las filas de 5 min es el acumulado de 5 min. Para comparar años hay que llevar todo a la misma resolución (por ejemplo, sumar la lluvia y promediar el resto por hora o por día).

## Archivos de origen

| Archivo | Fuente | Paso | Registros | Desde | Hasta |
|---|---|---|---|---|---|
| `Puente Bruselas 2017.xlsx` | MAIGRAI | 60 min | 5.530 | 2017-01-01 00:00 | 2017-12-30 11:00 |
| `Puente_Bruselas_2020.csv` | MeerKAD | 5 min | 1.577 | 2020-02-20 19:01 | 2020-12-26 16:35 |
| `Puente_Bruselas_2021.csv` | MeerKAD | 5 min | 5.176 | 2021-01-03 09:55 | 2021-11-05 11:52 |
| `Puente_Bruselas_2022.csv` | MeerKAD | 5 min | 12.917 | 2022-01-24 13:45 | 2022-10-08 23:45 |
| `Puente_Bruselas_2023.csv` | MeerKAD | 5 min | 16.904 | 2023-05-18 11:36 | 2023-12-07 14:18 |
| `Puente_Bruselas_2024.csv` | MeerKAD | 5 min | 68.535 | 2024-02-29 17:18 | 2024-12-31 23:59 |
| `Puente_Bruselas_2025.csv` | MeerKAD | 5 min | 97.716 | 2025-01-01 00:04 | 2025-12-31 23:57 |

Años sin ningún archivo: **2018, 2019**.

## Anomalías encontradas y cómo se corrigieron

1. **Dos formatos distintos.** Los Excel (MAIGRAI) traen la fecha como fecha de Excel y un dato por hora; los CSV (MeerKAD) usan `;` como separador, `,` como decimal, fecha `DD/MM/AAAA H:MM`, codificación Latin-1 (el símbolo `°` aparecía como `�`) y un dato cada ~5 min. Todo se llevó al formato descrito arriba.
2. **Decimales con ruido en los Excel** (p. ej. `0.6599999999999999` o `845.888736`): se redondearon a 3 decimales.
3. **Control de rangos.** Según el PDF de observaciones, los CSV de MeerKAD ya venían depurados (valores fuera de rango → vacío), pero los Excel de MAIGRAI "no tuvieron tratamiento de datos". Para que todo el archivo sea homogéneo se aplicaron los mismos rangos válidos del PDF a todos los años.
   No se encontró ningún valor fuera de rango.

4. **Fechas repetidas:** no se encontró ninguna.

No se aplicó a los años de MAIGRAI el filtro de "sensor pegado" (más de 20 valores idénticos seguidos) que describe el PDF, porque con datos horarios ese criterio no equivale al de 5 min. Queda pendiente para la etapa de limpieza.

## Para revisar (no se modificó)

- No hay datos de 2018 ni 2019 (lo confirma el PDF de observaciones).
- La lluvia está vacía en 2020 y 2023; la velocidad del agua está vacía en 2021.

## Datos disponibles por año

Porcentaje de registros con dato en cada variable (— = sin datos).

| Año | Fuente | Registros | `nivel_(m)` | `velocidad_agua_(m/s)` | `lluvia_(mm)` |
|---|---|---|---|---|---|
| 2017 | MAIGRAI | 5.530 | 95 % | 100 % | 100 % |
| 2020 | MeerKAD | 1.577 | 47 % | 53 % | — |
| 2021 | MeerKAD | 5.176 | 25 % | — | 88 % |
| 2022 | MeerKAD | 12.917 | 67 % | 92 % | 100 % |
| 2023 | MeerKAD | 16.904 | 96 % | 95 % | — |
| 2024 | MeerKAD | 68.535 | 87 % | 63 % | 62 % |
| 2025 | MeerKAD | 97.716 | 90 % | 92 % | 68 % |
