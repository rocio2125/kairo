import os
from flask import Flask, request, jsonify
import psycopg2
from groq import Groq
import json
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)

# CONFIGURACIÓN
DB_URI = os.environ.get("DATABASE_URL")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# --- PRINT PARA DEPURAR ---
print("--- DEBUG INFO ---")
print(f"Directorio actual: {os.getcwd()}")
if GROQ_API_KEY:
    print(f"API Key cargada: {GROQ_API_KEY[:5]}... (Oculta)")
else:
    print("ERROR CRÍTICO: No se encontró GROQ_API_KEY")
print("------------------")
print("--- DEBUG BBDD ---")
if DB_URI:
    print(f"URL BBDD detectada: {DB_URI[:15]}...") # Solo muestra el principio
else:
    print("❌ ERROR: La variable DATABASE_URL está vacía o es None.")
print("------------------")
# -----------------------------

# HABILITAR CORS
CORS(app, supports_credentials=True)

# modelo Groq a usar
modelo_groq = "llama-3.3-70b-versatile"  # Último modelo disponible

# Cliente Groq
client = Groq(api_key=GROQ_API_KEY)

# Esquema para el LLM (Contexto)
DB_SCHEMA = """
Tabla 1: clientes (columnas: id_cliente,nombre,apellidos,email,pais,ciudad,edad,genero)
Tabla 2: transacciones (columnas: id_transaccion,id_cliente,fecha_compra,producto,categoria_producto,precio_unitario,cantidad,importe_total,metodo_pago,coste_envio,coste_fabricacion)
Relación: clientes.id_cliente = transacciones.id_cliente
"""
# --- Analizar intención ---
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

    IMPORTANTE: Responde ÚNICAMENTE con el objeto JSON válido.
    """

    try:
        completion = client.chat.completions.create(
            model=modelo_groq, # último modelo
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": natural_query}
            ],
            temperature=0,
            stream=False,
            # Forzamos salida JSON
            response_format={"type": "json_object"}
        )
        
        # Parseamos el texto JSON a un diccionario de Python real
        respuesta_json = json.loads(completion.choices[0].message.content)
        return respuesta_json
        
    except Exception as e:
        print(f"❌ Error en Groq: {e}")
        return None
    
# --- Generar SQL ---
def get_sql_from_groq(natural_query):
    system_prompt = f"""
    Eres un experto SQL. Esquema: {DB_SCHEMA}
    INSTRUCCIONES: Devuelve SOLO el código SQL PostgreSQL para la pregunta del usuario.
    Sin markdown, sin explicaciones.
    No puedes modificar ni borrar las tablas.
    """
    try:
        completion = client.chat.completions.create(
            model=modelo_groq, # último modelo
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": natural_query}
            ],
            temperature=0, 
            stream=False,
        )
        return completion.choices[0].message.content.replace("```sql", "").replace("```", "").strip()
    except Exception as e:
        print(f"❌ ERROR REAL EN GROQ: {e}")
        return None

# --- Ejecutar en DB ---
def execute_query(sql_query):
    conn = None
    try:
        conn = psycopg2.connect(DB_URI)
        cur = conn.cursor()
        cur.execute(sql_query)
        
        if cur.description:
            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
            results = [dict(zip(columns, row)) for row in rows]
            return results
        else:
            return [] # No devolvió datos
    except Exception as e:
        return {"error": str(e)}
    finally:
        if conn:
            conn.close()

# --- Generar Respuesta Natural ---
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
    4. No menciones "SQL" ni "Query" ni "ID" a menos que sea necesario. Habla en lenguaje natural.
    5. Si hay muchos datos, resume los hallazgos principales.
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

# ENPOINT DE BIENVENIDA
@app.route('/', methods=['GET'])
def home():
    return "Estamos en funcionamiento equipo."

# ENDPOINT PRINCIPAL
@app.route('/consulta', methods=['POST'])
def process_request():
    data = request.json
    pregunta = data.get('prompt')
    
    if not pregunta:
        return jsonify({"error": "Falta el prompt"}), 400

    # 1. Analizar intención (SQL + Gráfico)
    analisis = analizar_intencion(pregunta)
    
    if not analisis or "sql" not in analisis:
        return jsonify({"error": "No se pudo generar la consulta."}), 500

    sql_query = analisis["sql"]
    tipo_respuesta = analisis.get("type", "data")
    tipo_grafico = analisis.get("chart_type", None)

    # 2. Consultar Datos
    raw_data = execute_query(sql_query)
    
    if isinstance(raw_data, dict) and "error" in raw_data:
        return jsonify({"respuesta": "Error SQL", "detalle": raw_data}), 500

    # 3. Generar Conversación
    respuesta_bot = generar_respuesta_natural(pregunta, raw_data)
    
    # 4. Devolver TODO al frontend
    return jsonify({
        "metadata": {
                "prompt": pregunta
            },
        "sql": sql_query,
        "type": tipo_respuesta,       
        "chart_type": tipo_grafico,   
        "data": raw_data,             
        "respuesta_bot": respuesta_bot
    })
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
