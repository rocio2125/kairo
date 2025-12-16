import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Data Assistant AI",
    page_icon="📊",
    layout="centered"
)

# --- CONFIGURACIÓN URL BACKEND ---
# Intenta leer la variable de entorno (Docker), si no, usa localhost
DEFAULT_URL = "http://127.0.0.1:5000/consulta"
API_URL = os.environ.get("BACKEND_URL", DEFAULT_URL)

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Configuración")
    api_url = st.text_input("URL del Backend", value=API_URL)
    st.divider()
    st.info("Escribe tu pregunta y la IA decidirá si mostrarte una tabla o un gráfico.")

# --- INTERFAZ PRINCIPAL ---
st.title("📊 Asistente de Datos Inteligente")
st.markdown("Pregunta sobre tus **Ventas**, **Clientes** o **Transacciones**.")

# Formulario de entrada
with st.form("my_form"):
    text_input = st.text_area(
        "Escribe tu consulta:", 
        placeholder="Ej: Grafícame las ventas totales por categoría de producto en un gráfico de barras"
    )
    submitted = st.form_submit_button("Analizar")

if submitted and text_input:
    with st.spinner("🧠 Analizando intención, generando SQL y consultando datos..."):
        try:
            # Petición al Backend
            response = requests.post(api_url, json={"prompt": text_input})
            
            if response.status_code == 200:
                data_json = response.json()
                
                # 1. RESPUESTA VERBAL
                st.success("Respuesta:")
                st.write(data_json.get("respuesta_bot", "Sin respuesta textual."))
                
                # 2. PROCESAMIENTO DE DATOS Y GRÁFICOS
                raw_data = data_json.get("data", [])
                viz_type = data_json.get("type", "data")       # 'chart' o 'data'
                chart_type = data_json.get("chart_type", None) # 'bar', 'line', 'pie'
                
                if raw_data:
                    df = pd.DataFrame(raw_data)
                    
                    # Lógica de Visualización
                    if viz_type == "chart" and not df.empty:
                        st.subheader(f"📈 Visualización: {chart_type.upper()}")
                        
                        # Heurística simple: Asumimos Col 1 = Eje X (Texto), Col 2 = Eje Y (Numérico)
                        # Si hay más columnas, el usuario o el modelo deberían especificar, pero esto es un MVP.
                        col_names = df.columns.tolist()
                        
                        if len(col_names) >= 2:
                            x_col = col_names[0]
                            y_col = col_names[1]
                            
                            if chart_type == "bar":
                                st.bar_chart(df.set_index(x_col)[y_col])
                                
                            elif chart_type == "line":
                                st.line_chart(df.set_index(x_col)[y_col])
                                
                            elif chart_type == "pie":
                                fig = px.pie(df, names=x_col, values=y_col, title=f"Distribución por {x_col}")
                                st.plotly_chart(fig, use_container_width=True)
                            
                            else:
                                st.warning(f"Tipo de gráfico '{chart_type}' no reconocido. Mostrando datos.")
                                st.dataframe(df)
                        else:
                            st.warning("No hay suficientes columnas para generar un gráfico (mínimo 2).")
                            st.dataframe(df)
                            
                    else:
                        # Si es solo datos o el dataframe está vacío
                        st.subheader("📋 Tabla de Datos")
                        st.dataframe(df)
                else:
                    st.info("La consulta no devolvió resultados numéricos.")

                # 3. ZONA TÉCNICA (DEBUG)
                with st.expander("🕵️ Ver detalles técnicos (SQL)"):
                    st.code(data_json.get("sql", "--"), language="sql")
                    st.json(data_json)

            else:
                st.error(f"Error {response.status_code}: {response.text}")

        except requests.exceptions.ConnectionError:
            st.error("🚨 No se pudo conectar con el Backend.")
            st.markdown(f"Verifica que la API esté corriendo en: `{api_url}`")