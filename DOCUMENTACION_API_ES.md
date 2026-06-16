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

# Ejecutar el servidor API
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

## 📋 **Endpoints de la API**

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
```
Genera un podcast usando el sistema empresarial de agentes IA.

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

**Respuesta:**
```json
{
  "success": true,
  "message": "Podcast generado exitosamente con patrones empresariales de agentes IA",
  "audio_path": "PodcastOutput/podcast_20250925_065140.mp3",
  "articles_processed": 15,
  "tasks_completed": 4,
  "a2a_quality_score": 0.92,
  "system_status": {
    "system_health": "healthy",
    "active_agents": 4
  },
  "generation_time": 45.3
}
```

### **📁 Listar Archivos**
```http
GET /files
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
      "download_url": "/download/podcast_20250925_065140.mp3"
    }
  ]
}
```

### **📥 Descargar Archivo**
```http
GET /download/{filename}
```
Descarga un archivo de podcast generado.

**Parámetros:**
- `filename` (string): Nombre del archivo a descargar

**Respuesta:** Descarga de archivo binario

### **📊 Estado del Sistema**
```http
GET /status
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

# Generar podcast en inglés
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{"language": "en", "voice": "Aria"}'

# Generar podcast en español
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{"language": "es", "voice": "Sarah"}'

# Listar archivos generados
curl -X GET "http://localhost:8000/files"

# Descargar un podcast
curl -X GET "http://localhost:8000/download/podcast_20250925_065140.mp3" \
  --output podcast.mp3
```

### **Ejemplo Cliente Python**

```python
import requests
import json

# URL base de la API
BASE_URL = "http://localhost:8000"

def generate_podcast(language="en", voice="Aria"):
    """Generar un podcast usando la API."""
    response = requests.post(
        f"{BASE_URL}/generate",
        json={"language": language, "voice": voice}
    )
    return response.json()

def download_podcast(filename, output_path):
    """Descargar un podcast generado."""
    response = requests.get(f"{BASE_URL}/download/{filename}")
    with open(output_path, 'wb') as f:
        f.write(response.content)

# Uso
result = generate_podcast("es", "Sarah")
if result["success"]:
    print(f"Podcast generado: {result['audio_path']}")
    print(f"Puntuación de Calidad A2A: {result['a2a_quality_score']}")
```

### **Ejemplo JavaScript/Node.js**

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:8000';

async function generatePodcast(language = 'en', voice = 'Aria') {
  try {
    const response = await axios.post(`${BASE_URL}/generate`, {
      language,
      voice
    });
    return response.data;
  } catch (error) {
    console.error('Error generando podcast:', error.response?.data);
    throw error;
  }
}

// Uso
generatePodcast('es', 'Sarah')
  .then(result => {
    console.log('Podcast generado:', result.audio_path);
    console.log('Puntuación de Calidad A2A:', result.a2a_quality_score);
  })
  .catch(console.error);
```

## 🐳 **Configuración Docker**

### **Variables de Entorno**

```env
# Claves API Requeridas
ANTHROPIC_API_KEY=tu_clave_anthropic_aqui
ELEVEN_API_KEY=tu_clave_elevenlabs_aqui

# Claves API Opcionales
OPENAI_API_KEY=tu_clave_openai_aqui
NEWS_API_KEY=tu_clave_news_api_aqui

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

# Ejecutar el contenedor
docker run -p 8000:8000 --env-file .env ai-parrot-enterprise

# Ejecutar con docker-compose
docker-compose up --build

# Ver logs
docker-compose logs -f ai-parrot

# Detener el servicio
docker-compose down
```

## 🔒 **Consideraciones de Seguridad**

1. **Claves API**: Nunca confirmes claves API en control de versiones
2. **Entorno**: Usa archivos `.env` o variables de entorno
3. **Red**: Considera ejecutar detrás de un proxy reverso (nginx)
4. **Autenticación**: Añade autenticación API para uso en producción
5. **Limitación de Tasa**: Implementa limitación de tasa para despliegues en producción

## 📈 **Monitoreo**

La API proporciona varios endpoints de monitoreo:

- `/health` - Verificación básica de salud
- `/status` - Estado detallado del sistema
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
