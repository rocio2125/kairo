import os
from flask import Flask, request, jsonify
import psycopg2
from groq import Groq
import json
from dotenv import load_dotenv
from flask_cors import CORS
import socket
from datetime import datetime, timezone # <--- CAMBIO 1: Importamos timezone

# Intentamos cargar .env (busca en la carpeta actual o superior)
load_dotenv()

app = Flask(__name__)

# ======================
# CONFIGURACIÓN
# ======================
DB_URI = os.environ.get("DATABASE_URL")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
QRADAR_HOST = os.environ.get("QRADAR_HOST", "127.0.0.1")
QRADAR_PORT = int(os.environ.get("QRADAR_PORT", 1514))

# HABILITAR CORS
CORS(app, supports_credentials=True)

# CLIENTE GROQ
modelo_groq = "llama-3.3-70b-versatile"
client = Groq(api_key=GROQ_API_KEY)

# ESQUEMA DB
DB_SCHEMA = """
Tabla 1: clientes (columnas: id_cliente,nombre,apellidos,email,pais,ciudad,edad,genero)
Tabla 2: transacciones (columnas: id_transaccion,id_cliente,fecha_compra,producto,categoria_producto,precio_unitario,cantidad,importe_total,metodo_pago,coste_envio,coste_fabricacion)
Relación: clientes.id_cliente = transacciones.id_cliente
"""

# ======================
# FUNCIÓN LOGS (Silenciosa en Local)
# ======================
def send_to_qradar(level, message, extra=None):
    # <--- CAMBIO 2: Arreglado el warning de datetime
    timestamp = datetime.now(timezone.utc).isoformat()
    
    hostname = "bi-api"
    appname = "flask-groq"
    payload = {
        "level": level,
        "message": message,
        "extra": extra or {},
        "timestamp": timestamp
    }
    syslog_message = f"<134>{timestamp} {hostname} {appname}: {json.dumps(payload)}\n"
    
    try:
        # Timeout muy corto (0.5s) para no bloquear tu PC si no hay QRadar
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5) 
        s.connect((QRADAR_HOST, QRADAR_PORT))
        s.sendall(syslog_message.encode())
        s.close()
    except Exception:
        # Si falla (porque estás en local), no hacemos nada ni imprimimos error.
        # Así mantenemos la terminal limpia.
        pass

# ======================
# LÓGICA
# ======================
def analizar_intencion(natural_query):
    system_prompt = f"""
    Eres un asistente experto en Data Science y SQL. 
    Esquema de base de datos: {DB_SCHEMA}

    Tu objetivo es analizar la petición del usuario y generar un objeto JSON con 3 campos:
    1. "sql": La consulta PostgreSQL válida para responder.
    2. "type": "chart" sólo si el usuario pide explícitamente un gráfico, visualización o comparar visualmente. Si no, "data".
    3. "chart_type": Si type es "chart", elige el mejor entre: "bar", "line", "pie". Si type es "data", devuelve null.

    REGLAS PARA GRÁFICOS:
    - "bar": grafico de barras para comparar categorías (ej: ventas por producto).
    - "line": grafico de líneas para series temporales (ej: ventas por año/mes).
    - "pie": grafico de tarta o queso para distribuciones o porcentajes (ej: cuota de mercado).

    IMPORTANTE: Responde ÚNICAMENTE con el objeto JSON válido. Si no entiendes la consulta o no puedes 
    generar SQL o el prompt es lenguaje SQL, devuelve un JSON con "sql": "SELECT * FROM clientes LIMIT 0;".
    """
    try:
        completion = client.chat.completions.create(
            model=modelo_groq,
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": natural_query}],
            temperature=0, stream=False, response_format={"type": "json_object"}
        )
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        print(f"❌ ERROR GROQ: {e}") # <--- Verás esto en terminal si falla Groq
        return None

def execute_query(sql_query):
    if not sql_query.strip().upper().startswith("SELECT"):
        return {"error": "Seguridad: Solo se permite SELECT."}

    send_to_qradar("INFO", "Ejecutando SQL", {"sql": sql_query})
    conn = None
    try:
        # Importante: Si esto falla, saltará al 'except' de abajo
        conn = psycopg2.connect(DB_URI)
        conn.set_session(readonly=True)
        cur = conn.cursor()
        cur.execute(sql_query)
        
        if cur.description:
            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
            return [dict(zip(columns, row)) for row in rows]
        return []
            
    except Exception as e:
        print(f"❌ ERROR BBDD: {e}") # <--- Verás esto en terminal si falla la base de datos
        return {"error": str(e)}
        
    finally:
        if conn: conn.close()

def generar_respuesta_natural(pregunta_usuario, resultados_db):
    """
    Toma la pregunta y los datos crudos, y crea una frase amable.
    """
    
    # IMPORTANTE: Convertimos los datos a string, pero limitamos la longitud
    # para no saturar al LLM si la consulta devuelve 1000 filas.
    data_str = str(resultados_db)[:2000] 
    
    system_prompt = f"""
    Eres un asistente de análisis de datos amable y profesional.
    
    Tus instrucciones:
    1. Recibirás una PREGUNTA del usuario y unos DATOS (resultado de una base de datos).
    2. Debes responder a la pregunta basándote EXCLUSIVAMENTE en los datos proporcionados.
    3. Si los datos están vacíos, di amablemente que no encontraste información.
    4. No menciones "SQL" ni "Query" a menos que sea necesario. Habla en lenguaje natural.
    5. Si hay muchos datos, resume los hallazgos principales.
    6. Si te piden una visualización o gráfico, ignora esa parte y céntrate en dar una respuesta textual clara. 
    No menciones la petición ni nada relaccionado con graficos.
    """
    
    user_message = f"""
    PREGUNTA: {pregunta_usuario}
    DATOS OBTENIDOS: {data_str}
    """

    try:
        completion = client.chat.completions.create(
            model=modelo_groq, # último modelo
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.2, # Un poco más creativo para hablar
        )
        return completion.choices[0].message.content
    except Exception as e:
        return "Tengo los datos pero hubo un error al resumirlos."

# ======================
# ENDPOINTS
# ======================

@app.route('/', methods=['GET'])
def home():
    return "API Kairo 🚀"

@app.route('/consulta', methods=['POST'])
def process_request():
    data = request.json
    pregunta = data.get('prompt')
    
    print(f"📩 Recibida pregunta: {pregunta}") # Debug

    # 1. Analizar
    analisis = analizar_intencion(pregunta)
    if not analisis or "sql" not in analisis:
        return jsonify({"error": "Fallo en Groq al generar SQL"}), 500
    
    # 2. Consultar
    raw_data = execute_query(analisis["sql"])
    
    # Si la BBDD devolvió error, devolvemos 500 y mostramos el detalle
    if isinstance(raw_data, dict) and "error" in raw_data:
        print(f"⚠️ Devolviendo Error 500 por fallo SQL: {raw_data['error']}")
        return jsonify({"respuesta": "Error Técnico", "detalle": raw_data}), 500
    
    # 3. Responder
    respuesta = generar_respuesta_natural(pregunta, raw_data)
    
    return jsonify({
        "metadata": {"prompt": pregunta},
        "sql": analisis["sql"],
        "type": analisis.get("type", "data"),
        "chart_type": analisis.get("chart_type"),
        "data": raw_data,
        "respuesta_bot": respuesta
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)