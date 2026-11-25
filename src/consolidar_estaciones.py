"""
Consolidación de datos crudos por estación.

Lee todos los archivos anuales de cada estación en ``data/raw/<estacion>/``
(Excel .xlsx de 2016-2020 exportados con MAIGRAI y .csv de 2020-2025
exportados con MeerKAD), corrige las diferencias de formato entre años y
escribe un único archivo por estación:

    data/processed/<estacion>/<estacion>_consolidado.csv
    data/processed/<estacion>/README.md   (anomalías encontradas y correcciones)

Los archivos de ``data/raw`` NO se modifican.

Uso (desde la carpeta raíz del repositorio):

    python src/consolidar_estaciones.py
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
RAW_DIR = RAIZ / "data" / "raw"
OUT_DIR = RAIZ / "data" / "processed"

# ---------------------------------------------------------------------------
# Nombres estándar de las variables (los mismos que usan los CSV de MeerKAD y
# los PDF de observaciones) y orden de las columnas en el archivo consolidado.
# ---------------------------------------------------------------------------
COLUMNAS_ESTANDAR = [
    "fecha_hora",
    "nivel_(m)",
    "velocidad_agua_(m/s)",
    "temperatura_(°C)",
    "humedad_(%)",
    "radiacion_solar_(W/m2)",
    "rad_u_(W/m2)",
    "pres_atmosferica_(hPa)",
    "lluvia_(mm)",
    "direccion_viento_(°)",
    "velocidad_viento_(m/s)",
    "voltaje_bateria_(VDC)",
]
COLUMNAS_CONTROL = ["fuente", "intervalo_min"]


def _clave(nombre: str) -> str:
    """Normaliza un encabezado para compararlo: minúsculas, sin tildes ni
    símbolos raros, sin espacios ni signos de puntuación."""
    s = unicodedata.normalize("NFKD", str(nombre))
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.replace("\ufffd", "")  # caracter de reemplazo por mala codificación
    return re.sub(r"[^a-z0-9]", "", s.lower())


# Cada encabezado encontrado en los archivos crudos -> nombre estándar.
# Las claves están normalizadas con _clave().
ALIAS = {
    # fecha
    "fechahora": "fecha_hora",
    "fecha": "fecha_hora",
    # nivel / caudal
    "nivelm": "nivel_(m)",
    "velocidadaguams": "velocidad_agua_(m/s)",
    # temperatura
    "temperaturac": "temperatura_(°C)",
    # humedad
    "humedad": "humedad_(%)",
    "humedadrelativa": "humedad_(%)",
    # radiación
    "radiacionsolarwm2": "radiacion_solar_(W/m2)",
    "raduwm2": "rad_u_(W/m2)",
    # presión
    "presatmosfericahpa": "pres_atmosferica_(hPa)",
    "presionatmosfericahpa": "pres_atmosferica_(hPa)",
    # lluvia
    "lluviamm": "lluvia_(mm)",
    # viento
    "direccionviento": "direccion_viento_(°)",
    "direccionvientoms": "direccion_viento_(°)",  # unidad mal escrita en San Bartolo
    "velocidadvientoms": "velocidad_viento_(m/s)",
    # otros
    "voltajebateriavdc": "voltaje_bateria_(VDC)",
}

# Rangos válidos de los PDF "Observaciones <estación>.pdf" (límites inclusivos).
RANGOS = {
    "temperatura_(°C)": (0, 50),
    "humedad_(%)": (0, 100),
    "lluvia_(mm)": (0, 100),
    "radiacion_solar_(W/m2)": (0, 2000),
    "direccion_viento_(°)": (0, 361),
    "velocidad_viento_(m/s)": (0, 90),
    "voltaje_bateria_(VDC)": (0.1, 20),
    "nivel_(m)": (0, np.inf),
    "pres_atmosferica_(hPa)": (500, 1100),
}

# ---------------------------------------------------------------------------
# Observaciones manuales por estación (revisión de los datos, no automáticas).
# Se copian al README de cada estación en la sección "Para revisar".
# ---------------------------------------------------------------------------
NOTAS_REVISAR = {
    "El_Batan": [
        "Los CSV de MeerKAD traen una columna `Rad,_U (W/m2)` (valores entre 0,03 y 0,39) que no aparece "
        "en los Excel ni en el PDF de observaciones. Se conservó con el nombre `rad_u_(W/m2)`; "
        "**confirmar con el proveedor qué mide** (posiblemente radiación UV).",
        "La presión atmosférica solo existe en 2017-2018 (Excel). Los CSV 2020-2025 no traen esa variable.",
        "La lluvia está vacía en 2020, 2021 y 2022 y parcialmente en 2023.",
    ],
    "El_Meson": [
        "En 2020 el CSV trae `voltaje_bateria_(VDC)` en lugar de `pres_atmosferica_(hPa)`. "
        "No es un cambio de nombre: son variables distintas, por eso se dejaron en columnas separadas "
        "(la presión queda vacía en 2020 y el voltaje vacío en los demás años).",
        "La presión de 2017 (Excel) varía entre ~710 y ~901 hPa y la de 2018 baja hasta ~547 hPa, "
        "mientras que 2019-2025 está estable en ~810-850 hPa. Son valores dentro del rango válido pero "
        "probablemente erróneos; revisar antes de usar la presión de 2017-2018.",
    ],
    "La_Lindosa": [
        "El año 2020 está repartido en dos archivos: `La Lindosa 2020.xlsx` (1 ene - 26 feb 14:00, horario, "
        "MAIGRAI) y `La_Lindosa_2020.csv` (desde 26 feb 14:19, cada 5 min, MeerKAD). No se solapan; se unieron.",
    ],
    "Las_Juntas": [
        "El nivel de 2019 (Excel) está completamente vacío.",
    ],
    "Los_Micos": [],
    "Puente_Bruselas": [
        "No hay datos de 2018 ni 2019 (lo confirma el PDF de observaciones).",
        "La lluvia está vacía en 2020 y 2023; la velocidad del agua está vacía en 2021.",
    ],
    "San_Bartolo": [
        "En los Excel 2017-2019 las columnas de viento se llamaban `Velocidad_viento_(m/s)` y "
        "`Direccion_viento_(m/s)`. La dirección tenía la unidad equivocada (m/s en vez de °); por sus valores "
        "(0-360) es dirección en grados y se renombró a `direccion_viento_(°)`. Los CSV 2020-2025 no traen viento.",
        "La presión cambia de nivel entre periodos: ~765-900 hPa (2017), ~750-780 hPa (2018-2019), "
        "~780-810 hPa (2021) y ~680-720 hPa (2022-2025). Puede deberse a un cambio de sensor, de calibración o "
        "de ubicación; **revisar antes de usar la presión**. En 2020 hay valores hasta 1099,94 hPa (dentro del "
        "rango válido pero poco realistas).",
        "La lluvia está vacía en 2019 y 2023. En 2024-2025 el registro es cada ~6 min en vez de 5 min.",
    ],
    "San_Benito": [
        "El nivel de 2017-2018 (Excel) está entre 0 y 7,77 m, mientras que en 2023-2025 está entre ~0,4 y "
        "1,5 m. Probablemente cambió la referencia (cero) del sensor; **no son comparables sin ajustar**.",
        "El nivel está vacío en 2020, 2021 y 2022. No hay datos de 2019.",
    ],
    "Santa_Rosalia": [
        "En 2017 la presión vale 0 en muchas horas (valor de relleno del equipo): se reemplazó por vacío al "
        "aplicar el rango válido. La presión de 2016 (~894 hPa) es muy distinta a la de 2018 (~795 hPa) y "
        "2021-2025 (~705-745 hPa); revisar antes de usarla.",
        "La lluvia de 2017 está vacía. No hay datos de 2019, 2020, 2022 ni 2023.",
    ],
}


@dataclass
class Registro:
    """Lo que pasó con cada archivo crudo, para escribir el README."""

    archivo: str
    fuente: str
    intervalo: int
    filas: int
    inicio: pd.Timestamp | None
    fin: pd.Timestamp | None
    renombres: dict = field(default_factory=dict)
    notas: list = field(default_factory=list)


# ---------------------------------------------------------------------------
# Lectura
# ---------------------------------------------------------------------------
def leer_excel(ruta: Path) -> pd.DataFrame:
    df = pd.read_excel(ruta, header=0)
    # Columnas sin encabezado y sin datos (formato sobrante en el Excel)
    df = df.loc[:, ~(df.columns.astype(str).str.startswith("Unnamed") & df.isna().all())]
    df = df.dropna(how="all")
    return df


def leer_csv(ruta: Path) -> pd.DataFrame:
    return pd.read_csv(ruta, sep=";", decimal=",", encoding="latin-1")


def corregir_casos_especiales(estacion: str, ruta: Path, df: pd.DataFrame, reg: Registro) -> pd.DataFrame:
    """Correcciones puntuales detectadas al revisar los archivos."""
    sin_nombre = [c for c in df.columns if str(c).startswith("Unnamed")]
    if estacion == "Las_Juntas" and ruta.name == "Las_Juntas_2020.csv" and sin_nombre:
        vacias = [c for c in sin_nombre if df[c].isna().all()]
        con_datos = [c for c in sin_nombre if df[c].notna().any()]
        for c in con_datos:
            choque = (df["nivel_(m)"].notna() & df[c].notna()).sum()
            if choque:
                raise ValueError(f"{ruta}: la columna {c} se solapa con nivel_(m) en {choque} filas")
            n = int(df[c].notna().sum())
            df["nivel_(m)"] = df["nivel_(m)"].fillna(df[c])
            desde = pd.to_datetime(df.loc[df[c].notna(), df.columns[0]], format="%d/%m/%Y %H:%M").min()
            reg.notas.append(
                f"desde el {desde:%d/%m/%Y %H:%M} el nivel dejó de escribirse en la columna `nivel_(m)` y pasó a "
                f"una columna sin nombre (las filas traen dos `;` de más). Se movieron {_num(n)} valores de vuelta "
                "a `nivel_(m)`; nunca se solapan con valores ya existentes."
            )
        df = df.drop(columns=vacias + con_datos)
        if vacias:
            reg.notas.append(f"se eliminaron {len(vacias)} columna(s) sin nombre y vacía(s).")
    sin_nombre = [c for c in df.columns if str(c).startswith("Unnamed")]
    if sin_nombre:
        if all(df[c].isna().all() for c in sin_nombre):
            df = df.drop(columns=sin_nombre)
        else:
            raise ValueError(f"{ruta}: columnas sin nombre con datos no previstas: {sin_nombre}")
    return df


def estandarizar_columnas(df: pd.DataFrame, reg: Registro) -> pd.DataFrame:
    nuevos = {}
    for c in df.columns:
        clave = _clave(c)
        if clave not in ALIAS:
            raise KeyError(f"{reg.archivo}: encabezado no reconocido {c!r} (clave {clave!r}). Agréguelo a ALIAS.")
        estandar = ALIAS[clave]
        nuevos[c] = estandar
        if str(c).replace("\ufffd", "°") != estandar:
            reg.renombres[str(c)] = estandar
    df = df.rename(columns=nuevos)
    if df.columns.duplicated().any():
        raise ValueError(f"{reg.archivo}: dos columnas terminan con el mismo nombre estándar")
    return df


def leer_archivo(estacion: str, ruta: Path) -> tuple[pd.DataFrame, Registro]:
    es_excel = ruta.suffix.lower() == ".xlsx"
    df = leer_excel(ruta) if es_excel else leer_csv(ruta)
    reg = Registro(
        archivo=ruta.name,
        fuente="MAIGRAI" if es_excel else "MeerKAD",
        intervalo=0,
        filas=len(df),
        inicio=None,
        fin=None,
    )
    df = corregir_casos_especiales(estacion, ruta, df, reg)
    df = estandarizar_columnas(df, reg)

    if es_excel:
        df["fecha_hora"] = pd.to_datetime(df["fecha_hora"])
    else:
        df["fecha_hora"] = pd.to_datetime(df["fecha_hora"], format="%d/%m/%Y %H:%M")

    for c in df.columns:
        if c != "fecha_hora":
            df[c] = pd.to_numeric(df[c], errors="raise").astype(float)

    if es_excel:
        # Los Excel guardan valores como 0.6599999999999999 o 845.888736 (conversiones
        # internas); se redondean a 3 decimales para quitar ese ruido.
        num = [c for c in df.columns if c != "fecha_hora"]
        df[num] = df[num].round(3)

    paso = df["fecha_hora"].diff().dt.total_seconds().div(60).mode()
    reg.intervalo = int(paso.iloc[0]) if len(paso) else 0
    reg.inicio, reg.fin = df["fecha_hora"].min(), df["fecha_hora"].max()

    años = df["fecha_hora"].dt.year.unique()
    año_nombre = re.search(r"(20\d\d)", ruta.name)
    if año_nombre and (len(años) != 1 or int(año_nombre.group(1)) != años[0]):
        reg.notas.append(f"el archivo contiene años {sorted(años)} distintos al de su nombre.")

    df["fuente"] = reg.fuente
    df["intervalo_min"] = 60 if es_excel else 5
    return df, reg


# ---------------------------------------------------------------------------
# Consolidación
# ---------------------------------------------------------------------------
def aplicar_rangos(df: pd.DataFrame) -> pd.DataFrame:
    """Reemplaza por vacío los valores fuera de rango. Devuelve una tabla con
    el número de valores reemplazados por variable y fuente."""
    filas = []
    for var, (lo, hi) in RANGOS.items():
        if var not in df.columns:
            continue
        fuera = df[var].notna() & ~df[var].between(lo, hi)
        for fuente, n in df.loc[fuera, "fuente"].value_counts().items():
            ejemplos = df.loc[fuera & (df["fuente"] == fuente), var].unique()[:5]
            filas.append((var, fuente, int(n), ", ".join(f"{v:g}" for v in ejemplos)))
        df.loc[fuera, var] = np.nan
    return pd.DataFrame(filas, columns=["variable", "fuente", "reemplazados", "ejemplos"])


def consolidar_estacion(carpeta: Path) -> dict:
    estacion = carpeta.name
    archivos = sorted(
        [p for p in carpeta.iterdir() if p.suffix.lower() in (".csv", ".xlsx")],
        key=lambda p: (re.search(r"(20\d\d)", p.name).group(1), p.suffix != ".xlsx"),
    )
    partes, registros = [], []
    for ruta in archivos:
        df, reg = leer_archivo(estacion, ruta)
        partes.append(df)
        registros.append(reg)

    df = pd.concat(partes, ignore_index=True)
    df = df.sort_values(["fecha_hora", "fuente"], kind="stable").reset_index(drop=True)

    # Fechas repetidas (p. ej. si dos archivos se solapan): se deja la de MeerKAD
    # (ya depurada), que queda de última al ordenar por fuente.
    dup = df["fecha_hora"].duplicated(keep="last")
    n_dup = int(dup.sum())
    df = df.loc[~dup]

    qc = aplicar_rangos(df)

    columnas = [c for c in COLUMNAS_ESTANDAR if c in df.columns] + COLUMNAS_CONTROL
    df = df[columnas]

    destino = OUT_DIR / estacion
    destino.mkdir(parents=True, exist_ok=True)
    salida = destino / f"{estacion}_consolidado.csv"
    df.to_csv(salida, index=False, encoding="utf-8", date_format="%Y-%m-%d %H:%M", float_format="%.3f")
    # Quitar ceros sobrantes (0.660 -> 0.66) para que el archivo sea más liviano.
    texto = salida.read_text(encoding="utf-8")
    texto = re.sub(r"(\.\d*?)0+(?=,|\n)", r"\1", texto)
    texto = re.sub(r"\.(?=,|\n)", "", texto)
    salida.write_text(texto, encoding="utf-8")

    escribir_readme(estacion, df, registros, qc, n_dup, archivos, carpeta)
    return {"estacion": estacion, "filas": len(df), "inicio": df.fecha_hora.min(), "fin": df.fecha_hora.max(),
            "archivos": len(archivos), "columnas": [c for c in columnas if c not in ("fecha_hora", *COLUMNAS_CONTROL)]}


# ---------------------------------------------------------------------------
# README por estación
# ---------------------------------------------------------------------------
def _fmt(ts) -> str:
    return "" if ts is None or pd.isna(ts) else pd.Timestamp(ts).strftime("%Y-%m-%d %H:%M")


def _num(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def tabla_cobertura(df: pd.DataFrame) -> str:
    variables = [c for c in df.columns if c not in ("fecha_hora", *COLUMNAS_CONTROL)]
    año = df["fecha_hora"].dt.year
    enc = "| Año | Fuente | Registros | " + " | ".join(f"`{v}`" for v in variables) + " |"
    sep = "|" + "---|" * (3 + len(variables))
    lineas = [enc, sep]
    for a, g in df.groupby(año):
        fuentes = "+".join(sorted(g["fuente"].unique()))
        celdas = []
        for v in variables:
            pct = 100 * g[v].notna().mean()
            celdas.append("—" if pct == 0 else f"{pct:.0f} %")
        lineas.append(f"| {a} | {fuentes} | {_num(len(g))} | " + " | ".join(celdas) + " |")
    return "\n".join(lineas)


def escribir_readme(estacion, df, registros, qc, n_dup, archivos, carpeta):
    nombre = estacion.replace("_", " ")
    años_con_datos = sorted(df["fecha_hora"].dt.year.unique())
    faltantes = [a for a in range(años_con_datos[0], años_con_datos[-1] + 1) if a not in años_con_datos]
    variables = [c for c in df.columns if c not in ("fecha_hora", *COLUMNAS_CONTROL)]

    L = []
    L.append(f"# Estación {nombre} — datos consolidados\n")
    L.append(
        f"Archivo: [`{estacion}_consolidado.csv`]({estacion}_consolidado.csv) — "
        f"{_num(len(df))} registros, del {_fmt(df.fecha_hora.min())} al {_fmt(df.fecha_hora.max())}.\n"
    )
    L.append(
        "Generado automáticamente por [`src/consolidar_estaciones.py`](../../../src/consolidar_estaciones.py) "
        f"a partir de los {len(archivos)} archivos de [`data/raw/{estacion}`](../../raw/{estacion}). "
        "Los datos crudos no se modificaron. Para regenerarlo: `python src/consolidar_estaciones.py`.\n"
    )

    L.append("## Formato del archivo\n")
    L.append("- Separador `,` (coma), decimales con `.` (punto), codificación UTF-8.")
    L.append("- `fecha_hora` en formato `AAAA-MM-DD HH:MM`, ordenada de la más antigua a la más reciente.")
    L.append("- Celda vacía = dato faltante o descartado.")
    L.append(f"- Variables: {', '.join(f'`{v}`' for v in variables)}.")
    L.append("- `fuente`: `MAIGRAI` (Excel 2016-2020, un dato por hora) o `MeerKAD` (CSV 2020-2025, un dato cada ~5 min).")
    L.append(
        "- `intervalo_min`: 60 o 5. **Ojo:** la `lluvia_(mm)` de las filas horarias es el acumulado de una hora y la de "
        "las filas de 5 min es el acumulado de 5 min. Para comparar años hay que llevar todo a la misma resolución "
        "(por ejemplo, sumar la lluvia y promediar el resto por hora o por día).\n"
    )

    L.append("## Archivos de origen\n")
    L.append("| Archivo | Fuente | Paso | Registros | Desde | Hasta |")
    L.append("|---|---|---|---|---|---|")
    for r in registros:
        L.append(f"| `{r.archivo}` | {r.fuente} | {r.intervalo} min | {_num(r.filas)} | {_fmt(r.inicio)} | {_fmt(r.fin)} |")
    L.append("")
    if faltantes:
        L.append(f"Años sin ningún archivo: **{', '.join(map(str, faltantes))}**.\n")

    L.append("## Anomalías encontradas y cómo se corrigieron\n")
    n = 1
    L.append(
        f"{n}. **Dos formatos distintos.** Los Excel (MAIGRAI) traen la fecha como fecha de Excel y un dato por hora; "
        "los CSV (MeerKAD) usan `;` como separador, `,` como decimal, fecha `DD/MM/AAAA H:MM`, codificación Latin-1 "
        "(el símbolo `°` aparecía como `�`) y un dato cada ~5 min. Todo se llevó al formato descrito arriba."
    )
    n += 1
    renombres = {}
    for r in registros:
        for viejo, nuevo in r.renombres.items():
            renombres.setdefault((viejo, nuevo), []).append(r.archivo)
    if renombres:
        L.append(f"{n}. **Nombres de variables distintos entre años.** Se renombraron así:\n")
        L.append("   | Nombre original | Nombre estándar | Archivos |")
        L.append("   |---|---|---|")
        for (viejo, nuevo), arch in renombres.items():
            L.append(f"   | `{viejo}` | `{nuevo}` | {', '.join(f'`{a}`' for a in arch)} |")
        L.append("")
        n += 1
    hay_excel = any(r.fuente == "MAIGRAI" for r in registros)
    if hay_excel:
        L.append(
            f"{n}. **Decimales con ruido en los Excel** (p. ej. `0.6599999999999999` o `845.888736`): se redondearon a 3 decimales."
        )
        n += 1
    for r in registros:
        for nota in r.notas:
            L.append(f"{n}. **`{r.archivo}`:** {nota}")
            n += 1
    if hay_excel:
        L.append(
            f"{n}. **Control de rangos.** Según el PDF de observaciones, los CSV de MeerKAD ya venían depurados "
            "(valores fuera de rango → vacío), pero los Excel de MAIGRAI \"no tuvieron tratamiento de datos\". "
            "Para que todo el archivo sea homogéneo se aplicaron los mismos rangos válidos del PDF a todos los años."
        )
    else:
        L.append(f"{n}. **Control de rangos.** Se verificaron los rangos válidos del PDF de observaciones en todos los años.")
    if qc.empty:
        L.append("   No se encontró ningún valor fuera de rango.\n")
    else:
        L.append("   Valores reemplazados por vacío:\n")
        L.append("   | Variable | Fuente | Valores reemplazados | Ejemplos |")
        L.append("   |---|---|---|---|")
        for _, q in qc.iterrows():
            L.append(f"   | `{q.variable}` | {q.fuente} | {_num(q.reemplazados)} | {q.ejemplos} |")
        L.append("")
    n += 1
    L.append(
        f"{n}. **Fechas repetidas:** "
        + (f"se encontraron {_num(n_dup)}; se dejó una sola fila por fecha (la de MeerKAD si había ambas)." if n_dup else "no se encontró ninguna.")
        + "\n"
    )
    L.append(
        "No se aplicó a los años de MAIGRAI el filtro de \"sensor pegado\" (más de 20 valores idénticos seguidos) que "
        "describe el PDF, porque con datos horarios ese criterio no equivale al de 5 min. Queda pendiente para la etapa "
        "de limpieza.\n"
    )

    notas = NOTAS_REVISAR.get(estacion, [])
    if notas:
        L.append("## Para revisar (no se modificó)\n")
        for nota in notas:
            L.append(f"- {nota}")
        L.append("")

    L.append("## Datos disponibles por año\n")
    L.append("Porcentaje de registros con dato en cada variable (— = sin datos).\n")
    L.append(tabla_cobertura(df))
    L.append("")

    (OUT_DIR / estacion / "README.md").write_text("\n".join(L), encoding="utf-8")


def main():
    estaciones = sorted(p for p in RAW_DIR.iterdir() if p.is_dir())
    resumen = []
    for carpeta in estaciones:
        print(f"Consolidando {carpeta.name} ...", flush=True)
        resumen.append(consolidar_estacion(carpeta))
    print()
    for r in resumen:
        print(f"{r['estacion']:<16} {r['archivos']:>2} archivos  {r['filas']:>8} filas  {r['inicio']} -> {r['fin']}")
    return resumen


if __name__ == "__main__":
    main()
