# 🤖 KAIRO: AI-Powered SQL Assistant (RAG Architecture)

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Framework](https://img.shields.io/badge/Framework-Flask-lightgrey)
![AI](https://img.shields.io/badge/LLM-Llama%203.3%20(Groq)-red)
![Architecture](https://img.shields.io/badge/Architecture-RAG-green)

## 📋 Descripción del Proyecto
**KAIRO** es un asistente inteligente diseñado para democratizar el acceso a los datos corporativos. Permite a usuarios no técnicos realizar consultas complejas a bases de datos SQL utilizando lenguaje natural. 

El sistema utiliza una arquitectura **RAG (Retrieval-Augmented Generation)** para interpretar la intención del usuario, generar la consulta SQL precisa, ejecutarla de forma segura y devolver una respuesta analítica enriquecida. Este proyecto fue desarrollado de forma multidisciplinar junto a equipos de Full Stack y Ciberseguridad.

## 🏗️ Arquitectura de la API
Como responsable de la lógica de datos y backend, diseñé un flujo de información robusto:

1.  **Capa de Procesamiento (NLP)**: Integración con el modelo **Llama 3.3** a través de la API de **Groq** para la traducción de lenguaje natural a SQL.
2.  **Motor RAG**: Implementación de una lógica de recuperación que contextualiza las consultas con el esquema de la base de datos en tiempo real.
3.  **Orquestación**: Desarrollo de una API con **Flask** que gestiona las peticiones, la validación de prompts y el formateo de los resultados para el frontend.
4.  **Seguridad y Hardening**: Colaboración activa con el equipo de Ciberseguridad para implementar protocolos de seguridad de red y protección contra inyecciones SQL.

## 🚀 Funcionalidades Técnicas
* **Generación de SQL en Tiempo Real**: Traducción precisa de preguntas humanas a consultas PostgreSQL/MySQL.
* **Análisis Inteligente**: El sistema no solo entrega datos, sino que proporciona una interpretación de los mismos basada en el contexto del negocio.
* **Interfaz de API Documentada**: Endpoints optimizados para la comunicación fluida con el frontend.
* **Pipeline de Datos Seguro**: Flujo de información securizado para garantizar la integridad y privacidad de los datos consultados.

## 🛠️ Stack Tecnológico
* **Backend & Lógica**: Python, Flask.
* **IA & LLM**: Groq Cloud, Llama 3.3, LangChain (conceptual).
* **Bases de Datos**: SQL (Estructura corporativa).
* **Seguridad**: Protocolos de Hardening y Redes Seguras.

## 👤 Autora
**Rocío Ortiz Gutiérrez**
* **LinkedIn**: [https://www.linkedin.com/in/rocioortizg/](https://www.linkedin.com/in/rocioortizg/)
* **GitHub**: [https://github.com/rocio2125](https://github.com/rocio2125)
* **Demo & Post**: [Detalles del Proyecto en LinkedIn](https://www.linkedin.com/posts/rocioortizg_datascience-rag-generativeai-activity-7408528158389452800-xmKG)
