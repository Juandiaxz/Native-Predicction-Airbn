# Native Prediction Airbnb 🚀

Este proyecto es una aplicación web interactiva diseñada para la predicción de precios y análisis inteligente de alojamientos de Airbnb. Utiliza modelos de Machine Learning para estimar costos basados en características específicas del inmueble y del entorno.

---

## 📊 Arquitectura del Proyecto

El sistema está construido bajo una arquitectura cliente-servidor dinámica utilizando **Dash (Plotly)** / **Streamlit** en el frontend y **Python** con **Scikit-Learn** en el backend, desplegado eficientemente en servicios en la nube (Railway/Render).

---

## 🧬 Fundamento Matemático del Modelo

Para la estimación de los precios, el modelo evalúa múltiples variables predictoras. La relación matemática general para una predicción base se define mediante la siguiente ecuación de regresión lineal múltiple:

$$Y = \beta_0 + \beta_1 X_1 + \beta_2 X_2 + \dots + \beta_n X_n + \epsilon$$

Donde:
* $Y$ es el precio estimado del alojamiento.
* $\beta_0$ es. el intercepto (precio base).
* $\beta_i$ corresponden a los coeficientes de peso asignados a cada característica (p. ej., número de habitaciones, ubicación, noches mínimas).
* $X_i$ son las variables de entrada del alojamiento.
* $\epsilon$ representa el término de error aleatorio.

### Normalización de Variables
Para asegurar que las variables con diferentes escalas (como el número de reseñas vs. el precio de limpieza) no sesguen el modelo, se aplica una normalización Min-Max a los datos numéricos antes del entrenamiento:

$$X_{norm} = \frac{X - X_{min}}{X_{max} - X_{min}}$$

---

## 🛠️ Tecnologías Utilizadas

* **Lenguaje:** Python 3.10+
* **Análisis de Datos:** Pandas, NumPy
* **Machine Learning:** Scikit-Learn (Random Forest / Regresión Lineal)
* **Visualización e Interfaz:** Dash / Streamlit & Plotly
* **Despliegue:** Railway / Render

---

## 🚀 Instalación y Configuración Local

Sigue estos pasos para clonar y ejecutar el proyecto en tu entorno local:

### 1. Clonar el repositorio
```bash
git clone [https://github.com/TU_USUARIO/Native-Predicction-Airbn.git](https://github.com/TU_USUARIO/Native-Predicction-Airbn.git)
cd Native-Predicction-Airbn
