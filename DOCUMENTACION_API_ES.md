<p align="center">
  <img src="assets/ai-parrot-logo.png" alt="AI-Parrot logo" width="320" />
</p>

# 🌐 Documentación API Empresarial AI-Parrot

## 🚀 **Inicio Rápido**

### **Despliegue Docker (Recomendado)**

1. **Clonar y Configurar**
   ```bash
   git clone <repository-url>
   cd AI-parrot
   cp .env.template .env
   # Editar .env con tus claves API
   ```

2. **Construir y Ejecutar**
   ```bash
   docker-compose up --build
   ```

3. **Acceder a la API**
   - API: http://localhost:8000
   - Documentos Interactivos: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### **Desarrollo Local**

```bash
# Instalar dependencias
pip install -r requirements.txt
pip install -r requirements-api.txt

# Ejecutar el servidor API en localhost
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

## 📋 **Endpoints de la API**

### **🔐 Autenticación Opcional**

Por defecto, el desarrollo local no requiere token. Si defines `AI_PARROT_API_TOKEN`, los endpoints protegidos requieren una de estas cabeceras:

```http
Authorization: Bearer tu_token
```

```http
X-API-Key: tu_token
```

Úsalo en despliegues no locales. Protege endpoints que pueden consumir créditos de API, exponer logs, listar archivos, descargar salidas o inspeccionar memoria. Las verificaciones de salud permanecen abiertas para que Docker y los monitores funcionen sin secreto.

### **🏠 Endpoint Raíz**
```http
GET /
```
Devuelve información del sistema y endpoints disponibles.

**Respuesta:**
```json
{
  "name": "Generador de Podcasts Empresarial AI-Parrot",
  "version": "1.0.0",
  "description": "Sistema Empresarial de Agentes IA para Generación Inteligente de Podcasts",
  "enterprise_patterns": "A2A + Supervisor + MCP + Circuit Breaker + Observer",
  "docs": "/docs",
  "health": "/health"
}
```

### **💚 Verificación de Salud**
```http
GET /health
```
Devuelve el estado de salud del sistema y validación de claves API.

**Respuesta:**
```json
{
  "status": "healthy",
  "timestamp": "2025-09-25T06:51:40",
  "version": "1.0.0",
  "enterprise_patterns": {
    "a2a_collaborative_assessment": true,
    "agent_supervisor_coordination": true,
    "mcp_integration_sse_transport": true,
    "circuit_breaker_resilience": true,
    "observer_pattern_monitoring": true
  },
  "api_keys": {
    "anthropic": true,
    "openai": true,
    "elevenlabs": true,
    "news_api": false
  }
}
```

### **🎙️ Generar Podcast**
```http
POST /generate
POST /api/generate
```
Encola una tarea de generación de podcast y responde inmediatamente.

La generación llama servicios RSS/MCP, modelos LLM, traducción y texto a voz. Por eso la API usa un flujo por tareas:

1. Envía `POST /generate` o `POST /api/generate`.
2. Lee el `task_id` de la respuesta.
3. Consulta `GET /tasks/{task_id}` o `GET /api/tasks/{task_id}` hasta que el estado sea `completed` o `failed`.
4. Descarga el archivo generado desde `/download/{filename}`.

**Cuerpo de la Solicitud:**
```json
{
  "language": "en",
  "voice": "Aria"
}
```

**Parámetros:**
- `language` (string): "en" para inglés, "es" para español
- `voice` (string): Nombre de voz ElevenLabs (ej., "Aria", "Sarah", "Lily")

**Respuesta encolada (`202 Accepted`):**
```json
{
  "success": true,
  "message": "Podcast generation queued",
  "task_id": "8d6f68b8-6c1a-4b72-a6db-0cbb24a2a1d0"
}
```

### **⏳ Estado de Tarea**
```http
GET /tasks/{task_id}
GET /api/tasks/{task_id}
```
Devuelve el estado actual de una tarea de generación.

**Estados:**
- `queued`: La API aceptó la solicitud y aún no empezó el trabajo.
- `running`: Los agentes están obteniendo contenido, resumiendo, escribiendo el guion, traduciendo o generando audio.
- `completed`: La tarea terminó y `result` contiene los metadatos de salida.
- `failed`: La tarea falló y `error` explica la causa.

**Respuesta completada:**
```json
{
  "task_id": "8d6f68b8-6c1a-4b72-a6db-0cbb24a2a1d0",
  "status": "completed",
  "created_at": "2026-06-16T18:30:00",
  "updated_at": "2026-06-16T18:31:15",
  "request": {
    "language": "es",
    "voice": "Sarah"
  },
  "result": {
    "success": true,
    "audio_path": "PodcastOutput/podcast_20260616_183115_Sarah_es.mp3",
    "articles_processed": 15,
    "tasks_completed": 4,
    "generation_time": 75.3
  },
  "error": null
}
```

### **📁 Listar Archivos**
```http
GET /files
GET /api/files
```
Lista todos los archivos de podcast generados.

**Respuesta:**
```json
{
  "files": [
    {
      "name": "podcast_20250925_065140.mp3",
      "size": 2457600,
      "created": "2025-09-25T06:51:40",
      "modified": "2025-09-25T06:52:25",
      "download_url": "/download/podcast_20260616_183115_Sarah_es.mp3"
    }
  ]
}
```

### **📥 Descargar Archivo**
```http
GET /download/{filename}
GET /api/download/{filename}
```
Descarga un archivo de podcast generado.

**Parámetros:**
- `filename` (string): Nombre del archivo a descargar

**Respuesta:** Descarga de archivo binario

### **📊 Estado del Sistema**
```http
GET /status
GET /api/status
```
Devuelve estado detallado del sistema y métricas.

**Respuesta:**
```json
{
  "system": "Sistema Empresarial AI-Parrot",
  "status": "operational",
  "enterprise_patterns": {
    "a2a_collaborative_assessment": "active",
    "agent_supervisor_coordination": "active",
    "mcp_integration_sse_transport": "active",
    "circuit_breaker_resilience": "active",
    "observer_pattern_monitoring": "active"
  },
  "api_keys": {
    "anthropic": "✅ Disponible",
    "openai": "✅ Disponible",
    "elevenlabs": "✅ Disponible",
    "news_api": "⚠️ Opcional"
  },
  "statistics": {
    "podcasts_generated": 5,
    "supported_languages": ["en", "es"],
    "supported_voices": ["Aria", "Sarah", "Lily", "Custom"]
  },
  "timestamp": "2025-09-25T06:51:40"
}
```

## 🔧 **Ejemplos de Uso**

### **Ejemplos cURL**

```bash
# Verificación de salud
curl -X GET "http://localhost:8000/health"

# Encolar podcast en español
TASK_ID=$(curl -s -X POST "http://localhost:8000/api/generate" \
  -H "Content-Type: application/json" \
  -d '{"language": "es", "voice": "Sarah"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['task_id'])")

# Consultar hasta que el estado sea completed o failed
curl -X GET "http://localhost:8000/api/tasks/${TASK_ID}"

# Listar archivos generados
curl -X GET "http://localhost:8000/api/files"

# Descargar un podcast
curl -X GET "http://localhost:8000/api/download/podcast_20260616_183115_Sarah_es.mp3" \
  --output podcast.mp3
```

### **Ejemplo Cliente Python**

```python
import requests
import time
import os

# URL base de la API
BASE_URL = "http://localhost:8000"
HEADERS = {}
if os.getenv("AI_PARROT_API_TOKEN"):
    HEADERS["Authorization"] = f"Bearer {os.environ['AI_PARROT_API_TOKEN']}"

def generate_podcast(language="en", voice="Aria"):
    """Encolar un podcast y esperar a que termine."""
    response = requests.post(
        f"{BASE_URL}/api/generate",
        json={"language": language, "voice": voice},
        headers=HEADERS,
        timeout=30,
    )
    response.raise_for_status()
    task_id = response.json()["task_id"]

    while True:
        task_response = requests.get(
            f"{BASE_URL}/api/tasks/{task_id}",
            headers=HEADERS,
            timeout=10,
        )
        task_response.raise_for_status()
        task = task_response.json()

        if task["status"] == "completed":
            return task["result"]
        if task["status"] == "failed":
            raise RuntimeError(task["error"])

        time.sleep(5)

def download_podcast(filename, output_path):
    """Descargar un podcast generado."""
    response = requests.get(f"{BASE_URL}/api/download/{filename}", headers=HEADERS)
    response.raise_for_status()
    with open(output_path, 'wb') as f:
        f.write(response.content)

# Uso
result = generate_podcast("es", "Sarah")
if result["success"]:
    print(f"Podcast generado: {result['audio_path']}")
```

### **Ejemplo JavaScript/Node.js**

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:8000';
const HEADERS = process.env.AI_PARROT_API_TOKEN
  ? { Authorization: `Bearer ${process.env.AI_PARROT_API_TOKEN}` }
  : {};

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function generatePodcast(language = 'en', voice = 'Aria') {
  try {
    const queued = await axios.post(
      `${BASE_URL}/api/generate`,
      { language, voice },
      { headers: HEADERS }
    );

    const taskId = queued.data.task_id;
    while (true) {
      const task = await axios.get(`${BASE_URL}/api/tasks/${taskId}`, { headers: HEADERS });
      if (task.data.status === 'completed') return task.data.result;
      if (task.data.status === 'failed') throw new Error(task.data.error);
      await sleep(5000);
    }
  } catch (error) {
    console.error('Error generando podcast:', error.response?.data);
    throw error;
  }
}

// Uso
generatePodcast('es', 'Sarah')
  .then(result => {
    console.log('Podcast generado:', result.audio_path);
  })
  .catch(console.error);
```

## 🐳 **Configuración Docker**

### **Variables de Entorno**

```env
# Claves API Requeridas
ANTHROPIC_API_KEY=tu_clave_anthropic_aqui
ELEVENLABS_API_KEY=tu_clave_elevenlabs_aqui

# Claves API Opcionales
OPENAI_API_KEY=tu_clave_openai_aqui
NEWS_API_KEY=tu_clave_news_api_aqui
AI_PARROT_API_TOKEN=cambia_esto_para_despliegues_no_locales

# Configuración Servidor MCP
MCP_SERVER_URL=http://localhost:3002/mcp
MCP_SSE_URL=http://localhost:3002/sse
MCP_SERVER_NAME=local-mcp-server

# Logging
LOG_LEVEL=INFO
```

### **Comandos Docker**

```bash
# Construir la imagen
docker build -t ai-parrot-enterprise .

# Ejecutar el contenedor en localhost
docker run -p 127.0.0.1:8000:8000 --env-file .env ai-parrot-enterprise

# Ejecutar con docker-compose
docker-compose up --build

# Ver logs
docker-compose logs -f ai-parrot-api

# Detener el servicio
docker-compose down
```

## 🔒 **Consideraciones de Seguridad**

1. **Claves API**: Nunca confirmes claves API en control de versiones
2. **Entorno**: Usa archivos `.env` o variables de entorno
3. **Red**: Considera ejecutar detrás de un proxy reverso (nginx)
4. **Autenticación**: Define `AI_PARROT_API_TOKEN` para despliegues no locales
5. **Limitación de Tasa**: Implementa limitación de tasa para despliegues en producción

## 📈 **Monitoreo**

La API proporciona varios endpoints de monitoreo:

- `/health` o `/api/health` - Verificación básica de salud
- `/status` o `/api/status` - Estado detallado del sistema
- `/tasks/{task_id}` o `/api/tasks/{task_id}` - Progreso de generación de podcasts
- Verificaciones de salud del contenedor vía Docker

## 🚀 **Despliegue en Producción**

Para despliegue en producción, considera:

1. **Proxy Reverso**: Usa nginx o Traefik
2. **SSL/TLS**: Habilita HTTPS
3. **Autenticación**: Añade autenticación de clave API
4. **Limitación de Tasa**: Implementa limitación de tasa de solicitudes
5. **Monitoreo**: Añade métricas Prometheus
6. **Logging**: Logging centralizado con stack ELK
7. **Escalado**: Usa Kubernetes para escalado horizontal

---

**La API Empresarial AI-Parrot proporciona una interfaz RESTful limpia al poderoso sistema empresarial de agentes IA, facilitando la integración de generación de podcasts en cualquier aplicación o flujo de trabajo.** 🎯
