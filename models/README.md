# models

Modelos predictivos entrenados (por ejemplo LSTM y CNN-LSTM) y sus métricas de evaluación (Objetivo 2).

## Contenido

| Carpeta | Qué contiene | Lo genera |
|---|---|---|
| [`La_Lindosa/metricas_prueba_2025.csv`](La_Lindosa/metricas_prueba_2025.csv) | Errores (RMSE, MAE, NSE y mejora sobre la persistencia) de SARIMAX, XGBoost, LSTM y Prophet en 2025, a 1, 3, 6 y 12 h, en todas las horas y en nivel alto | [`notebooks/05_modelos_La_Lindosa.ipynb`](../notebooks/05_modelos_La_Lindosa.ipynb) |
| [`Los_Micos/metricas_prueba_2025.csv`](Los_Micos/metricas_prueba_2025.csv) | Lo mismo para Los Micos | [`notebooks/06_modelos_Los_Micos.ipynb`](../notebooks/06_modelos_Los_Micos.ipynb) |

**Resultado:** en las dos estaciones el mejor modelo a 6 horas es **XGBoost** (RMSE 6,3 cm en La Lindosa y 3,7 cm en Los Micos, 8 % y 20 % mejor que suponer que el nivel no cambia), seguido de cerca por la LSTM. Los modelos entrenados no se guardan aquí (se vuelven a entrenar en minutos con los notebooks).
