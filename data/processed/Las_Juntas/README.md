# Estación Las Juntas — datos consolidados

Archivo: [`Las_Juntas_consolidado.csv`](Las_Juntas_consolidado.csv) — 547.597 registros, del 2017-06-27 12:00 al 2025-12-31 23:59.

Generado automáticamente por [`src/consolidar_estaciones.py`](../../../src/consolidar_estaciones.py) a partir de los 9 archivos de [`data/raw/Las_Juntas`](../../raw/Las_Juntas). Los datos crudos no se modificaron. Para regenerarlo: `python src/consolidar_estaciones.py`.

## Formato del archivo

- Separador `,` (coma), decimales con `.` (punto), codificación UTF-8.
- `fecha_hora` en formato `AAAA-MM-DD HH:MM`, ordenada de la más antigua a la más reciente.
- Celda vacía = dato faltante o descartado.
- Variables: `nivel_(m)`, `lluvia_(mm)`.
- `fuente`: `MAIGRAI` (Excel 2016-2020, un dato por hora) o `MeerKAD` (CSV 2020-2025, un dato cada ~5 min).
- `intervalo_min`: 60 o 5. **Ojo:** la `lluvia_(mm)` de las filas horarias es el acumulado de una hora y la de las filas de 5 min es el acumulado de 5 min. Para comparar años hay que llevar todo a la misma resolución (por ejemplo, sumar la lluvia y promediar el resto por hora o por día).

## Archivos de origen

| Archivo | Fuente | Paso | Registros | Desde | Hasta |
|---|---|---|---|---|---|
| `Las Juntas_2017.xlsx` | MAIGRAI | 60 min | 3.414 | 2017-06-27 12:00 | 2017-12-31 23:00 |
| `Las Juntas_2018.xlsx` | MAIGRAI | 60 min | 7.950 | 2018-01-01 00:00 | 2018-12-31 23:00 |
| `Las Juntas_2019.xlsx` | MAIGRAI | 60 min | 1.215 | 2019-01-01 00:00 | 2019-02-20 14:00 |
| `Las_Juntas_2020.csv` | MeerKAD | 5 min | 63.200 | 2020-04-10 07:53 | 2020-12-31 23:56 |
| `Las_Juntas_2021.csv` | MeerKAD | 5 min | 101.724 | 2021-01-01 00:01 | 2021-12-30 14:20 |
| `Las_Juntas_2022.csv` | MeerKAD | 5 min | 99.233 | 2022-01-01 00:00 | 2022-12-31 23:58 |
| `Las_Juntas_2023.csv` | MeerKAD | 5 min | 96.688 | 2023-01-01 00:03 | 2023-12-31 23:57 |
| `Las_Juntas_2024.csv` | MeerKAD | 5 min | 70.021 | 2024-01-01 00:02 | 2024-12-31 23:58 |
| `Las_Juntas_2025.csv` | MeerKAD | 5 min | 104.152 | 2025-01-01 00:03 | 2025-12-31 23:59 |

## Anomalías encontradas y cómo se corrigieron

1. **Dos formatos distintos.** Los Excel (MAIGRAI) traen la fecha como fecha de Excel y un dato por hora; los CSV (MeerKAD) usan `;` como separador, `,` como decimal, fecha `DD/MM/AAAA H:MM`, codificación Latin-1 (el símbolo `°` aparecía como `�`) y un dato cada ~5 min. Todo se llevó al formato descrito arriba.
2. **Decimales con ruido en los Excel** (p. ej. `0.6599999999999999` o `845.888736`): se redondearon a 3 decimales.
3. **`Las_Juntas_2020.csv`:** desde el 15/04/2020 22:49 el nivel dejó de escribirse en la columna `nivel_(m)` y pasó a una columna sin nombre (las filas traen dos `;` de más). Se movieron 61.656 valores de vuelta a `nivel_(m)`; nunca se solapan con valores ya existentes.
4. **`Las_Juntas_2020.csv`:** se eliminaron 1 columna(s) sin nombre y vacía(s).
5. **Control de rangos.** Según el PDF de observaciones, los CSV de MeerKAD ya venían depurados (valores fuera de rango → vacío), pero los Excel de MAIGRAI "no tuvieron tratamiento de datos". Para que todo el archivo sea homogéneo se aplicaron los mismos rangos válidos del PDF a todos los años.
   No se encontró ningún valor fuera de rango.

6. **Fechas repetidas:** no se encontró ninguna.

No se aplicó a los años de MAIGRAI el filtro de "sensor pegado" (más de 20 valores idénticos seguidos) que describe el PDF, porque con datos horarios ese criterio no equivale al de 5 min. Queda pendiente para la etapa de limpieza.

## Para revisar (no se modificó)

- El nivel de 2019 (Excel) está completamente vacío.

## Datos disponibles por año

Porcentaje de registros con dato en cada variable (— = sin datos).

| Año | Fuente | Registros | `nivel_(m)` | `lluvia_(mm)` |
|---|---|---|---|---|
| 2017 | MAIGRAI | 3.414 | 61 % | 100 % |
| 2018 | MAIGRAI | 7.950 | 98 % | 100 % |
| 2019 | MAIGRAI | 1.215 | — | 100 % |
| 2020 | MeerKAD | 63.200 | 100 % | 100 % |
| 2021 | MeerKAD | 101.724 | 84 % | 100 % |
| 2022 | MeerKAD | 99.233 | 85 % | 91 % |
| 2023 | MeerKAD | 96.688 | 34 % | 69 % |
| 2024 | MeerKAD | 70.021 | 96 % | 100 % |
| 2025 | MeerKAD | 104.152 | 67 % | 100 % |
