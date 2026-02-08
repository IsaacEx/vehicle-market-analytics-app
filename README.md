# US VEHICLE MARKET: STRATEGIC ANALYTICS DASHBOARD

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B.svg)
![Pandas](https://img.shields.io/badge/Pandas-150458.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

Este proyecto transforma un conjunto de datos de más de 51,000 anuncios de vehículos usados en una herramienta interactiva de **Inteligencia de Negocios**. A diferencia de un análisis estático, esta aplicación permite identificar patrones de depreciación y nichos de mercado en tiempo real.

> **Nota de Arquitectura:** El flujo de datos ha sido desacoplado. El procesamiento pesado se realiza en el entorno de desarrollo (Notebook), persistiendo los resultados en formato **Apache Parquet** para maximizar el rendimiento y preservar el tipado de datos en la nube.

---

## 🌟 Características y Mejoras de Ingeniería

* **Optimización de Memoria (Backend PyArrow):** Implementación de tipos de datos eficientes (`int8`, `int16`, `string[pyarrow]`), reduciendo el consumo de RAM de la aplicación.
* **Capa de Datos de Alto Rendimiento:** Uso de formato **Parquet** para una carga de datos instantánea y preservación estricta del esquema de datos.
* **Análisis de Depreciación Avanzado:** Visualización de curvas de valor mediano por kilometraje y condición, utilizando suavizado por *bins* para eliminar el ruido estadístico.
* **Filtros de Contexto Real:** Selección dinámica por rango de años, precios y condiciones físicas, con validación de estados para evitar errores de renderizado.

---

## 🛠️ Stack Tecnológico

| Tecnología | Rol en el Proyecto |
| :--- | :--- |
| **Python 3.11+** | Lenguaje núcleo del proyecto. |
| **Pandas 3.0** | Manipulación de datos con motor de PyArrow. |
| **Streamlit** | Framework para el despliegue de la interfaz web. |
| **Plotly Express** | Motor de gráficos interactivos y dinámicos. |
| **Apache Parquet** | Formato de almacenamiento binario optimizado. |
| **Render** | Despliegue de la aplicación en la nube. |

---

## 🏗️ Estructura del Repositorio

```
car_sales_dashboard/
├── app.py                  # Aplicación web Streamlit
├── notebook/
│   └── EDA.ipynb           # Análisis exploratorio y preprocesamiento
├── data/
│   ├── vehicles_us.csv     # Dataset original
│   └── vehicles_clean.parquet  # Dataset preprocesado (generado por el notebook)
├── .streamlit/
│   └── config.toml         # Configuración de la interfaz
├── requirements.txt        # Dependencias del proyecto
├── LICENSE
└── README.md
```

---

## 📈 Hallazgos Estratégicos (Insights)

* **El "Muro" de las 100k mi:** Se identificó una caída crítica de valor (hasta el 60%) en el segmento de vehículos `good` al cruzar este umbral de kilometraje.
* **Resiliencia de Trucks/SUVs:** Estos segmentos dominan el volumen de oferta y mantienen un precio mediano significativamente mayor frente a los Sedanes bajo las mismas condiciones de uso.
* **Data Quality:** El análisis reveló vehículos etiquetados como "New" con alto kilometraje, permitiendo una limpieza de datos basada en la realidad del odómetro.

---

## 🚀 Instalación y Ejecución Local

1. Clonar el repositorio:
   ```bash
   git clone <url-del-repositorio>
   cd car_sales_dashboard
   ```
2. Crear un entorno virtual e instalar las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Ejecutar el notebook `notebook/EDA.ipynb` para generar el archivo `data/vehicles_clean.parquet`.

4. Ejecutar la aplicación:
   ```bash
   streamlit run app.py
   ```

---

Prueba la aplicación en vivo: <https://proyecto-sprint-7-yv1b.onrender.com>

---

## ⚖️ Licencia
Este proyecto está bajo la Licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.

---