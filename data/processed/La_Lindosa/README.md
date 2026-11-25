# Estación La Lindosa — datos consolidados

Archivo: [`La_Lindosa_consolidado.csv`](La_Lindosa_consolidado.csv) — 607.587 registros, del 2017-06-23 10:00 al 2025-12-31 23:59.

Generado automáticamente por [`src/consolidar_estaciones.py`](../../../src/consolidar_estaciones.py) a partir de los 10 archivos de [`data/raw/La_Lindosa`](../../raw/La_Lindosa). Los datos crudos no se modificaron. Para regenerarlo: `python src/consolidar_estaciones.py`.

## Formato del archivo

- Separador `,` (coma), decimales con `.` (punto), codificación UTF-8.
- `fecha_hora` en formato `AAAA-MM-DD HH:MM`, ordenada de la más antigua a la más reciente.
- Celda vacía = dato faltante o descartado.
- Variables: `nivel_(m)`, `temperatura_(°C)`, `lluvia_(mm)`.
- `fuente`: `MAIGRAI` (Excel 2016-2020, un dato por hora) o `MeerKAD` (CSV 2020-2025, un dato cada ~5 min).
- `intervalo_min`: 60 o 5. **Ojo:** la `lluvia_(mm)` de las filas horarias es el acumulado de una hora y la de las filas de 5 min es el acumulado de 5 min. Para comparar años hay que llevar todo a la misma resolución (por ejemplo, sumar la lluvia y promediar el resto por hora o por día).

## Archivos de origen

| Archivo | Fuente | Paso | Registros | Desde | Hasta |
|---|---|---|---|---|---|
| `La Lindosa 2017.xlsx` | MAIGRAI | 60 min | 3.605 | 2017-06-23 10:00 | 2017-12-31 23:00 |
| `La Lindosa 2018.xlsx` | MAIGRAI | 60 min | 8.566 | 2018-01-01 00:00 | 2018-12-31 23:00 |
| `La Lindosa 2019.xlsx` | MAIGRAI | 60 min | 8.050 | 2019-01-01 00:00 | 2019-12-31 23:00 |
| `La Lindosa 2020.xlsx` | MAIGRAI | 60 min | 1.358 | 2020-01-01 00:00 | 2020-02-26 14:00 |
| `La_Lindosa_2020.csv` | MeerKAD | 5 min | 85.804 | 2020-02-26 14:19 | 2020-12-31 23:57 |
| `La_Lindosa_2021.csv` | MeerKAD | 5 min | 103.936 | 2021-01-01 00:02 | 2021-12-31 23:57 |
| `La_Lindosa_2022.csv` | MeerKAD | 5 min | 98.316 | 2022-01-01 00:02 | 2022-12-31 23:55 |
| `La_Lindosa_2023.csv` | MeerKAD | 5 min | 104.248 | 2023-01-01 00:00 | 2023-12-31 23:56 |
| `La_Lindosa_2024.csv` | MeerKAD | 5 min | 102.664 | 2024-01-01 00:01 | 2024-12-31 23:56 |
| `La_Lindosa_2025.csv` | MeerKAD | 5 min | 91.040 | 2025-01-01 00:01 | 2025-12-31 23:59 |

## Anomalías encontradas y cómo se corrigieron

1. **Dos formatos distintos.** Los Excel (MAIGRAI) traen la fecha como fecha de Excel y un dato por hora; los CSV (MeerKAD) usan `;` como separador, `,` como decimal, fecha `DD/MM/AAAA H:MM`, codificación Latin-1 (el símbolo `°` aparecía como `�`) y un dato cada ~5 min. Todo se llevó al formato descrito arriba.
2. **Decimales con ruido en los Excel** (p. ej. `0.6599999999999999` o `845.888736`): se redondearon a 3 decimales.
3. **Control de rangos.** Según el PDF de observaciones, los CSV de MeerKAD ya venían depurados (valores fuera de rango → vacío), pero los Excel de MAIGRAI "no tuvieron tratamiento de datos". Para que todo el archivo sea homogéneo se aplicaron los mismos rangos válidos del PDF a todos los años.
   No se encontró ningún valor fuera de rango.

4. **Fechas repetidas:** no se encontró ninguna.

No se aplicó a los años de MAIGRAI el filtro de "sensor pegado" (más de 20 valores idénticos seguidos) que describe el PDF, porque con datos horarios ese criterio no equivale al de 5 min. Queda pendiente para la etapa de limpieza.

## Para revisar (no se modificó)

- El año 2020 está repartido en dos archivos: `La Lindosa 2020.xlsx` (1 ene - 26 feb 14:00, horario, MAIGRAI) y `La_Lindosa_2020.csv` (desde 26 feb 14:19, cada 5 min, MeerKAD). No se solapan; se unieron.

## Datos disponibles por año

Porcentaje de registros con dato en cada variable (— = sin datos).

| Año | Fuente | Registros | `nivel_(m)` | `temperatura_(°C)` | `lluvia_(mm)` |
|---|---|---|---|---|---|
| 2017 | MAIGRAI | 3.605 | 100 % | 93 % | 100 % |
| 2018 | MAIGRAI | 8.566 | 100 % | 100 % | 100 % |
| 2019 | MAIGRAI | 8.050 | 100 % | 100 % | 100 % |
| 2020 | MAIGRAI+MeerKAD | 87.162 | 100 % | 97 % | 100 % |
| 2021 | MeerKAD | 103.936 | 100 % | 100 % | 100 % |
| 2022 | MeerKAD | 98.316 | 100 % | 100 % | 100 % |
| 2023 | MeerKAD | 104.248 | 99 % | 97 % | 100 % |
| 2024 | MeerKAD | 102.664 | 94 % | 66 % | 100 % |
| 2025 | MeerKAD | 91.040 | 98 % | 71 % | 100 % |
