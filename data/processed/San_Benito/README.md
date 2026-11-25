# Estación San Benito — datos consolidados

Archivo: [`San_Benito_consolidado.csv`](San_Benito_consolidado.csv) — 430.039 registros, del 2017-01-01 00:00 al 2025-12-31 23:59.

Generado automáticamente por [`src/consolidar_estaciones.py`](../../../src/consolidar_estaciones.py) a partir de los 8 archivos de [`data/raw/San_Benito`](../../raw/San_Benito). Los datos crudos no se modificaron. Para regenerarlo: `python src/consolidar_estaciones.py`.

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
| `San Benito 2017.xlsx` | MAIGRAI | 60 min | 8.760 | 2017-01-01 00:00 | 2017-12-31 23:00 |
| `San Benito 2018.xlsx` | MAIGRAI | 60 min | 738 | 2018-01-01 00:00 | 2018-01-31 17:00 |
| `San_Benito_2020.csv` | MeerKAD | 5 min | 88.125 | 2020-02-13 14:59 | 2020-12-31 23:55 |
| `San_Benito_2021.csv` | MeerKAD | 5 min | 103.370 | 2021-01-01 00:00 | 2021-12-31 23:59 |
| `San_Benito_2022.csv` | MeerKAD | 5 min | 69.744 | 2022-01-01 00:04 | 2022-11-28 10:18 |
| `San_Benito_2023.csv` | MeerKAD | 5 min | 13.584 | 2023-10-18 14:58 | 2023-12-31 23:55 |
| `San_Benito_2024.csv` | MeerKAD | 5 min | 89.150 | 2024-01-01 00:00 | 2024-12-31 23:58 |
| `San_Benito_2025.csv` | MeerKAD | 5 min | 56.568 | 2025-01-01 00:03 | 2025-12-31 23:59 |

Años sin ningún archivo: **2019**.

## Anomalías encontradas y cómo se corrigieron

1. **Dos formatos distintos.** Los Excel (MAIGRAI) traen la fecha como fecha de Excel y un dato por hora; los CSV (MeerKAD) usan `;` como separador, `,` como decimal, fecha `DD/MM/AAAA H:MM`, codificación Latin-1 (el símbolo `°` aparecía como `�`) y un dato cada ~5 min. Todo se llevó al formato descrito arriba.
2. **Decimales con ruido en los Excel** (p. ej. `0.6599999999999999` o `845.888736`): se redondearon a 3 decimales.
3. **Control de rangos.** Según el PDF de observaciones, los CSV de MeerKAD ya venían depurados (valores fuera de rango → vacío), pero los Excel de MAIGRAI "no tuvieron tratamiento de datos". Para que todo el archivo sea homogéneo se aplicaron los mismos rangos válidos del PDF a todos los años.
   No se encontró ningún valor fuera de rango.

4. **Fechas repetidas:** no se encontró ninguna.

No se aplicó a los años de MAIGRAI el filtro de "sensor pegado" (más de 20 valores idénticos seguidos) que describe el PDF, porque con datos horarios ese criterio no equivale al de 5 min. Queda pendiente para la etapa de limpieza.

## Para revisar (no se modificó)

- El nivel de 2017-2018 (Excel) está entre 0 y 7,77 m, mientras que en 2023-2025 está entre ~0,4 y 1,5 m. Probablemente cambió la referencia (cero) del sensor; **no son comparables sin ajustar**.
- El nivel está vacío en 2020, 2021 y 2022. No hay datos de 2019.

## Datos disponibles por año

Porcentaje de registros con dato en cada variable (— = sin datos).

| Año | Fuente | Registros | `nivel_(m)` | `velocidad_agua_(m/s)` | `lluvia_(mm)` |
|---|---|---|---|---|---|
| 2017 | MAIGRAI | 8.760 | 97 % | 98 % | 100 % |
| 2018 | MAIGRAI | 738 | 100 % | 100 % | 100 % |
| 2020 | MeerKAD | 88.125 | — | 99 % | 52 % |
| 2021 | MeerKAD | 103.370 | — | 95 % | 100 % |
| 2022 | MeerKAD | 69.744 | — | 92 % | 100 % |
| 2023 | MeerKAD | 13.584 | 92 % | 87 % | 100 % |
| 2024 | MeerKAD | 89.150 | 94 % | 93 % | 100 % |
| 2025 | MeerKAD | 56.568 | 99 % | 93 % | 99 % |
