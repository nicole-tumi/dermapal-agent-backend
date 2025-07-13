from dotenv import load_dotenv
load_dotenv()


from langchain_openai import ChatOpenAI
import os
from flask import Flask, jsonify, request
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage
from langchain_openai import OpenAIEmbeddings
from langchain_elasticsearch import ElasticsearchStore
from psycopg_pool import ConnectionPool
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.prebuilt import create_react_agent


# Configuración de variables de trazabilidad para LangSmith
os.environ["LANGSMITH_ENDPOINT"] = os.environ.get("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
os.environ["LANGCHAIN_API_KEY"] = os.environ.get("LANGCHAIN_API_KEY", "")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = os.environ.get("LANGCHAIN_PROJECT", "gcpaiagent")
os.environ["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY", "")

# Inicialización de la aplicación Flask
app = Flask(__name__)

# Ruta principal que atiende las consultas del agente
@app.route('/agent', methods=['GET'])
def main():
    # Captura de parámetros enviados por GET
    id_agente = request.args.get('idagente')
    msg = request.args.get('msg')

    # Lectura de variables de entorno para base de datos y Elasticsearch
    DB_URI = os.environ.get("DB_URI", "")
    es_user = os.environ.get("es_user", "")
    es_password = os.environ.get("es_password", "")

    # Configuración opcional para conexiones PostgreSQL
    connection_kwargs = {
        "autocommit": True,
        "prepare_threshold": 0,
    }

    # Configuración del vector store usando Elasticsearch
    db_query = ElasticsearchStore(
        es_url="http://35.193.54.75:9200", #URL Elasticsearch
        es_user=es_user,
        es_password=es_password,
        index_name="skincare-products", #índice con productos
        embedding=OpenAIEmbeddings()
)

    # Herramienta RAG
    # Conversión del vector store en una herramienta de recuperación
    retriever = db_query.as_retriever()
    tool_rag = retriever.as_tool(
        name="busqueda_productos",
        description="Consulta en la información de productos de cuidado facial como limpiadores, tratamientos, hidratantes y protectores solares.",
    )

    # Inicializa conexión a la base de datos para memoria conversacional
    with ConnectionPool(
            # Example configuration
            conninfo=DB_URI,
            max_size=20,
            kwargs=connection_kwargs,
    ) as pool:
        checkpointer = PostgresSaver(pool) #Historial en Postgres

        # Modelo de lenguaje (GPT-4.1)
        model = ChatOpenAI(model="gpt-4.1-2025-04-14")

        # Agrupamos las herramientas
        tolkit = [tool_rag]

        # Prompt que define el comportamiento del asistente DermaPal
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system",
                """
                Eres DermaPal, un asistente conversacional especializado en cuidado facial y belleza. Estás diseñado para ayudar a las personas a descubrir productos adecuados para su piel y facilitar la compra de forma amigable, rápida y confiable.  
                Utiliza únicamente las herramientas disponibles para responder y brindar información.  
                Si no cuentas con una herramienta específica para resolver una pregunta, infórmalo claramente e indica de qué formas puedes ayudar.

                Tu misión es conversar con cercanía, recomendar productos según las necesidades de cada usuario, armar una rutina simple, calcular el total y cerrar el pedido.  
                También, considera que lo que recomiendes es una sugerencia y, si desean una recomendación dermatológica, deben acudir a su médico.

                Sigue esta estructura paso a paso:

                1. Saludo y diagnóstico: Saluda de manera cálida y amable. Pregunta por el tipo de piel (seca, grasa, mixta o sensible) y si hay alguna preocupación específica (manchas, acné, resequedad, brillo, etc.).

                2. Recomendación de rutina: Sugiere productos de tu base de datos para una rutina facial básica (por ejemplo: limpiador, tratamiento, hidratante y protector solar). Incluye nombre del producto, paso, tienda y precio. Solo usa productos que tengas registrados.

                3. Resumen de compra: Calcula el total estimado, muestra la disponibilidad y menciona la tienda donde se pueden adquirir.

                4. Opciones de envío y pago:
                - El envío es gratuito si el total supera los S/150. De lo contrario, se añade S/10.
                - Pregunta si prefiere recojo en tienda o entrega a domicilio.
                - En caso de entrega a domicilio, el costo de envío es gratis.
                - Solicita nombre completo y si desea pagar por transferencia o en tienda.

                5. Cierre de compra:
                - Si elige transferencia, indica que la cuenta es 12345678 en DermaBanco.
                - Si elige tienda, genera un código de pedido con el siguiente formato: AAAAMMDD_HHMMSS_NombreApellido (por ejemplo: 20250713_211504_CarlaLopez)

                Estilo de conversación:
                - Sé cálido, conciso y humano.
                - Evita tecnicismos a menos que el cliente los utilice.
                - Si no puedes responder algo, dilo con transparencia y guía al usuario sobre lo que sí puedes hacer.
                """),
                ("human", "{messages}"),
            ]
        )

        # Se crea el agente reactivo con el modelo, herramientas y memoria
        agent_executor = create_react_agent(model, tolkit, checkpointer=checkpointer, prompt=prompt)
        
        # Se configura un ID de hilo para mantener la sesión
        config = {"configurable": {"thread_id": id_agente}}
        
        # El agente responde al mensaje recibido
        response = agent_executor.invoke({"messages": [HumanMessage(content=msg)]}, config=config)
        
        # Se devuelve el último mensaje generado por el agente
        return response['messages'][-1].content

# Punto de entrada cuando se ejecuta el script directamente
if __name__ == '__main__':
    # Se inicia el servidor Flask escuchando en el puerto 8080, necesario para Cloud Run
    app.run(host='0.0.0.0', port=8080)