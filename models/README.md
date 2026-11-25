# models · Predicción de nivel del río (Objetivo 2)

Este documento explica **todo el proceso de modelación** del nivel del río en las estaciones **La Lindosa** y **Los Micos**: qué datos se usan, cómo se prepararon, qué modelos se probaron, cómo se evaluaron, qué métricas se usaron y por qué, cuáles fueron los resultados y qué modelo se recomienda para cada estación.

El detalle paso a paso, con todo el código explicado y las gráficas, está en los notebooks:

| Notebook | Estación |
|---|---|
| [`notebooks/05_modelos_La_Lindosa.ipynb`](../notebooks/05_modelos_La_Lindosa.ipynb) | La Lindosa |
| [`notebooks/06_modelos_Los_Micos.ipynb`](../notebooks/06_modelos_Los_Micos.ipynb) | Los Micos |

Los dos notebooks tienen exactamente la misma estructura y el mismo código; solo cambia la estación y los comentarios de los resultados.

---

## Resumen

| | La Lindosa | Los Micos |
|---|---|---|
| **Modelo recomendado** | **XGBoost** | **XGBoost** |
| Error típico a 6 h (RMSE) | 6,3 cm | 3,7 cm |
| Mejora sobre suponer que el nivel no cambia | 8 % | 20 % |
| Eficiencia de Nash-Sutcliffe (NSE) a 6 h | 0,54 | 0,75 |
| Segundo lugar | LSTM (6,4 cm) | LSTM (3,8 cm) |

XGBoost es el mejor en los cuatro horizontes evaluados (1, 3, 6 y 12 h) y también en las horas de crecida, en las dos estaciones. La LSTM queda muy cerca. SARIMAX solo aporta en Los Micos. Prophet no sirve para predecir a pocas horas.

---

## 1. Contexto y punto de partida

El trabajo continúa la limpieza de datos de los notebooks 01 a 04 (ver [`data/clean/README.md`](../data/clean/README.md)):

1. **01 · Resolución horaria:** los datos se llevaron a un valor por hora.
2. **02 · Calidad temporal:** se catalogaron los huecos.
3. **03 · Imputación:** se rellenaron los huecos y cada hora quedó marcada como `REAL`, `ALTA`, `MEDIA`, `BAJA` o `SIN_DATO`.
4. **04 · Análisis exploratorio:** se estudió cómo se comportan y relacionan el nivel, la lluvia y la temperatura.

Los hallazgos del notebook 04 que guían la modelación:

- El nivel se relaciona poco con la lluvia de la misma hora (r ≈ 0,1) pero bastante más con la **lluvia acumulada de 1 a 7 días** (r ≈ 0,25-0,31).
- El río **responde muy rápido**: el cambio de nivel sigue a la lluvia con 0 a 1 hora de retraso.
- La temperatura casi no se relaciona con el nivel.
- El **nivel de base cambia entre años** (La Lindosa baja en 2023-2025; Los Micos baja en 2021-2022 y tiene un escalón de +0,24 m el 22 de diciembre de 2023).

## 2. Datos usados

| Variable | Qué se usa | Por qué |
|---|---|---|
| Nivel | Solo horas `REAL` u `ALTA`; las `MEDIA` se dejan vacías | Las horas `MEDIA` son un promedio histórico, no lo que pasó en el río. Entrenar o evaluar con ellas mediría el método de relleno. |
| Lluvia | Valor final (con imputados) y sus acumulados de 1, 3, 6, 12, 24, 72 y 168 h | La lluvia acumulada necesita todas las horas; es la variable de lluvia más útil según el notebook 04. |
| Temperatura | No se usa | Casi no se relaciona con el nivel. |
| Fecha y hora | Hora del día y día del año, como seno y coseno | Ciclo diario y temporadas de lluvia. El seno y coseno hacen que las 23:00 queden "cerca" de las 00:00 y diciembre cerca de enero. |

## 3. Qué se predice: horizonte

Se predice el nivel **h horas después** de la última hora observada, con **h = 1, 3, 6 y 12 horas**. El modelo recomendado se elige con **h = 6 horas**:

- Como el río responde a la lluvia en 0 a 1 hora, sin pronóstico de lluvia ningún modelo puede anticipar una crecida causada por lluvia que aún no ha caído. Mientras más largo el horizonte, más pesa esa lluvia desconocida.
- A 1 hora casi todo acierta, pero un aviso con una hora de anticipación sirve poco.
- A 6 horas todavía hay información útil (el río que ya viene subiendo, la lluvia de los días anteriores) y el aviso da tiempo para reaccionar.

**Regla sin fuga de información:** para predecir la hora *t + h*, cada modelo usa solo datos observados hasta la hora *t*.

## 4. Partición de los datos

Las series de tiempo se parten **por fechas**, nunca al azar (si el modelo viera 2025 al entrenar, la prueba sería engañosa):

| Conjunto | Periodo | Uso |
|---|---|---|
| Entrenamiento | 2018-2023 | Los modelos aprenden de estos datos. 2017 se excluye porque está incompleto. |
| Validación | 2024 | Ajustes: número de árboles de XGBoost y cuándo dejar de entrenar la LSTM. |
| Prueba | 2025 | Solo para medir el error final y elegir el mejor modelo. |

Para que los cambios del nivel de base no afecten, SARIMAX, XGBoost y la LSTM predicen el **cambio de nivel** respecto al nivel actual, y no el nivel absoluto.

## 5. Modelos

### Referencia: persistencia

Predice que el nivel dentro de *h* horas será igual al de ahora. No es un modelo sino la **línea base** estándar en pronóstico de corto plazo: un modelo solo vale la pena si le gana.

### 5.1 SARIMAX (estadístico clásico)

- **Qué es:** modelo autorregresivo integrado de media móvil con variables externas (Box y Jenkins, 1976). Trabaja con el cambio de nivel hora a hora (*d* = 1), que depende de los cambios y errores de las horas anteriores, más un efecto lineal de la lluvia.
- **Variables externas:** lluvia acumulada de 6, 24 y 72 h, y seno y coseno de la hora (el ciclo diario se modela así en vez de con una parte estacional de periodo 24, que sería muy lenta).
- **Elección del orden:** se probaron (1,1,0), (2,1,0), (3,1,0), (1,1,1) y (2,1,1); se eligió el de menor AIC: **(2,1,1)** en las dos estaciones.
- **Predicción:** con el filtro de Kalman se obtiene el estado del modelo en cada hora y se proyecta hacia adelante. La lluvia futura se supone cero (no hay pronóstico de lluvia). El cálculo se verificó contra la función `forecast()` de statsmodels (diferencia ~10⁻¹⁶ m).

### 5.2 XGBoost (árboles de decisión con *boosting*)

- **Qué es:** cientos de árboles de decisión pequeños entrenados uno tras otro, cada uno corrigiendo los errores de los anteriores (Chen y Guestrin, 2016). Capta relaciones no lineales.
- **Atributos** (calculados con información hasta *t*): nivel sobre el mínimo de los últimos 7 días; cambio de nivel en las últimas 1, 2, 3, 6, 12 y 24 h; lluvia acumulada de 1 a 168 h; hora del día y día del año.
- **Objetivo:** cambio de nivel entre *t* y *t + h*; un modelo por horizonte.
- **Hiperparámetros:** tasa de aprendizaje 0,03, profundidad 6, 80 % de filas y columnas por árbol, y **parada temprana** con el error de validación (2024).

### 5.3 LSTM (red neuronal recurrente)

- **Qué es:** red neuronal que lee una secuencia hora a hora con una memoria interna (Hochreiter y Schmidhuber, 1997); es el modelo de aprendizaje profundo más usado en hidrología (Kratzert et al., 2018).
- **Entrada:** las últimas 72 horas, con 9 variables por hora (forma de la curva de nivel, nivel sobre la base de 7 días, lluvia de 1, 24 y 168 h, hora y día del año).
- **Salida:** los cambios de nivel de las siguientes 1 a 12 horas, todos a la vez.
- **Arquitectura:** una capa LSTM de 64 unidades y dos capas densas (unos 24.000 parámetros; red pequeña a propósito para no memorizar).
- **Entrenamiento:** Adam, lotes de 512, error cuadrático; parada temprana con la validación (2024). Entradas escaladas solo con estadísticas del entrenamiento.

### 5.4 Prophet (descomposición en tendencia y ciclos)

- **Qué es:** suma de una tendencia lenta, un ciclo anual, un ciclo diario y el efecto de la lluvia (Taylor y Letham, 2018).
- **Variables externas:** lluvia acumulada de 24, 72 y 168 h conocida en el origen.
- **Limitación:** no usa el nivel de las horas anteriores y predice el nivel absoluto, por lo que lo afectan los cambios del nivel de base.

## 6. Métricas

Todas se calculan en **las mismas horas de 2025** para todos los modelos: horas en las que el nivel que se predice es confiable y las 72 horas anteriores están completas. La función de métricas verifica que todos los modelos tengan predicción en cada una de esas horas.

Notación: $y_i$ nivel observado, $\hat{y}_i$ nivel predicho, $\bar{y}$ promedio de los observados, $n$ número de horas.

| Métrica | Fórmula | Qué mide | Mejor |
|---|---|---|---|
| **RMSE** | $\sqrt{\frac{1}{n}\sum (\hat{y}_i - y_i)^2}$ | Error típico en cm. Castiga los errores grandes (crecidas). **Métrica principal.** | 0 |
| **MAE** | $\frac{1}{n}\sum \lvert \hat{y}_i - y_i \rvert$ | Error promedio en cm; fácil de interpretar. | 0 |
| **NSE** (Nash y Sutcliffe, 1970) | $1 - \frac{\sum (\hat{y}_i - y_i)^2}{\sum (y_i - \bar{y})^2}$ | Estándar en hidrología. 1 perfecto, 0 igual que el promedio, negativo peor que el promedio. | 1 |
| **Mejora sobre persistencia** (Murphy, 1988) | $100\left(1 - \frac{RMSE_{modelo}}{RMSE_{persistencia}}\right)$ | Si el modelo vale la pena: 0 % no aporta, negativo es peor que no hacer nada. | alta |
| **RMSE en nivel alto** | RMSE en las horas con nivel > percentil 95 de 2025 | Desempeño en crecidas, lo que importa para alertas. | 0 |

**Por qué no basta el NSE:** en un río casi siempre tranquilo, el promedio es una referencia fácil de superar. La persistencia es mucho más exigente para predicción a pocas horas.

**Criterio de decisión** (definido antes de ver los resultados): (1) menor RMSE a 6 h; (2) debe ganarle a la persistencia; (3) se revisa el desempeño en nivel alto, comparando solo modelos que cumplen (2), porque un modelo con sesgo puede "acertar" en las crecidas por casualidad; (4) se revisa si gana en todos los horizontes; (5) se comprueba con pruebas estadísticas pareadas si la diferencia con los demás es significativa.

## 7. Resultados

### La Lindosa (prueba 2025, 6.895 horas evaluadas a 6 h)

RMSE en cm (entre paréntesis, mejora sobre la persistencia):

| Modelo | 1 h | 3 h | 6 h | 12 h | Nivel alto, 6 h |
|---|---|---|---|---|---|
| Persistencia | 2,9 | 5,2 | 6,9 | 8,3 | 18,1 |
| SARIMAX | 2,9 (1 %) | 5,2 (0 %) | 6,9 (0 %) | 8,3 (1 %) | 18,8 (−4 %) |
| **XGBoost** | **2,7 (7 %)** | **4,9 (6 %)** | **6,3 (8 %)** | **7,2 (14 %)** | **16,5 (9 %)** |
| LSTM | 2,8 (3 %) | 5,0 (4 %) | 6,4 (7 %) | 7,4 (12 %) | 16,8 (7 %) |
| Prophet | 46,9 | 47,0 | 46,4 | 45,7 | 66,5 |

### Los Micos (prueba 2025, 8.751 horas evaluadas a 6 h)

| Modelo | 1 h | 3 h | 6 h | 12 h | Nivel alto, 6 h |
|---|---|---|---|---|---|
| Persistencia | 1,8 | 3,5 | 4,6 | 5,4 | 14,5 |
| SARIMAX | 1,7 (6 %) | 3,2 (10 %) | 3,9 (16 %) | 4,3 (21 %) | 14,2 (2 %) |
| **XGBoost** | **1,7 (9 %)** | **3,0 (13 %)** | **3,7 (20 %)** | **4,1 (25 %)** | **13,3 (8 %)** |
| LSTM | 1,7 (4 %) | 3,1 (12 %) | 3,8 (18 %) | 4,2 (23 %) | 13,5 (7 %) |
| Prophet | 12,4 | 12,4 | 12,7 | 12,8 | 11,1 (sesgo, no válido) |

Las tablas completas (con MAE y NSE) están en [`La_Lindosa/metricas_prueba_2025.csv`](La_Lindosa/metricas_prueba_2025.csv) y [`Los_Micos/metricas_prueba_2025.csv`](Los_Micos/metricas_prueba_2025.csv). Columnas: `modelo`, `h` (horizonte en horas), `subconjunto` (`todas` o `nivel alto`), `n` (horas evaluadas), `RMSE_cm`, `MAE_cm`, `NSE`, `mejora_vs_persistencia_%`.

### ¿Las diferencias son significativas?

La metodología del proyecto pide una **prueba t de Student para muestras pareadas**. Como el error de una hora está muy relacionado con el de la siguiente, la prueba se hace con el **error cuadrático medio de cada día** (293 días en La Lindosa y 365 en Los Micos) y no con las horas sueltas. Las diferencias diarias no son normales (prueba de **Shapiro-Wilk**, p ≈ 0), así que se acompaña con la prueba de **Wilcoxon de rangos con signo**, que no supone normalidad. Nivel de significancia: 5 %. Horizonte: 6 h.

| Comparación | La Lindosa: p (t / Wilcoxon) | ¿Significativa? | Los Micos: p (t / Wilcoxon) | ¿Significativa? |
|---|---|---|---|---|
| XGBoost vs persistencia | 0,0006 / < 0,0001 | sí | < 0,0001 / < 0,0001 | sí |
| XGBoost vs SARIMAX | 0,0004 / < 0,0001 | sí | 0,008 / 0,07 | solo prueba t |
| XGBoost vs LSTM | 0,35 / 0,02 | no concluyente | 0,02 / 0,02 | sí |
| XGBoost vs Prophet | < 0,0001 / < 0,0001 | sí | < 0,0001 / < 0,0001 | sí |

En La Lindosa, XGBoost y la LSTM están prácticamente empatados; se prefiere XGBoost porque, a igual precisión, es más rápido, más simple y explicable. En Los Micos la ventaja de XGBoost sobre SARIMAX viene sobre todo de unos pocos días con cambios grandes de nivel.

### Interpretación

- **XGBoost gana en las dos estaciones** porque capta relaciones no lineales (la misma lluvia mueve el río de forma distinta según qué tan crecido esté) y usa la tendencia reciente del nivel. Las variables que más usa a 6 h son el cambio de nivel de las últimas 6 a 12 h, el nivel sobre la base de 7 días y la hora del día.
- **La LSTM queda muy cerca.** Con una sola estación y pocas crecidas por año, no tiene suficientes ejemplos para superar a XGBoost; con más estaciones como entrada podría mejorar.
- **SARIMAX** empata con la persistencia en La Lindosa (un modelo lineal no capta la respuesta no lineal del río), pero mejora 16 % en Los Micos, donde aprende que el río baja rápido después de cada pico.
- **Prophet falla** porque no usa el nivel reciente: en La Lindosa extrapoló la tendencia descendente de 2023 y predijo niveles de ~0,2 m cuando el río estaba en ~0,6 m; en Los Micos predice casi siempre ~0,4 m. Su aparente buen resultado en nivel alto en Los Micos es un efecto de ese sesgo (siempre predice alto), no una predicción real.
- **La mejora es mayor en Los Micos** (20 % frente a 8 %) porque sus picos son cortos y bajan rápido: los modelos aprenden que el pico no se mantiene, mientras que la persistencia lo repite.
- **Ningún modelo anticipa por completo una crecida con 6 horas** si la lluvia que la causa aún no ha caído: en los eventos más grandes de 2025, XGBoost y la LSTM suben antes que la persistencia pero se quedan cortos en el pico.

## 8. Limitaciones

- **Sin pronóstico de lluvia:** limita lo que se puede anticipar a más de 1-2 horas.
- **Un solo año de prueba (2025)**, con crecidas moderadas.
- **Pluviómetro de Los Micos en 2025:** casi no registró lluvia (incluso durante la mayor crecida del año marcó 0,1 mm/h), lo que resta valor a la lluvia como entrada en la prueba.
- **Cambios del nivel de base sin confirmar** con el operador (CAM).
- **Hiperparámetros estándar**, sin búsqueda exhaustiva.

## 9. Próximos pasos

1. Usar la lluvia y el nivel de la otra estación como entradas adicionales.
2. Incorporar un pronóstico de lluvia (CAM o IDEAM).
3. Validación por años para confirmar que el ranking es estable.
4. Definir umbrales de alerta con la CAM y evaluar los modelos como detectores de alerta (aciertos, falsas alarmas, alertas perdidas).
5. Revisar el pluviómetro de Los Micos y confirmar los cambios del nivel de base.

## 10. Cómo reproducir

```
pip install pandas numpy scipy matplotlib jupyter statsmodels xgboost prophet torch
jupyter notebook notebooks/
```

Abrir `05_modelos_La_Lindosa.ipynb` o `06_modelos_Los_Micos.ipynb` y ejecutar con *Run All* (5 a 10 minutos cada uno). Solo necesitan las series limpias de `data/clean/`. Los modelos entrenados no se guardan en esta carpeta porque se vuelven a entrenar en minutos; las métricas sí.

La LSTM usa azar; aunque se fija la semilla, sus resultados pueden variar unas décimas de centímetro entre computadores.

## Referencias

- Box, G. E. P. y Jenkins, G. M. (1976). *Time Series Analysis: Forecasting and Control*. Holden-Day.
- Chen, T. y Guestrin, C. (2016). XGBoost: A scalable tree boosting system. *Proceedings of the 22nd ACM SIGKDD Conference*, 785-794.
- Hochreiter, S. y Schmidhuber, J. (1997). Long short-term memory. *Neural Computation*, 9(8), 1735-1780.
- Hyndman, R. J. y Athanasopoulos, G. (2021). *Forecasting: Principles and Practice* (3.ª ed.). OTexts.
- Kratzert, F., Klotz, D., Brenner, C., Schulz, K. y Herrnegger, M. (2018). Rainfall-runoff modelling using Long Short-Term Memory (LSTM) networks. *Hydrology and Earth System Sciences*, 22, 6005-6022.
- Murphy, A. H. (1988). Skill scores based on the mean square error and their relationships to the correlation coefficient. *Monthly Weather Review*, 116, 2417-2424.
- Nash, J. E. y Sutcliffe, J. V. (1970). River flow forecasting through conceptual models part I: A discussion of principles. *Journal of Hydrology*, 10(3), 282-290.
- Shapiro, S. S. y Wilk, M. B. (1965). An analysis of variance test for normality (complete samples). *Biometrika*, 52(3-4), 591-611.
- Wilcoxon, F. (1945). Individual comparisons by ranking methods. *Biometrics Bulletin*, 1(6), 80-83.
- Taylor, S. J. y Letham, B. (2018). Forecasting at scale. *The American Statistician*, 72(1), 37-45.
