# Guía de Usuario para el Chatbot de Consultas SQL

## ¿Qué es este chatbot?
Este chatbot permite a cualquier usuario realizar preguntas sobre los datos de e-commerce en lenguaje natural y obtener visualizaciones, datos y un análisis.

---

## ¿Cómo funciona?
1. **Escribe tu pregunta** en el chat, por ejemplo:
   - "¿Cuántas ventas hubo en 2024?"
   - "Top 10 productos más vendidos en 2023 por categoria"
   - "Promedio de ventas por país en 2024"
   - "Genera un gráfico con la cuota de medios de pago"
   - "Muestra los 50 clientes con mayor AOV junto a sus datos demográficos"
   - "Calcula el beneficio total por país y genera un grafico de barras"

2. **El chatbot interpreta tu pregunta** y la traduce a una consulta SQL, después analiza el resultado.
3. **Recibes la respuesta** directamente en el chat, sin necesidad de saber SQL ni manejar bases de datos.

---

## Ejemplos de preguntas que puedes hacer
- ¿Cuántas transacciones hubo en 2024?
- Ventas totales el 2024 por país
- Muéstrame el promedio de ventas en 2023 por trimestre
- Top 5 productos más vendidos en 2024
- Número de clientes menores de 30 en México en 2024
- Mediana de importe_total por mes en 2023
- Ventas máximas por país en enero

---

## ¿Qué tipo de información puedes consultar?
- **Métricas**: ventas, ingresos, cantidad, precio, etc.
- **Filtros**: por año, mes, trimestre, país, ciudad, producto, categoría, género, edad.
- **Agrupaciones**: por año, mes, trimestre, país, etc.
- **Rankings**: top productos, mayores ventas, etc.
- **Gráficos**: de barras, de línea o de quesito sobre ventas, productos, etc. por meses, años, cantidades o frecuencias. Eso sí, debes indicar qué tipo de gráfico quieres específicamente.

---

## Consejos para mejores resultados
- Usa frases claras y directas.
- Puedes preguntar en cualquier idioma.
- No te olvides de indicar tu gráfico favorito: ¡de líneas, barras o incluso de quesito!

Ten en cuenta la estructura de la base de datos:
Tabla clientes: 
   columnas: id_cliente, nombre, apellidos, email, pais, ciudad, edad, genero
Tabla transacciones: 
   columnas: id_transaccion, id_cliente, fecha_compra, producto, categoria_producto, precio_unitario, cantidad,importe_total, metodo_pago, coste_envio, coste_fabricacion
---

## ¿Qué NO necesitas saber?
- No necesitas saber SQL.
- No necesitas saber cómo funciona la base de datos.
- No necesitas instalar nada: solo usa el chat.

---

## ¿Qué hacer si tienes problemas?
- Si el chatbot no entiende tu pregunta, intenta con otra redacción o consulta los ejemplos.
- Si recibes un mensaje de error, contacta con el soporte técnico.

---

## ¿Listo para empezar?
¡Ya puedes comenzar a explorar tus datos de e-commerce de forma sencilla y natural! No importa si nunca has usado una base de datos: este chatbot está diseñado para ayudarte a obtener la información que necesitas con solo escribir tu pregunta.

Recuerda:
- No tengas miedo de experimentar con diferentes preguntas.
- Si tienes dudas, revisa los ejemplos o consulta con tu equipo.

¿Tienes alguna pregunta, sugerencia o necesitas soporte?
- Contáctanos a través de GitHub o LinkedIn.

¡Saca el máximo partido a tus datos con Kairo!
