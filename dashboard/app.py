"""Dashboard de alertas tempranas · río Las Ceibas (Actividad 3.2).

Ejecutar desde la carpeta raíz del repositorio:

    streamlit run dashboard/app.py

No hay conexión en vivo con las estaciones, así que el "tiempo real" se simula
reproduciendo la serie histórica limpia (data/clean) hora por hora.
"""

import html
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

sys.path.insert(0, str(Path(__file__).resolve().parent))   # para encontrar motor.py desde cualquier carpeta
import motor  # noqa: E402

st.set_page_config(page_title="Alertas río Las Ceibas", page_icon="🌊", layout="wide")

AZUL, GRIS_TEXTO, GRIS_LINEA = "#1F4E79", "#52606D", "#CBD2D9"
AZUL_LLUVIA = "#6C9BD2"
INICIO_SIMULACION = pd.Timestamp("2024-11-13 00:00")   # justo antes de unas crecientes de noviembre de 2024


# =====================================================================
# Utilidades de formato
# =====================================================================
def num(x, dec=2):
    """Número con coma decimal, como se escribe en Colombia."""
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "—"
    return f"{x:,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def hora(t):
    return t.strftime("%d/%m/%Y %H:%M")


def etiqueta_estado(codigo, tamano="1rem"):
    nombre, fondo, texto, icono = motor.NIVELES[codigo]
    return (f"<span style='background:{fondo};color:{texto};padding:2px 10px;border-radius:6px;"
            f"font-weight:700;font-size:{tamano};white-space:nowrap'>{icono} {nombre}</span>")


# =====================================================================
# Acceso (un solo perfil: administrador)
# =====================================================================
def clave_admin():
    try:
        return st.secrets["ADMIN_PASSWORD"]
    except Exception:
        return "admin"   # clave por defecto si no se configuró ninguna (ver README)


def pantalla_acceso():
    st.title("🌊 Alertas tempranas · río Las Ceibas")
    st.write("Ingrese la contraseña de administrador para entrar al tablero.")
    with st.form("acceso"):
        clave = st.text_input("Contraseña", type="password")
        if st.form_submit_button("Entrar", type="primary"):
            if clave == clave_admin():
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Contraseña incorrecta.")
    if clave_admin() == "admin":
        st.caption("Se está usando la contraseña por defecto. Cámbiela antes de publicar el tablero (ver README).")


# =====================================================================
# Datos y modelo (se calculan una sola vez y quedan en memoria)
# =====================================================================
@st.cache_resource(show_spinner="Cargando datos y modelo…")
def preparar(estacion):
    datos = motor.cargar_serie(estacion)
    modelo, info = motor.cargar_modelo(estacion, datos)
    pron = motor.pronosticar(datos, modelo, info)
    return datos, pron, info


@st.cache_data(show_spinner=False)
def avisos_de(estacion, amarillo, naranja, rojo, margen):
    datos, pron, _ = preparar(estacion)
    return motor.calcular_avisos(datos, pron, {"amarillo": amarillo, "naranja": naranja, "rojo": rojo}, margen)


def umbrales_actuales(estacion):
    return st.session_state.umbrales[estacion]


def avisos(estacion):
    u = umbrales_actuales(estacion)
    return avisos_de(estacion, u["amarillo"], u["naranja"], u["rojo"], st.session_state.margen)


# =====================================================================
# Barra lateral: simulación y administración
# =====================================================================
def barra_lateral(primera, ultima):
    st.sidebar.header("⏱️ Simulación en tiempo real")
    st.sidebar.caption("Reproduce los datos históricos como si llegaran en vivo, una hora a la vez.")

    fecha = st.sidebar.date_input("Fecha de inicio", value=st.session_state.t.date(),
                                  min_value=primera.date(), max_value=ultima.date(), format="DD/MM/YYYY")
    hora_ini = st.sidebar.selectbox("Hora de inicio", range(24), index=st.session_state.t.hour,
                                    format_func=lambda h: f"{h:02d}:00")
    if st.sidebar.button("Ir a esa fecha", width="stretch"):
        st.session_state.t = pd.Timestamp(fecha) + pd.Timedelta(hours=hora_ini)
        st.session_state.reproduciendo = False
        st.rerun()

    c1, c2, c3 = st.sidebar.columns(3)
    if c1.button("⏮ −1 h", width="stretch"):
        st.session_state.t -= pd.Timedelta(hours=1)
    if st.session_state.reproduciendo:
        if c2.button("⏸ Pausa", width="stretch"):
            st.session_state.reproduciendo = False
            st.rerun()
    elif c2.button("▶ Play", width="stretch", type="primary"):
        st.session_state.reproduciendo = True
        st.rerun()
    if c3.button("+1 h ⏭", width="stretch"):
        st.session_state.t += pd.Timedelta(hours=1)

    st.session_state.paso = st.sidebar.select_slider(
        "Velocidad (horas simuladas cada 2 segundos)", options=[1, 2, 3, 6, 12, 24], value=st.session_state.paso)
    st.session_state.t = min(max(st.session_state.t, primera), ultima)

    st.sidebar.divider()
    st.sidebar.header("⚙️ Administración de umbrales")
    st.sidebar.caption("Valores provisionales del Informe 3.1 (tabla 8). No son oficiales: "
                       "se ajustan aquí mientras la CAM define los definitivos.")
    for estacion, nombre in motor.ESTACIONES.items():
        u = st.session_state.umbrales[estacion]
        with st.sidebar.expander(nombre):
            u["amarillo"] = st.number_input("Amarillo (m sobre la base)", 0.05, 5.0, u["amarillo"], 0.01,
                                            key=f"am_{estacion}", format="%.2f")
            u["naranja"] = st.number_input("Naranja (m sobre la base)", 0.05, 5.0, u["naranja"], 0.01,
                                           key=f"na_{estacion}", format="%.2f")
            u["rojo"] = st.number_input("Rojo (nivel absoluto, m)", 0.1, 10.0, u["rojo"], 0.01,
                                        key=f"ro_{estacion}", format="%.2f")
            if u["naranja"] <= u["amarillo"]:
                st.warning("El umbral naranja debería ser mayor que el amarillo.")
    st.session_state.margen = st.sidebar.number_input(
        "Margen de cierre (m)", 0.0, 0.5, st.session_state.margen, 0.01, format="%.2f",
        help="Un aviso baja de nivel cuando el nivel observado y el pronosticado quedan por debajo de "
             "(umbral − margen) durante 3 horas seguidas.")
    if st.sidebar.button("Restablecer valores provisionales", width="stretch"):
        for clave in list(st.session_state):
            if clave[:3] in ("am_", "na_", "ro_"):
                del st.session_state[clave]
        st.session_state.umbrales = {k: dict(v) for k, v in motor.UMBRALES_PROVISIONALES.items()}
        st.session_state.margen = motor.MARGEN_CIERRE
        st.rerun()
    st.sidebar.caption("Los cambios valen mientras la sesión esté abierta.")

    st.sidebar.divider()
    if st.sidebar.button("Cerrar sesión", width="stretch"):
        st.session_state.autenticado = False
        st.session_state.reproduciendo = False
        st.rerun()


# =====================================================================
# Panel general
# =====================================================================
def resumen_estacion(estacion, t):
    datos, pron, info = preparar(estacion)
    a = avisos(estacion).loc[t]
    validos = datos.nivel.loc[:t].dropna()
    ultimo = validos.index[-1] if len(validos) else None
    p = pron.loc[t]
    return {
        "estacion": estacion,
        "nombre": motor.ESTACIONES[estacion],
        "estado": int(a.estado),
        "aviso": int(a.aviso),
        "tipo": a.tipo,
        "nivel": a.nivel_obs,
        "sobre_base": a.sobre_base,
        "base": a.base_7d,
        "ultimo_dato": ultimo,
        "horas_sin_dato": (t - ultimo) / pd.Timedelta(hours=1) if ultimo is not None else np.nan,
        "tendencia_3h": datos.nivel.get(t) - datos.nivel.get(t - pd.Timedelta(hours=3)),
        "pronostico": p.pronostico if p.confianza_normal else np.nan,
        "rango": (p.rango_min, p.rango_max),
        "confianza": bool(p.confianza_normal),
        "lluvia_24h": datos.lluvia.loc[t - pd.Timedelta(hours=23):t].sum(),
    }


def franja_cuenca(resumenes, t):
    peor = max(resumenes, key=lambda r: (r["estado"] if r["estado"] >= 0 else 0.5))
    codigo = peor["estado"]
    nombre, fondo, texto, icono = motor.NIVELES[codigo]
    if codigo <= 0 and all(r["estado"] == 0 for r in resumenes):
        mensaje = "Todas las estaciones en estado normal."
    elif codigo == -1:
        mensaje = f"{peor['nombre']} sin datos válidos. {motor.ACCIONES[-1]}"
    else:
        mensaje = f"Aviso {nombre.lower()} ({peor['tipo']}) en {peor['nombre']}. {motor.ACCIONES[codigo]}"
    st.markdown(
        f"<div style='background:{fondo};color:{texto};padding:14px 20px;border-radius:10px;margin-bottom:8px'>"
        f"<div style='font-size:1.5rem;font-weight:800'>{icono} Cuenca: {nombre.upper()}</div>"
        f"<div style='font-size:1.05rem'>{html.escape(mensaje)}</div>"
        f"<div style='font-size:0.9rem;opacity:0.9'>Hora simulada: {hora(t)} (hora de Colombia)</div></div>",
        unsafe_allow_html=True)


def tarjeta(r):
    with st.container(border=True):
        c1, c2 = st.columns([3, 2])
        c1.subheader(r["nombre"])
        c2.markdown(f"<div style='text-align:right;padding-top:10px'>{etiqueta_estado(r['estado'], '1.1rem')}</div>",
                    unsafe_allow_html=True)
        if r["estado"] == -1 and r["aviso"] > 0:
            st.warning(f"Sin datos, pero el aviso {motor.NIVELES[r['aviso']][0].lower()} sigue vigente.")
        elif r["aviso"] > 0:
            st.caption(f"Aviso {r['tipo']}. {motor.ACCIONES[r['aviso']]}")

        m1, m2, m3 = st.columns(3)
        tendencia = r["tendencia_3h"]
        if np.isnan(tendencia):
            m1.metric("Nivel actual", f"{num(r['nivel'])} m")
        elif abs(tendencia) < 0.005:
            m1.metric("Nivel actual", f"{num(r['nivel'])} m", "estable en 3 h", delta_color="off")
        else:   # subir se muestra en rojo y bajar en verde
            m1.metric("Nivel actual", f"{num(r['nivel'])} m", f"{num(100 * tendencia, 0)} cm en 3 h",
                      delta_color="inverse")
        if np.isnan(r["pronostico"]):
            m2.metric(f"Pronóstico a {motor.HORIZONTE} h", "—")
            m2.caption("Sin pronóstico: faltan datos recientes.")
        else:
            m2.metric(f"Pronóstico a {motor.HORIZONTE} h", f"{num(r['pronostico'])} m")
            m2.caption(f"Rango probable: {num(r['rango'][0])} a {num(r['rango'][1])} m")
        m3.metric("Lluvia últimas 24 h", f"{num(r['lluvia_24h'], 0 if r['lluvia_24h'] >= 100 else 1)} mm")

        if r["ultimo_dato"] is not None:
            horas = int(r["horas_sin_dato"])
            hace = "dato de esta hora" if horas == 0 else f"último dato hace {horas} h"
            st.caption(f"Nivel sobre la base de 7 días: {num(r['sobre_base'])} m · {hace} "
                       f"({hora(r['ultimo_dato'])}).")


# =====================================================================
# Gráfico de la estación
# =====================================================================
def grafico_estacion(estacion, t, horas_atras):
    datos, pron, _ = preparar(estacion)
    u = umbrales_actuales(estacion)
    a = avisos(estacion).loc[t]
    desde = t - pd.Timedelta(hours=horas_atras)
    tramo = datos.loc[desde:t]
    p = pron.loc[t]
    futuro = t + pd.Timedelta(hours=motor.HORIZONTE)

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.72, 0.28], vertical_spacing=0.06,
                        subplot_titles=("Nivel del río (m)", "Lluvia horaria (mm)"))

    # Nivel observado (solo horas REAL o ALTA; los huecos quedan en blanco)
    fig.add_trace(go.Scatter(x=tramo.index, y=tramo.nivel, name="Nivel observado", mode="lines",
                             line=dict(color=AZUL, width=2),
                             hovertemplate="%{x|%d/%m %H:%M}<br>Nivel: %{y:.2f} m<extra></extra>"), 1, 1)

    # Pronóstico a 6 h con su rango probable
    valores_y = list(tramo.nivel.dropna())
    if p.confianza_normal:
        fig.add_trace(go.Scatter(
            x=[t, futuro], y=[datos.nivel.loc[t], p.pronostico], name=f"Pronóstico a {motor.HORIZONTE} h",
            mode="lines+markers", line=dict(color=AZUL, width=2, dash="dash"), marker=dict(size=[0, 10]),
            error_y=dict(type="data", symmetric=False, array=[0, p.rango_max - p.pronostico],
                         arrayminus=[0, p.pronostico - p.rango_min], color=GRIS_TEXTO, thickness=1.5, width=6),
            hovertemplate="%{x|%d/%m %H:%M}<br>Pronóstico: %{y:.2f} m<extra></extra>"), 1, 1)
        valores_y += [p.rango_min, p.rango_max]

    # Umbrales como líneas horizontales de su color
    base = a.base_7d
    lineas = []
    if not np.isnan(base):
        lineas += [(base + u["amarillo"], 1, f"Amarillo (base + {num(u['amarillo'])} m)"),
                   (base + u["naranja"], 2, f"Naranja (base + {num(u['naranja'])} m)")]
    lineas.append((u["rojo"], 3, f"Rojo ({num(u['rojo'])} m)"))
    tope = max(valores_y) if valores_y else 1.0
    piso = min(valores_y) if valores_y else 0.0
    fuera = []
    for y, codigo, texto in lineas:
        if y <= tope * 1.25 + 0.1:
            fig.add_hline(y=y, line=dict(color=motor.NIVELES[codigo][1], width=1.5, dash="dot"), row=1, col=1,
                          annotation_text=texto, annotation_position="top left",
                          annotation_font=dict(size=11, color=GRIS_TEXTO))
            tope = max(tope, y)
        else:
            fuera.append(texto)

    # Lluvia
    fig.add_trace(go.Bar(x=tramo.index, y=tramo.lluvia, name="Lluvia", marker_color=AZUL_LLUVIA,
                         hovertemplate="%{x|%d/%m %H:%M}<br>Lluvia: %{y:.1f} mm<extra></extra>"), 2, 1)

    # Línea vertical "ahora"
    for fila in (1, 2):
        fig.add_vline(x=t, line=dict(color=GRIS_TEXTO, width=1), row=fila, col=1)
    fig.add_annotation(x=t, y=1, yref="paper", text="ahora", showarrow=False, yanchor="bottom",
                       font=dict(color=GRIS_TEXTO, size=11))

    margen = max(0.05, 0.08 * (tope - piso))
    fig.update_yaxes(range=[piso - margen, tope + margen], row=1, col=1, gridcolor="#EEF1F4")
    fig.update_yaxes(rangemode="tozero", row=2, col=1, gridcolor="#EEF1F4")
    fig.update_xaxes(range=[desde, futuro + pd.Timedelta(hours=1)], gridcolor="#EEF1F4", tickformat="%H:%M<br>%d/%m")
    fig.update_layout(height=520, margin=dict(l=10, r=10, t=40, b=10), hovermode="x unified",
                      legend=dict(orientation="h", y=-0.12, x=0, yanchor="top"), plot_bgcolor="white",
                      bargap=0.15)
    st.plotly_chart(fig, width="stretch")
    if fuera:
        st.caption("Fuera de la escala de la gráfica: umbral " + ", ".join(fuera) + ".")


def detalle(t):
    c1, c2 = st.columns([2, 3])
    estacion = c1.radio("Estación", list(motor.ESTACIONES), format_func=motor.ESTACIONES.get, horizontal=True)
    ventanas = {"72 horas": 72, "7 días": 168, "30 días": 720}
    ventana = c2.radio("Ventana", list(ventanas), horizontal=True)
    grafico_estacion(estacion, t, ventanas[ventana])

    datos, pron, info = preparar(estacion)
    tramo = datos.lluvia.loc[:t]
    a1, a2, a3 = st.columns(3)
    a1.metric("Lluvia 24 h", f"{num(tramo.iloc[-24:].sum(), 1)} mm")
    a2.metric("Lluvia 72 h", f"{num(tramo.iloc[-72:].sum(), 1)} mm")
    a3.metric("Lluvia 7 días", f"{num(tramo.iloc[-168:].sum(), 1)} mm")
    st.info("El pronóstico no incluye lluvia futura: una creciente causada por lluvia que todavía no ha caído "
            "no se puede anticipar. El rango probable cubre el 90 % de los errores del modelo en 2024. "
            "Este es un aviso técnico de apoyo a la decisión; no reemplaza la alerta oficial.", icon="ℹ️")


# =====================================================================
# Bitácora y modelo
# =====================================================================
def vista_bitacora(t):
    dias = st.radio("Mostrar los últimos", [7, 30, 90, 365], index=1, horizontal=True,
                    format_func=lambda d: f"{d} días")
    tablas = [motor.bitacora(avisos(e), n, t, t - pd.Timedelta(days=dias)) for e, n in motor.ESTACIONES.items()]
    tabla = pd.concat([x for x in tablas if len(x)], ignore_index=True) if any(len(x) for x in tablas) else None
    if tabla is None:
        st.success("Sin avisos ni fallas de datos en este periodo.")
        return
    solo_hidro = st.checkbox("Ocultar fallas de datos", value=False)
    if solo_hidro:
        tabla = tabla[tabla._codigo >= 0]
    tabla = tabla.sort_values("Inicio", ascending=False).drop(columns="_codigo")
    tabla["Inicio"] = tabla.Inicio.dt.strftime("%d/%m/%Y %H:%M")
    tabla["Fin"] = tabla.Fin.map(lambda f: f if isinstance(f, str) else f.strftime("%d/%m/%Y %H:%M"))
    st.dataframe(tabla, hide_index=True, width="stretch",
                 column_config={"Nivel máx. (m)": st.column_config.NumberColumn(format="%.2f")})
    st.caption("Un episodio va desde que se activa un aviso hasta que vuelve a normal. "
               "«Cómo empezó» indica si lo activó el nivel observado o el pronóstico del modelo.")


def vista_modelo():
    st.markdown(f"""
**Modelo:** XGBoost (árboles de decisión con *boosting*), elegido en la Actividad 2.4 como el mejor en las dos
estaciones. Predice el **cambio de nivel en las próximas {motor.HORIZONTE} horas** con el nivel reciente,
la lluvia acumulada (1 h a 7 días) y la hora y el día del año. Se entrenó con 2018-2023, se ajustó con 2024
y se evaluó con 2025. Detalles en `models/README.md`.
""")
    filas = []
    for estacion, nombre in motor.ESTACIONES.items():
        _, _, info = preparar(estacion)
        m = motor.cargar_metricas(estacion)
        if len(m):
            m = m[(m.h == motor.HORIZONTE) & (m.subconjunto == "todas")].set_index("modelo")
            filas.append({"Estación": nombre,
                          "Error típico XGBoost (cm)": m.loc["XGBoost", "RMSE_cm"],
                          "Error típico si se supone que no cambia (cm)": m.loc["Persistencia", "RMSE_cm"],
                          "Mejora (%)": m.loc["XGBoost", "mejora_vs_persistencia_%"],
                          "NSE": m.loc["XGBoost", "NSE"],
                          "Rango probable (cm)": f"{num(100 * info['error_p05_m'], 1)} a +{num(100 * info['error_p95_m'], 1)}"})
    if filas:
        st.subheader(f"Desempeño en 2025 a {motor.HORIZONTE} h")
        st.dataframe(pd.DataFrame(filas), hide_index=True, width="stretch",
                     column_config={c: st.column_config.NumberColumn(format="%.1f")
                                    for c in ["Error típico XGBoost (cm)",
                                              "Error típico si se supone que no cambia (cm)", "Mejora (%)"]}
                     | {"NSE": st.column_config.NumberColumn(format="%.2f")})

    st.subheader("Niveles de aviso")
    niveles = pd.DataFrame([{"Estado": f"{motor.NIVELES[c][3]} {motor.NIVELES[c][0]}",
                             "Acción sugerida": motor.ACCIONES[c]} for c in [0, 1, 2, 3, -1]])
    st.dataframe(niveles, hide_index=True, width="stretch")
    st.subheader("Umbrales en uso")
    umbrales = pd.DataFrame([{"Estación": n,
                              "Amarillo (m sobre la base)": st.session_state.umbrales[e]["amarillo"],
                              "Naranja (m sobre la base)": st.session_state.umbrales[e]["naranja"],
                              "Rojo (nivel, m)": st.session_state.umbrales[e]["rojo"]}
                             for e, n in motor.ESTACIONES.items()])
    st.dataframe(umbrales, hide_index=True, width="stretch")
    st.markdown(f"""
**Cómo se activa un aviso** (Informe 3.1, sección 7.3):

1. **Observado:** el nivel de la última hora válida alcanza el umbral.
2. **Pronosticado:** el pronóstico a {motor.HORIZONTE} h alcanza el umbral (solo si el modelo tuvo todos sus datos de entrada).
3. Si se cumple un nivel más alto, el aviso **sube de inmediato**.
4. El aviso **baja un nivel** cuando el nivel observado y el pronosticado quedan por debajo de
   (umbral − margen) durante {motor.HORAS_CIERRE} horas seguidas.
5. **Sin dato:** si pasan más de {motor.HORAS_SIN_DATO} h sin un nivel válido, la estación se muestra en gris.
   Un aviso vigente no se cierra por falta de datos.

La **base** es el nivel mínimo de los últimos 7 días. Los umbrales amarillo y naranja se miden sobre la base
para que no los afecten los cambios del nivel de referencia de los sensores. Los valores son **provisionales**
(percentiles 99 y 99,9 de 2018-2025) y el rojo es un nivel absoluto provisional (percentil 99,9); los oficiales
los define la CAM con la OGRD.
""")


# =====================================================================
# Programa principal
# =====================================================================
def iniciar_estado():
    valores = {
        "autenticado": False, "t": INICIO_SIMULACION, "reproduciendo": False, "paso": 1,
        "umbrales": {k: dict(v) for k, v in motor.UMBRALES_PROVISIONALES.items()},
        "margen": motor.MARGEN_CIERRE,
    }
    for clave, valor in valores.items():
        st.session_state.setdefault(clave, valor)


def main():
    iniciar_estado()
    if not st.session_state.autenticado:
        pantalla_acceso()
        return

    series = [preparar(e)[0] for e in motor.ESTACIONES]
    primera = max(s.index[0] for s in series) + pd.Timedelta(days=8)   # 7 días para la base
    ultima = min(s.index[-1] for s in series)
    barra_lateral(primera, ultima)

    # La parte central se vuelve a dibujar sola cada 2 s mientras la simulación está en Play
    @st.fragment(run_every=2 if st.session_state.reproduciendo else None)
    def tablero():
        if st.session_state.reproduciendo:
            siguiente = st.session_state.t + pd.Timedelta(hours=st.session_state.paso)
            if siguiente > ultima:          # se acabó la serie: detener y redibujar todo
                st.session_state.reproduciendo = False
                st.session_state.t = ultima
                st.rerun()
            st.session_state.t = siguiente
        t = st.session_state.t

        st.title("🌊 Alertas tempranas · río Las Ceibas")
        estado = "▶ reproduciendo" if st.session_state.reproduciendo else "⏸ en pausa"
        st.caption(f"Simulación con datos históricos ({estado}). Estaciones La Lindosa y Los Micos · "
                   f"modelo XGBoost a {motor.HORIZONTE} h · perfil administrador.")

        resumenes = [resumen_estacion(e, t) for e in motor.ESTACIONES]
        franja_cuenca(resumenes, t)
        for col, r in zip(st.columns(len(resumenes)), resumenes):
            with col:
                tarjeta(r)

        tab1, tab2, tab3 = st.tabs(["📈 Detalle por estación", "📋 Bitácora de avisos", "🧠 Modelo y umbrales"])
        with tab1:
            detalle(t)
        with tab2:
            vista_bitacora(t)
        with tab3:
            vista_modelo()

    tablero()


main()
