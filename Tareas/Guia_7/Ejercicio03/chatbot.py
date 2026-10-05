"""
Ejercicio 3 - Chatbot basico (Guia 7: IA Generativa).

Interfaz de chat web servida por la libreria estandar de Python y respuestas
generadas por un modelo de Ollama corriendo en la maquina local.

Solo usa la libreria estandar: no requiere instalar nada mas.

Uso:
    python chatbot.py
"""

import json
import sys
import threading
import urllib.error
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# --- Config ---
OLLAMA_URL = "http://localhost:11434"
MODELO_PREDETERMINADO = "llama3.2:3b"
PUERTO = 8765
TEMPERATURA = 0.7
TIEMPO_LIMITE = 300

PROMPT_SISTEMA = (
    "Eres un asistente virtual de la materia IA y Mini-Robots de la Universidad "
    "Nacional de Colombia. Respondes siempre en espanol, de forma breve y clara, "
    "con un tono amable y directo. Explicas los conceptos tecnicos con ejemplos "
    "sencillos cuando ayude. Si no sabes algo o no estas seguro, lo dices con "
    "franqueza: nunca inventas datos, citas ni bibliografia."
)

MODELO = MODELO_PREDETERMINADO
AVISOS = []


# --- LLM ---
def listar_modelos():
    try:
        with urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=5) as r:
            datos = json.load(r)
    except (urllib.error.URLError, OSError, ValueError):
        return []
    return [m.get("name", "") for m in datos.get("models", []) if m.get("name")]


def resolver_modelo(preferido):
    disponibles = listar_modelos()
    if not disponibles:
        return preferido, [
            f"No se pudo contactar a Ollama en {OLLAMA_URL}. "
            f"Abre una terminal y ejecuta 'ollama serve'."
        ]
    for nombre in disponibles:
        if nombre.split(":")[0] == preferido.split(":")[0]:
            return nombre, []
    return disponibles[0], [
        f"El modelo '{preferido}' no esta descargado, se usara '{disponibles[0]}'."
    ]


def preguntar(mensajes, modelo):
    cuerpo = json.dumps(
        {
            "model": modelo,
            "messages": mensajes,
            "stream": False,
            "options": {"temperature": TEMPERATURA},
        }
    ).encode()
    peticion = urllib.request.Request(
        f"{OLLAMA_URL}/api/chat",
        data=cuerpo,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(peticion, timeout=TIEMPO_LIMITE) as r:
            datos = json.load(r)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Ollama respondio {e.code}: {e.read().decode('utf-8', 'replace')}") from e
    except (urllib.error.URLError, OSError) as e:
        raise RuntimeError(
            f"No se pudo conectar con Ollama ({OLLAMA_URL}). "
            f"Verifica que este corriendo con 'ollama serve'. Detalle: {e}"
        ) from e
    return datos.get("message", {}).get("content", "").strip()


# --- Interfaz ---
HTML = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Chatbot - IA y Mini-Robots</title>
<style>
  * { box-sizing: border-box; }
  body {
    margin: 0; font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
    background: #f4f5f7; color: #1f2328; height: 100vh;
    display: flex; flex-direction: column;
  }
  header {
    padding: 12px 18px; background: #fff; border-bottom: 1px solid #d8dbe0;
    display: flex; align-items: center; gap: 12px;
  }
  header h1 { font-size: 16px; margin: 0; font-weight: 600; }
  #modelo { font-size: 12px; color: #6a737d; margin-left: auto; }
  #chat {
    flex: 1; overflow-y: auto; padding: 18px;
    display: flex; flex-direction: column; gap: 10px;
  }
  .msg {
    max-width: 78%; padding: 10px 14px; border-radius: 14px;
    white-space: pre-wrap; word-wrap: break-word; line-height: 1.45; font-size: 14px;
  }
  .user { align-self: flex-end; background: #2f6feb; color: #fff; border-bottom-right-radius: 4px; }
  .bot { align-self: flex-start; background: #fff; border: 1px solid #d8dbe0; border-bottom-left-radius: 4px; }
  .error { align-self: center; background: #ffe9e9; color: #a4232b; border: 1px solid #f3b6b6; font-size: 13px; }
  footer { padding: 12px 18px; background: #fff; border-top: 1px solid #d8dbe0; }
  .fila { display: flex; gap: 10px; }
  textarea {
    flex: 1; resize: none; height: 46px; padding: 12px;
    border: 1px solid #d8dbe0; border-radius: 10px; font: inherit; font-size: 14px;
  }
  textarea:focus { outline: 2px solid #2f6feb; outline-offset: -1px; }
  button {
    padding: 0 18px; border: 0; border-radius: 10px; background: #2f6feb;
    color: #fff; font: inherit; font-weight: 600; cursor: pointer;
  }
  button:disabled { opacity: .5; cursor: default; }
  button.secundario { background: #eef0f3; color: #1f2328; padding: 8px 14px; font-weight: 500; }
  .pie { margin-top: 8px; display: flex; justify-content: space-between; align-items: center; }
  .pista { font-size: 12px; color: #6a737d; }
</style>
</head>
<body>
<header>
  <h1>Chatbot &middot; IA y Mini-Robots</h1>
  <span id="modelo">cargando...</span>
</header>

<div id="chat"></div>

<footer>
  <div class="fila">
    <textarea id="entrada" placeholder="Escribe tu pregunta..."></textarea>
    <button id="enviar">Enviar</button>
  </div>
  <div class="pie">
    <span class="pista">Enter envia &middot; Shift+Enter salta de linea</span>
    <button id="limpiar" class="secundario">Limpiar</button>
  </div>
</footer>

<script>
const historial = [];
const chat = document.getElementById('chat');
const entrada = document.getElementById('entrada');
const enviar = document.getElementById('enviar');

function burbuja(texto, rol) {
  const div = document.createElement('div');
  div.className = 'msg ' + rol;
  div.textContent = texto;
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
  return div;
}

async function mandar() {
  const texto = entrada.value.trim();
  if (!texto || entrada.disabled) return;

  historial.push({ role: 'user', content: texto });
  burbuja(texto, 'user');
  entrada.value = '';
  entrada.disabled = enviar.disabled = true;

  const pensando = burbuja('...', 'bot');
  try {
    const r = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages: historial })
    });
    const datos = await r.json();
    pensando.remove();
    if (!r.ok) {
      burbuja(datos.error || 'Ocurrio un error inesperado.', 'error');
      return;
    }
    historial.push({ role: 'assistant', content: datos.respuesta });
    burbuja(datos.respuesta, 'bot');
  } catch (e) {
    pensando.remove();
    burbuja('No se pudo conectar con el servidor: ' + e.message, 'error');
  } finally {
    entrada.disabled = enviar.disabled = false;
    entrada.focus();
  }
}

document.getElementById('limpiar').addEventListener('click', () => {
  historial.length = 0;
  chat.replaceChildren();
  burbuja('Conversacion reiniciada.', 'bot');
  entrada.focus();
});

enviar.addEventListener('click', mandar);
entrada.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    mandar();
  }
});

fetch('/api/info')
  .then((r) => r.json())
  .then((d) => {
    document.getElementById('modelo').textContent = 'modelo: ' + d.modelo;
    burbuja(
      'Hola! Soy un asistente de la materia IA y Mini-Robots. Respondiendo con el modelo "' +
      d.modelo + '" que se ejecuta en tu maquina. Escribe tu pregunta.',
      'bot'
    );
    for (const aviso of d.avisos) burbuja(aviso, 'error');
  })
  .catch(() => burbuja('No se pudo obtener la configuracion del servidor.', 'error'));
</script>
</body>
</html>
"""


# --- Servidor ---
class Manejador(BaseHTTPRequestHandler):
    server_version = "Chatbot/1.0"

    def responder(self, cuerpo, codigo=200, tipo="application/json"):
        if tipo == "application/json":
            cuerpo = json.dumps(cuerpo).encode()
        self.send_response(codigo)
        self.send_header("Content-Type", f"{tipo}; charset=utf-8")
        self.send_header("Content-Length", str(len(cuerpo)))
        self.end_headers()
        self.wfile.write(cuerpo)

    def do_GET(self):
        ruta = self.path.split("?")[0].rstrip("/") or "/"
        if ruta == "/":
            self.responder(HTML.encode(), tipo="text/html")
        elif ruta == "/api/info":
            self.responder({"modelo": MODELO, "avisos": AVISOS})
        else:
            self.responder({"error": "Ruta no encontrada."}, codigo=404)

    def do_POST(self):
        if self.path.split("?")[0].rstrip("/") != "/api/chat":
            self.responder({"error": "Ruta no encontrada."}, codigo=404)
            return
        try:
            largo = int(self.headers.get("Content-Length", 0))
            mensajes = json.loads(self.rfile.read(largo) or b"{}").get("messages")
            if not isinstance(mensajes, list) or not mensajes:
                raise ValueError("El campo 'messages' debe ser una lista no vacia.")
            completo = [{"role": "system", "content": PROMPT_SISTEMA}] + mensajes
            self.responder({"respuesta": preguntar(completo, MODELO)})
        except Exception as e:
            self.responder({"error": str(e)}, codigo=500)

    def log_message(self, formato, *args):
        pass


def main():
    global MODELO, AVISOS
    MODELO, AVISOS = resolver_modelo(MODELO_PREDETERMINADO)

    print("Chatbot - IA y Mini-Robots (Ejercicio 3)")
    print(f"  Modelo:  {MODELO}")
    for aviso in AVISOS:
        print(f"  Aviso:   {aviso}")
    if not AVISOS and not listar_modelos():
        print(f"  Sugerencia: ejecuta 'ollama pull {MODELO_PREDETERMINADO}'")
    print(f"  Interfaz: http://localhost:{PUERTO}\n")
    print("  Ctrl+C para salir.\n")

    servidor = ThreadingHTTPServer(("127.0.0.1", PUERTO), Manejador)
    threading.Timer(0.5, lambda: webbrowser.open(f"http://localhost:{PUERTO}")).start()
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nChao.")
    finally:
        servidor.server_close()
        sys.exit(0)


if __name__ == "__main__":
    main()