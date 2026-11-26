# Sistema de calidad de datos y modelos predictivos para alertas tempranas de inundaciones en la cuenca del río Las Ceibas

Proyecto de Ciencia, Tecnología e Innovación (CTeI) de la **Corporación Universitaria del Huila (CORHUILA)**, Facultad de Ingeniería.

| | |
|---|---|
| **Área de conocimiento** | Ingeniería, Arquitectura, Urbanismo y afines |
| **Sub-área** | Hidroclimatología |
| **Sector de aplicación** | Tecnologías de la Información · Sector público (medio ambiente y recursos naturales) |
| **Duración** | 10 meses (2 de febrero de 2026 a 30 de noviembre de 2026) |
| **Municipio beneficiado** | Neiva (Huila) |
| **Grupo de investigación** | [INPROTI](https://scienti.minciencias.gov.co/gruplac/jsp/visualiza/visualizagr.jsp?nro=00000000018533) |
| **Semillero** | E-Logic |

---

## Resumen

La cuenca del río Las Ceibas es la principal fuente de agua potable de Neiva y enfrenta un alto riesgo de inundaciones que amenaza a la ciudad y a sus comunidades ribereñas. Este proyecto desarrolla un sistema que:

1. **Valida y limpia** los datos hidrometeorológicos históricos de la cuenca.
2. **Entrena modelos predictivos** basados en inteligencia artificial para anticipar crecientes súbitas.
3. **Muestra un dashboard interactivo** con indicadores de riesgo en tiempo real para apoyar la toma de decisiones.

El objetivo es pasar de una gestión del riesgo **reactiva** a una **proactiva**, en línea con las políticas nacionales y regionales de gestión del riesgo y adaptación al cambio climático.

## Problema

Las inundaciones en Colombia son cada vez más frecuentes por el cambio climático y la deforestación. El Estudio Nacional del Agua 2022 registró 6.167 eventos de inundación entre 2010 y 2021 (IDEAM, 2023). El Huila, ubicado en la zona hidrográfica del Alto Magdalena, tiene municipios clasificados en riesgo "Alto" y "Muy Alto".

En Neiva, las crecientes súbitas del río Las Ceibas han afectado barrios ribereños y han obligado a cerrar la bocatoma del acueducto por alta turbidez (2021, 2024 y 2025). Contar con datos confiables y modelos que anticipen estos eventos es clave para proteger vidas, bienes y el abastecimiento de agua.

**Pregunta de investigación**

> ¿Cómo puede un sistema de gestión de la calidad de datos hidrometeorológicos y desarrollo de modelos predictivos mejorar la anticipación y respuesta ante eventos de inundación en el departamento del Huila?

## Objetivos

**Objetivo general.** Desarrollar un sistema de calidad de datos y modelos predictivos de variables hidrometeorológicas en la cuenca del río Las Ceibas, para la generación de alertas tempranas ante posibles inundaciones en Neiva, Huila.

**Objetivos específicos**

1. Implementar un sistema de limpieza y validación de datos históricos de variables hidrometeorológicas que garantice la calidad de la información.
2. Desarrollar modelos predictivos que permitan anticiparse a eventos de crecientes súbitas e inundaciones en la cuenca del río Las Ceibas.
3. Desarrollar un dashboard que integre los modelos predictivos y visualice en tiempo real los indicadores de riesgo para la toma de decisiones ante amenazas de inundación.

## Metodología

Investigación aplicada con enfoque **mixto** y diseño secuencial explicativo:

- **Cuantitativo:** diseño descriptivo-correlacional y cuasiexperimental para analizar las series hidrometeorológicas y comparar el rendimiento de distintos modelos de IA.
- **Cualitativo:** trabajo con actores clave para definir requisitos y evaluar la usabilidad del dashboard.

### Fase 1: Calidad de datos
- Definir criterios de calidad y protocolo de limpieza y validación.
- Recolectar, limpiar y consolidar las series históricas con scripts en **Python**.
- Validar el dataset con análisis estadísticos y revisión por expertos.
- Documentar el proceso y aprobar la base de datos final para el modelado.

### Fase 2: Modelos predictivos
- Seleccionar arquitecturas de IA (por ejemplo **LSTM** y modelos híbridos **CNN-LSTM**) y definir las métricas de evaluación.
- Entrenar los modelos con la base de datos validada.
- Evaluar su precisión con datos de prueba frente a crecientes históricas.
- Elegir el mejor modelo, documentarlo y empaquetarlo para el dashboard.

### Fase 3: Dashboard de alertas
- Levantar requisitos, diseñar la interfaz (UI/UX) y la arquitectura técnica.
- Desarrollar el dashboard integrando el modelo y las alertas en tiempo real. La propuesta planteaba **Power BI**; se construyó en **Streamlit** (Python), ver [`dashboard/`](dashboard/README.md).
- Realizar pruebas funcionales y de usabilidad, ajustes finales y despliegue.

### Análisis estadístico
- Prueba de **Shapiro-Wilk** para verificar la normalidad de las series limpias.
- Prueba **t de Student para muestras pareadas** para saber si la diferencia de precisión entre dos modelos es significativa.

## Cronograma (2026)

| # | Actividad | Inicio | Fin | Entregable |
|---|---|---|---|---|
| 1.1 | Selección del dataset, criterios de calidad y protocolo de limpieza | 02/02 | 27/02 | Dataset (.csv) |
| 1.2 | Scripts en Python para recolectar, limpiar y consolidar series | 03/03 | 13/03 | Notebook + dataset (.csv) |
| 1.3 | Validación estadística y revisión por expertos | 16/03 | 27/03 | Informe de pruebas |
| 1.4 | Documentación y aprobación de la base de datos final | 16/03 | 27/03 | Informe |
| 2.1 | Selección de arquitecturas de IA y diseño del experimento | 31/03 | 10/04 | Informe técnico |
| 2.2 | Entrenamiento de los modelos predictivos | 13/04 | 24/04 | Notebook + modelo |
| 2.3 | Evaluación de precisión con datos de prueba | 27/04 | 08/05 | Informe técnico |
| 2.4 | Selección, documentación y empaquetado del mejor modelo | 11/05 | 29/05 | Informe técnico |
| 3.1 | Requisitos, diseño UI/UX y arquitectura técnica | 01/06 | 27/06 | Informe técnico |
| 3.2 | Desarrollo del dashboard con alertas en tiempo real | 01/07 | 28/08 | Dashboard en Power BI |
| 3.3 | Pruebas funcionales y de usabilidad, ajustes y despliegue | Septiembre | 30/10 | Informe de pruebas |
| 3.4 | Redacción del artículo de investigación | 03/08 | 30/11 | Artículo |

## Resultados esperados

| Tipología | Producto |
|---|---|
| Desarrollo tecnológico e innovación | **Software:** sistema de calidad de datos y modelos predictivos para alertas tempranas de inundaciones |
| Generación de nuevo conocimiento | **Artículo** en revista especializada |
| Apropiación social del conocimiento | **Informe de investigación** del proyecto |

Además se espera obtener:
- Una base de datos hidrometeorológica validada y consolidada para la cuenca.
- Modelos de predicción de caudal y nivel del río calibrados y validados.
- Un protocolo técnico para integrar los modelos en un sistema de alerta temprana.

## Beneficiarios

- **Directos:** Oficina para la Gestión del Riesgo de Desastres de Neiva, Corporación Autónoma Regional del Alto Magdalena (**CAM**) y la empresa de acueducto **Las Ceibas E.S.P.**
- **Indirectos:** habitantes de Neiva, en especial quienes viven en zonas ribereñas.

## Impacto

- **Social:** menor vulnerabilidad de la población ante inundaciones y mejor capacidad de respuesta institucional y comunitaria.
- **Ambiental:** herramientas para monitorear el cambio climático y proteger el recurso hídrico.
- **Productivo:** posible reducción de pérdidas en agricultura y comercio.
- **Tecnológico:** capacidades locales en gestión de datos, hidroinformática e IA.
- **Institucional:** fortalece la Especialización en Hidroinformática de CORHUILA y la alianza con entidades como la CAM.

## Equipo

| Nombre | Institución | Rol |
|---|---|---|
| Alvaro Hernán Alarcón López | CORHUILA | Investigador principal |
| José Miguel Llanos Mosquera | CORHUILA | Co-investigador |
| Luis Felipe Giraldo Trujillo | Universidad de los Andes | Co-investigador |
| Andrea Milena Marín Zambrano | Universidad Antonio Nariño | Co-investigadora |
| Carol Milene Anturi Esquivel | CORHUILA (Esp. Hidroinformática) | Auxiliar |
| José Gregorio Hernández Vanegas | CORHUILA (Ing. Mecatrónica) | Auxiliar |
| Juan Fernando Pérez Olaya | CORHUILA (Ing. de Sistemas) | Auxiliar |
| Alvaro Felipe Ávila Vidal | CORHUILA (Ing. de Sistemas) | Auxiliar |
| Juan Felipe Narváez Amaya | CORHUILA (Ing. de Sistemas) | Auxiliar |
| Tomás Octavio Rodríguez | CORHUILA (Ing. de Sistemas) | Auxiliar |

Programas vinculados: Especialización en Hidroinformática, Especialización en Machine Learning para IoT e Ingeniería de Sistemas.

## Presupuesto

| Rubro | CORHUILA (efectivo) | CORHUILA (especie) | Total |
|---|---:|---:|---:|
| Talento humano | – | $30.000.000 | $30.000.000 |
| Salidas de campo (movilidad) | $3.000.000 | – | $3.000.000 |
| Divulgación de la investigación | $12.000.000 | – | $12.000.000 |
| **Total** | **$15.000.000** | **$30.000.000** | **$45.000.000** |

## Estructura sugerida del repositorio

El repositorio está empezando. Esta es una organización propuesta para ir agregando el trabajo de cada fase:

```
├── data/
│   ├── raw/            # Datos originales sin modificar
│   ├── processed/      # Datos consolidados por estación (.csv)
│   └── clean/          # Series horarias limpias e imputadas, listas para modelar
├── notebooks/          # Notebooks de exploración, limpieza y modelado
├── src/                # Scripts de Python reutilizables
├── models/             # Modelos entrenados
├── dashboard/          # Archivos del dashboard (Streamlit)
├── docs/               # Informes, protocolos y documentación
└── README.md
```

## Tecnologías previstas

- **Python** para la limpieza, validación y modelado de datos (notebooks y scripts).
- **Redes neuronales** (LSTM, CNN-LSTM) para la predicción de caudales y niveles.
- **Streamlit** para el dashboard de alertas (la propuesta planteaba Power BI).

## Referencias principales

- Ghimire, S., et al. (2021). Streamflow prediction using an integrated methodology based on convolutional neural network and long short-term memory networks. *Scientific Reports, 11*(1), 17497. https://doi.org/10.1038/s41598-021-96751-4
- Kratzert, F., Klotz, D., Hochreiter, S., & Nearing, G. S. (2021). A note on leveraging synergy in multiple meteorological data sets with deep learning for rainfall–runoff modeling. *Hydrology and Earth System Sciences, 25*(5), 2685–2703. https://doi.org/10.5194/hess-25-2685-2021
- Duarte, Y. E., et al. (2025). Deep Learning and Time Series for the Prediction of Monthly Precipitation. A Case Study in the Department of Boyacá, Colombia. *Revista Ingeniería, 30*(1), e21930. https://doi.org/10.14483/23448393.21930
- Mena-Rentería, D., et al. (2025). Impact of climate change on the hydrological regime in a small watershed of the tropical Andean Plateau. *Sustainable Water Resources Management, 11*(2), 23. https://doi.org/10.1007/s40899-024-01186-0
- Zambrano Nájera, J., & Rey, D. M. (2022). Assessment of Storm Floods in a Small Tropical Andean Basins. *Frontiers in Climate, 4*. https://doi.org/10.3389/fclim.2022.760894
- Matovelle, C., et al. (2024). Water quality assessment methods of the highland Andean rivers: A scoping systematic review. *Heliyon, 10*(9), e30552. https://doi.org/10.1016/j.heliyon.2024.e30552
- IDEAM. (2023). *Estudio Nacional del Agua 2022*. https://www.ideam.gov.co/sala-de-prensa/informes/publicacion-jue-23032023-1200
- Corhuila. (2025). *Especialización en Hidroinformática*. https://corhuila.edu.co/carreras_profesional/especializacion-en-hidroinformatica-modalidad-virtual/

La bibliografía completa está en el formato de presentación de la propuesta (Anexo 1, FO-IV-01).

---

*Corporación Universitaria del Huila – CORHUILA. Institución universitaria vigilada por MinEducación.*
