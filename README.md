# Asistente Conversacional: DermaPal 🧴✨

> Asistente conversacional especializado en cuidado facial que recomienda productos de skincare y facilita la compra según tipo de piel, necesidad y presupuesto.

## 🧠 ¿Qué es DermaPal?

DermaPal es un asistente conversacional desarrollado con tecnologías de inteligencia artificial, diseñado para ayudar a las personas a encontrar productos de cuidado facial de manera personalizada y eficiente. A través de una conversación natural, DermaPal recomienda productos según el tipo de piel, necesidades específicas y presupuesto, facilitando además la experiencia de compra.

## ⚙️ Tecnologías utilizadas

-   **Python + Flask**: Backend y servidor web.
-   **Langchain**: Framework para construir agentes de IA.
-   **OpenAI GPT-4.1**: Modelo de lenguaje para generación de respuestas.
-   **Elasticsearch**: Vector store para recuperación de información sobre productos.
-   **PostgreSQL**: Checkpointer para trazabilidad de conversaciones.
-   **Google Cloud Run**: Infraestructura serverless para despliegue del backend.
-   **Docker**: Contenedor del proyecto.

## 🚀 ¿Qué puede hacer el asistente?

1. Saluda y diagnostica tipo de piel y necesidades.
2. Recomienda una rutina facial con productos de la base de datos.
3. Calcula el total de compra e informa si aplica envío gratis.
4. Pregunta modalidad de entrega y método de pago.
5. Cierra el pedido generando un código de compra o indicando datos para transferencia.

## 📦 Cómo desplegar

### 1. Construir la imagen Docker en Google Cloud:

```bash
gcloud builds submit --tag gcr.io/[PROJECT-ID]/dermapal-agent:latest

### 2. Construir la imagen Docker en Google Cloud:
gcloud run deploy dermapal-agent \
  --image gcr.io/[PROJECT-ID]/dermapal-agent:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "OPENAI_API_KEY=<tu_openai_api_key>,LANGCHAIN_API_KEY=<tu_langchain_api_key>,LANGSMITH_ENDPOINT=https://api.smith.langchain.com,LANGCHAIN_PROJECT=gcpaiagent,DB_URI=<tu_db_uri>,es_user=<tu_usuario_es>,es_password=<tu_contraseña_es>"


💡 Reemplaza [PROJECT-ID] y las variables de entorno con tus valores reales.
```

## ✅ Endpoint de prueba

Una vez desplegado, puedes acceder al endpoint así:

https://<tu-url>.run.app/agent?idagente=cliente123&msg=Hola, tengo piel mixta y manchas
