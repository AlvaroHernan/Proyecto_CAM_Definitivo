"""Pruebas automáticas del motor del dashboard (Actividad 3.3, requisito RNF-11).

Ejecutar desde la carpeta raíz del repositorio:

    python -m pip install pytest
    python -m pytest tests -v

Comprueban con los datos reales (data/clean) y con series sintéticas que:
- los modelos guardados son los evaluados (predicción de control y error en 2025),
- el pronóstico de cada hora solo usa datos hasta esa hora (sin "ver el futuro"),
- el rango probable cubre cerca del 90 % de los errores,
- las reglas de avisos (observado, pronosticado, escalamiento, cierre con histéresis, sin dato)
  se cumplen como las define el Informe 3.1, sección 7.3.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "dashboard"))
import motor  # noqa: E402

U = {"amarillo": 0.48, "naranja": 1.18, "rojo": 1.87}


# ---------------------------------------------------------------------------
# Con los datos reales
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module", params=list(motor.ESTACIONES))
def estacion(request):
    e = request.param
    datos = motor.cargar_serie(e)
    modelo, info = motor.cargar_modelo(e, datos)
    pron = motor.pronosticar(datos, modelo, info)
    return e, datos, modelo, info, pron


def test_modelo_guardado_reproduce_la_prediccion_de_control(estacion):
    e, datos, modelo, info, pron = estacion
    assert "reentrenado" not in info["version"], "el archivo guardado no reprodujo la predicción de control"
    t = pd.Timestamp(info["control_fecha"])
    cambio = pron.pronostico.loc[t] - datos.nivel.loc[t]
    assert abs(cambio - info["control_cambio_m"]) <= 0.001     # RNF-11: diferencia ≤ 0,001 m


def test_error_2025_igual_al_reportado(estacion):
    """RMSE a 6 h en 2025 igual al del Objetivo 2 (±0,2 cm) y mejor que la persistencia."""
    e, datos, modelo, info, pron = estacion
    futuro = datos.nivel.shift(-motor.HORIZONTE)
    ok = pron.confianza_normal & futuro.notna() & (datos.index.year == 2025)
    rmse = np.sqrt(((futuro - pron.pronostico)[ok] ** 2).mean()) * 100
    rmse_persistencia = np.sqrt(((futuro - datos.nivel)[ok] ** 2).mean()) * 100
    referencia = motor.cargar_metricas(e)
    referencia = referencia[(referencia.h == 6) & (referencia.modelo == "XGBoost") &
                            (referencia.subconjunto == "todas")].RMSE_cm.iloc[0]
    assert abs(rmse - referencia) <= 0.2
    assert rmse < rmse_persistencia


def test_pronostico_no_usa_datos_futuros(estacion):
    """Calcular con la serie cortada en t da lo mismo que con la serie completa."""
    e, datos, modelo, info, pron = estacion
    for t in pd.to_datetime(["2024-11-13 07:00", "2025-05-10 12:00"]):
        corto = datos.loc[:t].copy()
        p_corto = motor.pronosticar(corto, modelo, info)
        assert p_corto.pronostico.loc[t] == pytest.approx(pron.pronostico.loc[t], abs=1e-6)
        assert bool(p_corto.confianza_normal.loc[t]) == bool(pron.confianza_normal.loc[t])


def test_cobertura_del_rango_probable(estacion):
    """El rango probable cubre 90 % en 2024 (calibración) y al menos 85 % en 2025 (prueba)."""
    e, datos, modelo, info, pron = estacion
    futuro = datos.nivel.shift(-motor.HORIZONTE)
    dentro = (futuro >= pron.rango_min) & (futuro <= pron.rango_max)
    for anio, minimo in [(2024, 0.88), (2025, 0.85)]:
        ok = pron.confianza_normal & futuro.notna() & (datos.index.year == anio)
        assert dentro[ok].mean() >= minimo


def test_crecida_del_13_de_noviembre_de_2024():
    """Ejemplo del Informe 3.2: amarillo a las 04:00, naranja a las 07:00 y rojo a las 08:00."""
    datos = motor.cargar_serie("La_Lindosa")
    modelo, info = motor.cargar_modelo("La_Lindosa", datos)
    avisos = motor.calcular_avisos(datos, motor.pronosticar(datos, modelo, info),
                                   motor.UMBRALES_PROVISIONALES["La_Lindosa"])
    dia = avisos.loc["2024-11-13 03:00":"2024-11-13 08:00", "aviso"].tolist()
    assert dia == [0, 1, 1, 1, 2, 3]


# ---------------------------------------------------------------------------
# Con series sintéticas: reglas de avisos
# ---------------------------------------------------------------------------
def serie(niveles, base=0.50):
    indice = pd.date_range("2024-01-01", periods=len(niveles), freq="h")
    datos = pd.DataFrame({"nivel": niveles, "lluvia": 0.0, "base_7d": base, "calidad": "REAL"}, index=indice)
    return datos


def sin_pronostico(datos, valores=None):
    p = pd.DataFrame(index=datos.index)
    p["pronostico"] = np.nan if valores is None else valores
    p["confianza_normal"] = p.pronostico.notna()
    return p


def test_aviso_observado_y_escalamiento_inmediato():
    datos = serie([0.6, 1.0, 1.7, 2.0])          # sobre la base: 0,1 / 0,5 / 1,2 / 1,5 (rojo por nivel 2,0)
    a = motor.calcular_avisos(datos, sin_pronostico(datos), U)
    assert a.aviso.tolist() == [0, 1, 2, 3]
    assert set(a.tipo.iloc[1:]) == {"observado"}


def test_cierre_con_histeresis_baja_un_nivel_tras_3_horas():
    # amarillo, luego 4 horas por debajo de (0,48 - 0,05) sobre la base
    datos = serie([1.0, 0.7, 0.7, 0.7, 0.7])
    a = motor.calcular_avisos(datos, sin_pronostico(datos), U)
    assert a.aviso.tolist() == [1, 1, 1, 0, 0]
    assert a.tipo.iloc[1] == "en cierre"


def test_nivel_que_oscila_cerca_del_umbral_no_cierra_el_aviso():
    # 0,95 m = 0,45 m sobre la base: debajo del umbral, pero dentro del margen de 5 cm
    datos = serie([1.0, 0.95, 0.95, 0.95, 0.95, 0.95])
    a = motor.calcular_avisos(datos, sin_pronostico(datos), U)
    assert a.aviso.tolist() == [1] * 6


def test_aviso_pronosticado_solo_con_confianza_normal():
    datos = serie([0.6] * 3)
    pron = sin_pronostico(datos, [0.6, 1.1, 1.1])            # pronóstico 0,6 m sobre la base
    pron.loc[pron.index[2], "confianza_normal"] = False       # tercera hora sin ventana completa
    a = motor.calcular_avisos(datos, pron, U)
    assert a.aviso.tolist() == [0, 1, 1]                      # la tercera sigue por histéresis
    assert a.tipo.tolist() == ["", "pronosticado", "en cierre"]


def test_sin_dato_despues_de_2_horas_y_aviso_vigente_no_se_cierra():
    datos = serie([1.0, np.nan, np.nan, np.nan, np.nan])
    a = motor.calcular_avisos(datos, sin_pronostico(datos), U)
    assert a.estado.tolist() == [1, 1, 1, -1, -1]             # gris desde la tercera hora sin dato
    assert a.aviso.tolist() == [1, 1, 1, 1, 1]                # el aviso sigue vigente


def test_bitacora_lista_episodios_y_fallas():
    datos = serie([0.6, 1.0, 1.0, 0.6, 0.6, 0.6, 0.6, np.nan, np.nan, np.nan, 0.6])
    a = motor.calcular_avisos(datos, sin_pronostico(datos), U)
    tabla = motor.bitacora(a, "Prueba", a.index[-1])
    assert sorted(tabla["Cómo empezó"]) == ["falla de dato", "observado"]


def test_umbrales_provisionales_ordenados():
    for u in motor.UMBRALES_PROVISIONALES.values():
        assert 0 < u["amarillo"] < u["naranja"]
