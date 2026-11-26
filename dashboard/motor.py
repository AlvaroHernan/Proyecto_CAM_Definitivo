"""Motor del dashboard: datos, modelo XGBoost (6 h) y lógica de avisos.

No tiene nada de Streamlit, así que se puede probar o reutilizar por separado.
Reproduce exactamente la preparación de datos y los atributos de XGBoost de los
notebooks 05 y 06 (ver models/README.md).
"""

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------- Rutas ----------------
CARPETA_DASHBOARD = Path(__file__).resolve().parent
RAIZ = CARPETA_DASHBOARD.parent
CARPETA_DATOS = RAIZ / "data" / "clean"
CARPETA_METRICAS = RAIZ / "models"
CARPETA_MODELOS = CARPETA_DASHBOARD / "modelos"

# ---------------- Parámetros del modelo (iguales a los notebooks) ----------------
ESTACIONES = {"La_Lindosa": "La Lindosa", "Los_Micos": "Los Micos"}
HORIZONTE = 6                     # horas hacia adelante
ACUMULADOS = [1, 3, 6, 12, 24, 72, 168]
INI_TRAIN, FIN_TRAIN = "2018-01-01", "2023-12-31 23:00"
INI_VAL, FIN_VAL = "2024-01-01", "2024-12-31 23:00"
SEMILLA = 42

# ---------------- Niveles de aviso (Informe 3.1, tablas 7 y 12) ----------------
# código: (nombre, color de fondo, color de texto, ícono)
NIVELES = {
    # Gris más oscuro que el #8A949E del Informe 3.1: con texto blanco este daba un contraste de
    # 3,1:1 y WCAG 2.1 AA pide 4,5:1 (prueba de accesibilidad de la Actividad 3.3). El nuevo da 4,8:1.
    -1: ("Sin dato", "#69737C", "#FFFFFF", "○"),
    0: ("Normal", "#2E7D32", "#FFFFFF", "●"),
    1: ("Amarillo", "#F2B705", "#1F2933", "▲"),
    2: ("Naranja", "#E8710A", "#1F2933", "▲"),
    3: ("Rojo", "#C62828", "#FFFFFF", "■"),
}
ACCIONES = {
    -1: "Revisar la estación; no suponer que está normal.",
    0: "Seguimiento rutinario.",
    1: "Atención: vigilar con más frecuencia y revisar la lluvia.",
    2: "Alistamiento: preparar recursos y la bocatoma.",
    3: "Respuesta según los protocolos de las autoridades.",
}

# Umbrales provisionales (Informe 3.1, tabla 8). NO son umbrales oficiales.
# amarillo y naranja: metros sobre la base (mínimo de los últimos 7 días).
# rojo: nivel absoluto en metros. El informe lo deja "por definir con la CAM";
# aquí se usa provisionalmente el percentil 99,9 del nivel absoluto, solo para pruebas.
UMBRALES_PROVISIONALES = {
    "La_Lindosa": {"amarillo": 0.48, "naranja": 1.18, "rojo": 1.87},
    "Los_Micos": {"amarillo": 0.37, "naranja": 0.68, "rojo": 1.03},
}
MARGEN_CIERRE = 0.05     # m; el aviso baja cuando todo queda por debajo de (umbral - margen)...
HORAS_CIERRE = 3         # ...durante 3 horas seguidas
HORAS_SIN_DATO = 2       # más de 2 h sin dato válido = "Sin dato"

# Rango probable por condición (RF-08, ajuste de la Actividad 3.3). En 2025 el rango único de
# La Lindosa cubrió solo el 81 % de los errores; separarlo en horas "normales" y "activas"
# (con lluvia en las últimas 6 h o con el río a 10 cm o más sobre su base) lo lleva al 87 %.
SOBRE_BASE_ACTIVO = 0.10     # m


# =====================================================================
# Datos
# =====================================================================
def cargar_serie(estacion):
    """Lee la serie horaria limpia y devuelve las variables que usa el modelo."""
    archivo = CARPETA_DATOS / estacion / f"{estacion}_horario_limpio.csv"
    df = pd.read_csv(archivo, parse_dates=["fecha_hora"], index_col="fecha_hora").asfreq("h")
    datos = pd.DataFrame(index=df.index)
    # Nivel confiable: solo REAL o ALTA (las horas MEDIA son un promedio histórico, no lo que pasó)
    datos["nivel"] = df.nivel_m.where(df.nivel_m_calidad.isin(["REAL", "ALTA"]))
    datos["calidad"] = df.nivel_m_calidad
    datos["lluvia"] = df.lluvia_mm
    datos["base_7d"] = datos.nivel.rolling(168, min_periods=24).min()
    return datos


def calcular_atributos(datos):
    """Los 17 atributos de XGBoost, calculados solo con información hasta la hora t."""
    nivel, indice = datos.nivel, datos.index
    a = pd.DataFrame(index=indice)
    a["nivel_sobre_base7d"] = nivel - datos.base_7d
    for k in [1, 2, 3, 6, 12, 24]:
        a[f"cambio_{k}h"] = nivel - nivel.shift(k)
    for w in ACUMULADOS:
        a[f"lluvia_{w}h"] = datos.lluvia.rolling(w, min_periods=1).sum()
    a["sin_hora"] = np.sin(2 * np.pi * indice.hour / 24)
    a["cos_hora"] = np.cos(2 * np.pi * indice.hour / 24)
    a["sin_dia"] = np.sin(2 * np.pi * indice.dayofyear / 365.25)
    a["cos_dia"] = np.cos(2 * np.pi * indice.dayofyear / 365.25)
    return a


# =====================================================================
# Modelo
# =====================================================================
def ruta_modelo(estacion):
    return CARPETA_MODELOS / f"{estacion}_xgboost_{HORIZONTE}h.json"


def ruta_info(estacion):
    return CARPETA_MODELOS / f"{estacion}_xgboost_{HORIZONTE}h_info.json"


def condicion_activa(atributos):
    """Horas "activas": con lluvia en las últimas 6 h o con el río a 10 cm o más sobre su base."""
    return (atributos["lluvia_6h"] > 0) | (atributos["nivel_sobre_base7d"] >= SOBRE_BASE_ACTIVO)


def rango_por_condicion(error, atributos):
    """Percentiles 5 y 95 del error, por separado para horas normales y activas."""
    activo = condicion_activa(atributos.loc[error.index])
    return {"normal": [float(error[~activo].quantile(0.05)), float(error[~activo].quantile(0.95))],
            "activo": [float(error[activo].quantile(0.05)), float(error[activo].quantile(0.95))]}


def version_modelo(estacion, modelo=None):
    """Identificador corto del modelo: nombre del archivo y huella (hash) de su contenido."""
    if ruta_modelo(estacion).exists() and modelo is None:
        contenido = ruta_modelo(estacion).read_bytes()
    else:
        contenido = bytes(modelo.save_raw("json"))
    return f"{ruta_modelo(estacion).stem} · {hashlib.sha256(contenido).hexdigest()[:10]}"


def entrenar(estacion, datos=None):
    """Entrena XGBoost igual que en los notebooks: 2018-2023 entrena, 2024 valida (parada temprana).

    Devuelve el modelo y un diccionario con información para mostrar (rango probable, árboles...).
    """
    import xgboost as xgb

    datos = cargar_serie(estacion) if datos is None else datos
    atributos = calcular_atributos(datos)
    nivel = datos.nivel
    objetivo = nivel.shift(-HORIZONTE) - nivel          # cambio de nivel entre t y t+6
    usable = objetivo.notna() & nivel.notna()
    fechas = datos.index.to_series()
    ent = usable & fechas.between(INI_TRAIN, FIN_TRAIN)
    val = usable & fechas.between(INI_VAL, FIN_VAL)

    # Mismos hiperparámetros que XGBRegressor en los notebooks, con la interfaz nativa de XGBoost
    parametros = {"objective": "reg:squarederror", "eta": 0.03, "max_depth": 6, "min_child_weight": 5,
                  "subsample": 0.8, "colsample_bytree": 0.8, "seed": SEMILLA,
                  # base_score fijo: así el archivo .json da lo mismo en todas las versiones de XGBoost
                  "base_score": 0.0}
    d_ent = xgb.DMatrix(atributos[ent], label=objetivo[ent])
    d_val = xgb.DMatrix(atributos[val], label=objetivo[val])
    modelo = xgb.train(parametros, d_ent, num_boost_round=3000, evals=[(d_val, "validacion")],
                       early_stopping_rounds=100, verbose_eval=False)
    modelo = modelo[: modelo.best_iteration + 1]   # se queda con los árboles hasta el mejor punto

    # Rango probable del 90 %: percentiles 5 y 95 del error en validación (2024)
    error_val = objetivo[val] - modelo.predict(d_val)
    info = {
        "estacion": estacion,
        "horizonte_h": HORIZONTE,
        "arboles": int(modelo.num_boosted_rounds()),
        "horas_entrenamiento": int(ent.sum()),
        "error_p05_m": float(error_val.quantile(0.05)),
        "error_p95_m": float(error_val.quantile(0.95)),
        "rango_por_condicion": rango_por_condicion(error_val, atributos),
        "atributos": list(atributos.columns),
    }
    # Predicción de control: al cargar el modelo se verifica que dé lo mismo
    muestra = atributos[val].iloc[[0]]
    info["control_fecha"] = str(muestra.index[0])
    info["control_cambio_m"] = float(modelo.predict(xgb.DMatrix(muestra))[0])
    return modelo, info


def cargar_modelo(estacion, datos=None):
    """Carga el modelo guardado en dashboard/modelos; si no existe, lo entrena en el momento."""
    import xgboost as xgb

    if ruta_modelo(estacion).exists() and ruta_info(estacion).exists():
        try:
            modelo = xgb.Booster()
            modelo.load_model(ruta_modelo(estacion))
            info = json.loads(ruta_info(estacion).read_text(encoding="utf-8"))
            datos = cargar_serie(estacion) if datos is None else datos
            muestra = calcular_atributos(datos)[info["atributos"]].loc[[pd.Timestamp(info["control_fecha"])]]
            if abs(modelo.predict(xgb.DMatrix(muestra))[0] - info["control_cambio_m"]) < 1e-4:
                info["version"] = version_modelo(estacion)
                return modelo, info
        except Exception:
            pass
    # Si no hay modelo guardado, está dañado o no da la predicción de control, se entrena (unos segundos)
    modelo, info = entrenar(estacion, datos)
    info["version"] = version_modelo(estacion, modelo) + " (reentrenado al arrancar)"
    return modelo, info


def pronosticar(datos, modelo, info):
    """Pronóstico a 6 h para todas las horas de la serie.

    Para cada hora t solo se usan datos hasta t, así que recorrer la serie hora a hora
    (la "simulación en tiempo real") equivale a calcularlo una sola vez para todas.
    """
    import xgboost as xgb

    atributos = calcular_atributos(datos)[info["atributos"]]
    cambio = modelo.predict(xgb.DMatrix(atributos))
    p = pd.DataFrame(index=datos.index)
    p["pronostico"] = datos.nivel + cambio
    if "rango_por_condicion" in info:
        activo = condicion_activa(atributos)
        r = info["rango_por_condicion"]
        p["condicion"] = np.where(activo, "activa", "normal")
        p["rango_min"] = p.pronostico + np.where(activo, r["activo"][0], r["normal"][0])
        p["rango_max"] = p.pronostico + np.where(activo, r["activo"][1], r["normal"][1])
    else:   # fichas antiguas: un solo rango
        p["condicion"] = "única"
        p["rango_min"] = p.pronostico + info["error_p05_m"]
        p["rango_max"] = p.pronostico + info["error_p95_m"]
    # Confianza normal: todos los atributos disponibles (ventana de entrada completa)
    p["confianza_normal"] = atributos.notna().all(axis=1) & datos.nivel.notna()
    return p


# =====================================================================
# Avisos
# =====================================================================
def _nivel_de_aviso(relativo, absoluto, u):
    """0 normal, 1 amarillo, 2 naranja, 3 rojo (NaN cuenta como normal)."""
    n = np.zeros(len(relativo), dtype=int)
    n[np.nan_to_num(relativo, nan=-9) >= u["amarillo"]] = 1
    n[np.nan_to_num(relativo, nan=-9) >= u["naranja"]] = 2
    n[np.nan_to_num(absoluto, nan=-9) >= u["rojo"]] = 3
    return n


def _por_debajo(relativo, absoluto, nivel_aviso, u, margen):
    """¿El valor está por debajo de (umbral del aviso vigente - margen)?"""
    if np.isnan(relativo) and np.isnan(absoluto):
        return True
    if nivel_aviso == 3:
        return np.isnan(absoluto) or absoluto < u["rojo"] - margen
    umbral = u["amarillo"] if nivel_aviso == 1 else u["naranja"]
    return np.isnan(relativo) or relativo < umbral - margen


def calcular_avisos(datos, pron, umbrales, margen=MARGEN_CIERRE, horas_cierre=HORAS_CIERRE):
    """Estado de aviso hora a hora, con la lógica de la sección 7.3 del Informe 3.1.

    1. Observado: el nivel de la última hora válida alcanza el umbral.
    2. Pronosticado: el pronóstico a 6 h (con confianza normal) alcanza el umbral.
    3. Escalamiento inmediato si se cumple un nivel más alto.
    4. Cierre con histéresis: baja un nivel cuando observado y pronóstico quedan por debajo
       de (umbral - margen) durante 3 horas seguidas.
    5. Sin dato (> 2 h sin nivel válido): se muestra gris, pero el aviso vigente no se cierra.
    """
    # Nivel observado: último dato válido de hace máximo 2 horas
    nivel_obs = datos.nivel.ffill(limit=HORAS_SIN_DATO)
    base = datos.base_7d.ffill(limit=HORAS_SIN_DATO)
    sin_dato = nivel_obs.isna().to_numpy()

    obs_abs = nivel_obs.to_numpy()
    obs_rel = obs_abs - base.to_numpy()
    pro_abs = pron.pronostico.where(pron.confianza_normal).to_numpy()
    pro_rel = pro_abs - base.to_numpy()

    n_obs = _nivel_de_aviso(obs_rel, obs_abs, umbrales)
    n_pro = _nivel_de_aviso(pro_rel, pro_abs, umbrales)

    n = len(datos)
    aviso = np.zeros(n, dtype=int)
    tipo = np.full(n, "", dtype=object)
    actual, horas_bajo = 0, 0
    for i in range(n):
        if not sin_dato[i]:
            nuevo = max(n_obs[i], n_pro[i])
            if nuevo > actual:                      # escalamiento inmediato
                actual, horas_bajo = nuevo, 0
            elif actual > 0:
                bajo = (_por_debajo(obs_rel[i], obs_abs[i], actual, umbrales, margen)
                        and _por_debajo(pro_rel[i], pro_abs[i], actual, umbrales, margen))
                horas_bajo = horas_bajo + 1 if bajo else 0
                if horas_bajo >= horas_cierre:      # baja un nivel
                    actual, horas_bajo = actual - 1, 0
            if actual > 0:
                if n_obs[i] >= actual:
                    tipo[i] = "observado"
                elif n_pro[i] >= actual:
                    tipo[i] = "pronosticado"
                else:
                    tipo[i] = "en cierre"   # ya bajó, esperando las 3 horas para cerrar
        aviso[i] = actual

    return pd.DataFrame({
        "aviso": aviso,                                   # aviso vigente (no se cierra sin datos)
        "estado": np.where(sin_dato, -1, aviso),          # lo que se muestra (gris si no hay dato)
        "tipo": tipo,
        "nivel_obs": obs_abs,
        "sobre_base": obs_rel,
        "base_7d": base.to_numpy(),
    }, index=datos.index)


def bitacora(avisos, nombre_estacion, hasta, desde=None):
    """Lista de episodios entre `desde` y `hasta`.

    Un episodio hidrológico va desde que se activa un aviso (amarillo o más) hasta que vuelve
    a normal. También se listan los periodos sin dato (fallas de la estación).
    """
    tramo = avisos.loc[desde:hasta]
    ultimo = tramo.index[-1]
    filas = []

    def agregar(mascara, aviso, tipo):
        for _, grupo in tramo[mascara].groupby(mascara.ne(mascara.shift()).cumsum()[mascara]):
            codigo = aviso(grupo)
            filas.append({
                "Estación": nombre_estacion,
                "Aviso máximo": f"{NIVELES[codigo][3]} {NIVELES[codigo][0]}",
                "Cómo empezó": tipo(grupo),
                "Inicio": grupo.index[0],
                "Fin": "activo" if grupo.index[-1] == ultimo else grupo.index[-1],
                "Horas": len(grupo),
                "Nivel máx. (m)": grupo.nivel_obs.max() if codigo >= 0 else None,
                "_codigo": codigo,
            })

    agregar(tramo.aviso.gt(0), lambda g: int(g.aviso.max()), lambda g: g.tipo.iloc[0])
    agregar(tramo.estado.eq(-1), lambda g: -1, lambda g: "falla de dato")
    tabla = pd.DataFrame(filas)
    return tabla.sort_values("Inicio", ascending=False) if len(tabla) else tabla


def cargar_metricas(estacion):
    archivo = CARPETA_METRICAS / estacion / "metricas_prueba_2025.csv"
    return pd.read_csv(archivo) if archivo.exists() else pd.DataFrame()
