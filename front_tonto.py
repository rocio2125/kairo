import streamlit as st
import requests
import os

# --- CONFIGURACIÓN ---
# Si existe la variable de entorno (Docker), úsala. Si no, usa localhost.
DEFAULT_URL = "http://127.0.0.1:5000/consulta"
API_URL = os.environ.get("BACKEND_URL", DEFAULT_URL)

st.title("🔍 Visor JSON de API")
st.caption(f"Conectado a: `{API_URL}`")

# --- INTERFAZ ---
prompt = st.text_area("Introduce tu prompt:", height=100)

if st.button("Enviar Petición"):
    if not prompt:
        st.warning("Escribe algo primero.")
    else:
        try:
            # Enviamos la petición POST
            response = requests.post(API_URL, json={"prompt": prompt})
            
            # Si la respuesta es exitosa (200)
            if response.status_code == 200:
                st.success("✅ Respuesta recibida (200 OK)")
                
                # Muestra el JSON completo y formateado
                st.json(response.json())
                
            else:
                # Si hay error (400, 500, etc)
                st.error(f"❌ Error {response.status_code}")
                st.text(response.text)
                
        except requests.exceptions.ConnectionError:
            st.error(f"🚨 No se pudo conectar a {API_URL}")
            st.info("Asegúrate de que tu backend (app.py) esté corriendo.")