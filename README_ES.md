<p align="center">
  <img src="assets/ai-parrot-logo.png" alt="AI-Parrot logo" width="320" />
</p>

# 🤖 Generador de Podcasts AI-Parrot

**Sistema Empresarial de Agentes IA para Generación Inteligente de Podcasts**

🏗️ **Arquitectura Central**: Construido con patrones de agentes IA de nivel empresarial como diseño fundamental del sistema. Esto no es solo un generador de podcasts - es una demostración integral de coordinación multi-agente lista para producción.

🤖 **Patrones Empresariales Integrados**:
- 🤝 **Evaluación Colaborativa A2A** - Los agentes colaboran en puntuación de calidad
- 🏛️ **Coordinación de Supervisor de Agentes** - Orquestación jerárquica de tareas
- 🔗 **Integración MCP con Transporte SSE** - Obtención dinámica de contenido
- 🔄 **Resistencia Circuit Breaker** - Tolerancia a fallos y degradación elegante
- 👁️ **Monitoreo Patrón Observer** - Observabilidad del sistema en tiempo real

## ✨ Características

| Tarea | Modelo | Propósito |
|-------|--------|-----------|
| Clasificación de Artículos | Claude Haiku | Puntuación de relevancia rápida y rentable |
| Resumen de Artículos | Claude Sonnet | Velocidad y calidad equilibradas |
| Generación de Guión | Claude Opus | Contenido creativo de alta calidad |
| Refinamiento de Guión | GPT-4 (o Claude Sonnet) | Optimización precisa para TTS |

## 🌟 Funcionalidades

- **Obtención Automatizada de Artículos**: Obtiene los últimos artículos de feeds RSS
- **Resumen Impulsado por IA**: Usa Claude AI para procesar y resumir contenido
- **Narración de Sonido Natural**: Convierte texto a voz usando voces de alta calidad de ElevenLabs
- **Soporte Multi-idioma**: Genera podcasts en inglés o español
- **Voces Personalizables**: Elige entre múltiples voces de alta calidad
- **Salida Personalizable**: Controla voz, número de artículos y formato de salida
- **Flujo de Trabajo LangGraph**: Pipeline robusto para generación de podcasts

## 🚀 Inicio Rápido

### Prerrequisitos

- Python 3.8+
- [UV](https://github.com/astral-sh/uv) para gestión de entorno virtual y dependencias
- Claves API para servicios requeridos (ver abajo)
- (Opcional) `ffmpeg` para procesamiento de audio (instalado por defecto en la mayoría de sistemas)

### Claves API Requeridas

#### 🔑 Requeridas
- `ANTHROPIC_API_KEY` - Para modelos Claude AI (Sonnet, Haiku, Opus)

#### 📝 Opcionales pero Recomendadas
- `OPENAI_API_KEY` - Para refinamiento de guión GPT-4 (recurre a Claude Sonnet si no está disponible)
- `ELEVENLABS_API_KEY` - Para texto a voz de alta calidad (requerido para salida de audio)
- `NEWS_API_KEY` - Para integración News API (recurre a feeds RSS si no está disponible)

Añádelas a tu archivo `.env` en la raíz del proyecto.

### Instalación

1. Clona el repositorio:
   ```bash
   git clone <repository-url>
   cd AI-parrot
   ```

2. Configura el entorno (automático con el script):
   ```bash
   # Hacer el script ejecutable
   chmod +x run_podcast.sh
   
   # Ejecutar el script (configurará el entorno si es necesario)
   ./run_podcast.sh --help
   ```

### Usando el Script (Recomendado)

```bash
# Hacer el script ejecutable (solo necesario una vez)
chmod +x run_podcast.sh

# Generar podcast en inglés con voz por defecto
./run_podcast.sh --language en --voice "Aria"

# Generar podcast en español
./run_podcast.sh --language es --voice "Sarah"

# Mostrar ayuda
./run_podcast.sh --help
```

### Ejecución Manual

```bash
# Activar el entorno virtual
source .venv/bin/activate  # En Windows: .venv\Scripts\activate

# Generar podcast con patrones IA empresariales
python -m podcast_generator.main --language en --voice "Aria"

# Podcast en español
python -m podcast_generator.main --language es --voice "Sarah"
```

### 🌐 Interfaz Web Unificada

El sistema proporciona tanto FastAPI como Streamlit en un solo contenedor:

```bash
# Ejecutar servicio unificado con Docker (Recomendado)
docker-compose up --build

# O ejecutar localmente
./run_api.sh      # Solo API
./run_ui.sh       # Solo Streamlit

# Acceder al sistema unificado
# - UI Streamlit: http://localhost:8501 (Interfaz Interactiva)
# - FastAPI: http://localhost:8000/api (REST API)
# - Documentos Interactivos: http://localhost:8000/api/docs
# - Información del Sistema: http://localhost:8000/info
# - Verificación de Salud: http://localhost:8000/api/health
```

**Uso de API:**
```bash
# Generar podcast vía API
curl -X POST "http://localhost:8000/api/generate" \
  -H "Content-Type: application/json" \
  -d '{"language": "en", "voice": "Aria"}'

# Verificar estado del sistema
curl -X GET "http://localhost:8000/api/status"
```

## 📚 Documentación

Para documentación detallada, por favor consulta los siguientes archivos en el directorio `docs/`:

- [ARCHITECTURE.md](docs/ARCHITECTURE.md): Arquitectura y diseño del sistema
- [CODE_EXPLANATION.md](docs/CODE_EXPLANATION.md): Documentación detallada del código
- [QUICKSTART.md](docs/QUICKSTART.md): Guía de inicio

## 🔧 Configuración

### Variables de Entorno

Crea un archivo `.env` con las siguientes variables:

```env
# Requeridas
ANTHROPIC_API_KEY=tu_clave_anthropic_aqui

# Opcionales pero recomendadas
OPENAI_API_KEY=tu_clave_openai_aqui  # Requerida para traducción al español
ELEVENLABS_API_KEY=tu_clave_elevenlabs_aqui  # Requerida para generación de audio
NEWS_API_KEY=tu_clave_newsapi_aqui  # Recurre a feeds RSS si no está disponible

# Configuración Servidor MCP (Opcional)
MCP_SERVER_URL=http://localhost:3002/mcp
MCP_SSE_URL=http://localhost:3002/sse
MCP_SERVER_NAME=local-mcp-server
```

### 🔗 Integración MCP

El sistema soporta **Protocolo de Contexto de Modelo (MCP)** para obtención dinámica de contenido con respaldo inteligente a feeds RSS.

**Servidor MCP**: Para obtención mejorada de artículos, puedes usar nuestro servidor RSS MCP complementario:

- **Repositorio**: [RSS-MCPserver](https://github.com/GTuritto/RSS-MCPserver)
- **Propósito**: Proporciona contenido RSS dinámico vía protocolo MCP con transporte SSE
- **Características**: Obtención de contenido en tiempo real, caché inteligente, agregación multi-feed
- **Respaldo**: El sistema automáticamente recurre a feeds RSS directos si el servidor MCP no está disponible

La integración MCP demuestra patrones de obtención de contenido de nivel empresarial con mecanismos de respaldo resistentes.

**Configuración Rápida MCP:**
```bash
# Clonar y ejecutar el servidor MCP
git clone https://github.com/GTuritto/RSS-MCPserver
cd RSS-MCPserver
npm install && npm start

# El sistema AI-Parrot detectará y usará automáticamente el servidor MCP
```

### Opciones de Idioma y Voz

El generador de podcasts soporta múltiples idiomas y voces:

#### Idiomas
- `en` - Inglés (por defecto)
- `es` - Español

#### Voces Recomendadas
- **Inglés**: Aria (por defecto), Sarah, Lily
- **Español**: Aria, Sarah, Lily (optimizadas para español)

Para especificar un idioma y voz al ejecutar el script:

```bash
# Inglés con voz por defecto (Aria)
./run_podcast.sh

# Español con voz por defecto
./run_podcast.sh --language es

# Especificar una voz diferente
./run_podcast.sh --language es --voice "Sarah"
```

### Uso del Script

```bash
# Mostrar ayuda
./run_podcast.sh --help

# Generar podcast con opciones personalizadas
./run_podcast.sh --language es --voice "Lily"
NEWS_API_KEY=tu_clave_news_api
OUTPUT_DIR=./PodcastOutput
```

## 🎙️ Uso

### Uso Básico

```bash
poetry run python run_podcast.py
```

### Opciones Avanzadas

```bash
poetry run python run_podcast.py \
    --num-articles 5 \
    --output-dir ./my_podcasts \
    --voice "Aria" \
    --topic "IA y Tecnología"
```

## 📂 Archivos de Salida

La aplicación genera los siguientes archivos en el directorio `PodcastOutput`:

- `AIpodcast_YYYYMMDD_narrative.txt`: El guión del podcast generado
- `AIpodcast_YYYYMMDD.mp3`: El archivo de audio del podcast (si se proporciona la clave API de ElevenLabs)
- `podcast_articles_YYYYMMDD.csv`: Archivo CSV que contiene los artículos procesados

## 🔍 Solución de Problemas

### Problemas Comunes

1. **Permiso Denegado** al ejecutar el script:
   ```bash
   chmod +x run_podcast.sh
   ```

2. **Dependencias Faltantes**:
   El script instalará automáticamente las dependencias requeridas.

3. **Errores de Clave API**:
   Asegúrate de que tus claves API estén correctamente configuradas en el archivo `.env` o variables de entorno.

4. **Falla la Generación de Audio**:
   - Verifica tu clave API de ElevenLabs
   - Asegúrate de tener suficientes créditos en tu cuenta de ElevenLabs
   - Verifica tu conexión a internet

## 🤝 Contribuir

¡Damos la bienvenida a contribuciones! Por favor lee nuestras [Pautas de Contribución](CONTRIBUTING.md) antes de enviar pull requests.

## 📄 Licencia

Este proyecto está licenciado bajo la [Licencia MIT](LICENSE).

## Estructura del Proyecto

```text
AI-parrot/
├── .venv/                      # Entorno virtual
├── pyproject.toml              # Configuración del proyecto
├── README.md                   # Este archivo
├── .env                        # Variables de entorno (claves API)
└── src/                        # Código fuente
    ├── __init__.py             # Inicialización del paquete
    ├── utils/                  # Módulos de utilidades
    │   ├── __init__.py         # Inicialización del paquete
    │   └── env.py              # Utilidades de entorno
    └── podcast_generator/      # Sistema generador de podcasts
        ├── __init__.py         # Inicialización del paquete
        ├── article_fetcher.py  # Utilidades de obtención de artículos
        ├── ai_processor.py     # Módulos de procesamiento IA
        ├── file_utils.py       # Utilidades de manejo de archivos
        ├── langgraph_workflow.py # Flujo de trabajo LangGraph
        └── main.py             # Script principal
```

## Sistema Generador de Podcasts

El sistema generador de podcasts usa LangGraph para orquestar un flujo de trabajo que:

1. Obtiene artículos recientes relacionados con IA de varias fuentes
2. Clasifica artículos por relevancia a temas de IA
3. Resume los artículos más relevantes usando Mistral AI
4. Genera un guión de podcast con transiciones naturales entre historias
5. Convierte el guión a un archivo de audio usando texto a voz
6. Guarda todas las salidas (texto, audio y datos de artículos)

El sistema está construido con extensibilidad en mente, facilitando agregar nuevas fuentes de artículos o personalizar el proceso de generación.
