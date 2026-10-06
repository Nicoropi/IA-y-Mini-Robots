# Ejercicio 3 — Chatbot

Chatbot con interfaz web, en un solo archivo de Python y **sin dependencias**
(usa únicamente la librería estándar). Las respuestas las genera un modelo de
**Ollama** corriendo en la máquina local: gratis, sin API key y sin enviar nada
a internet.

```
Ejercicio03/
├── chatbot.py   # toda la aplicación (servidor + interfaz + llamada a Ollama)
└── README.md
```

## 1. Instalar Ollama (una sola vez)

Descarga desde <https://ollama.com/download> e instálalo. En Linux:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

## 2. Descargar un modelo

```bash
ollama pull llama3.2:3b
```

Modelos alternativos si tienes poca memoria RAM: `gemma2:2b` o `qwen2.5:3b`.
El bot detecta solo qué modelos tienes y te avisa en la interfaz cuál va a usar.

## 3. Ejecutar

```bash
python chatbot.py
```

Se abre el navegador en `http://localhost:8765`. Para detenerlo: `Ctrl+C`.

La primera vez, si Ollama no está corriendo, el bot lo detecta y muestra el
error con la instrucción exacta (`ollama serve`) en lugar de fallar en silencio.

## Cómo funciona

El script levanta un servidor HTTP local con la librería estándar y hace tres
cosas:

| Ruta | Método | Qué hace |
|---|---|---|
| `/` | GET | Devuelve la interfaz de chat (HTML + CSS + JS en un solo archivo) |
| `/api/info` | GET | Modelo en uso y avisos de configuración |
| `/api/chat` | POST | Recibe el historial, llama a Ollama y devuelve la respuesta |

El flujo de una pregunta es:

1. El navegador envía `messages` (todo el historial de la conversación) a `/api/chat`.
2. El servidor le antepone el mensaje de sistema y hace `POST` a Ollama
   (`http://localhost:11434/api/chat` con `stream: false`).
3. Se devuelve `message.content` y el navegador lo pinta como burbuja.

El historial vive en el navegador, así que **"Limpiar"** lo borra sin tocar el
servidor. El botón `Enter` envía y `Shift+Enter` hace salto de línea.

## Modo RAG

Este ejercicio es solo el chatbot, sin recuperación de documentos. El RAG
—convertir los PDFs de `Docs_Clase/` en texto, trocearlos, generar embeddings
y buscar los trozos relevantes antes de responder— queda como siguiente paso.
La estructura ya está preparada: basta interceptar el punto 2 e inyectar el
contexto recuperado antes de la llamada a Ollama.

## Problemas frecuentes

**"No se pudo conectar con Ollama"** → Ollama no está corriendo: `ollama serve`.

**El bot responde en inglés** → el prompt de sistema está en
`PROMPT_SISTEMA` (en `chatbot.py`); se puede ajustar ahí.

**Quiero otro modelo** → cambia `MODELO_PREDETERMINADO` (en `chatbot.py`), o
simplemente ten un modelo distinto descargado y el bot lo usa automáticamente.

**Puerto 8765 ocupado** → cambia `PUERTO` (en `chatbot.py`).
