# Agente de mantenimiento con Ollama

Ejercicio 4 de la guía *7. Inteligencia Artificial Generativa* (José J. Martínez P., septiembre 2026).

> **Enunciado:** Desarrollar un agente de mantenimiento que:
> - Busque un repuesto (código)
> - Consulte en el almacén (código)
> - Genere una orden de trabajo (falla, equipo)
> - Actualice el historial de fallas

Un LLM local (Ollama) decide qué herramienta usar y con qué argumentos. Las herramientas son funciones de Python que consultan y modifican una base de datos SQLite de la planta.

## Componentes del agente

Según la sección 7.8 de la guía, un agente necesita tres cosas:

| Componente | En este proyecto |
|---|---|
| **Modelo de IA** | `qwen3.5:4b`, ejecutado localmente con Ollama |
| **Memoria** | La lista `messages` de la sesión: mensajes del usuario, respuestas del LLM y resultados de herramientas |
| **Herramientas** | 4 funciones Python (`herramientas.py`) sobre una base SQLite (`database.py`) |

La memoria de la conversación es **memoria de sesión**: se pierde al cerrar el programa. La información de la planta (órdenes e historial) sí es persistente, porque se guarda en `planta.db`.

## Flujo

```mermaid
flowchart TD
    U[Usuario: "La Bomba 3 vibra y tiene fuga..."] --> LLM[LLM - Ollama]
    LLM -->|1| T1[buscar_repuesto]
    LLM -->|2| T2[consultar_almacen]
    LLM -->|3| T3[generar_orden_trabajo]
    LLM -->|4| T4[actualizar_historial_fallas]
    T1 --> DB[(SQLite planta.db)]
    T2 --> DB
    T3 --> DB
    T4 --> DB
    DB -. resultado .-> LLM
    LLM --> R[Respuesta final al usuario]
```

El LLM **no inventa** el stock ni las órdenes: decide qué herramienta llamar, Python la ejecuta y el resultado vuelve al LLM. Ese ciclo está en la función `ejecutar_agente()` de `main.py`.

## Estructura

```text
agente-mantenimiento-ollama/
├── main.py                   # agente: ciclo LLM -> herramienta -> resultado
├── herramientas.py           # las 4 herramientas del agente
├── database.py               # base SQLite y datos de ejemplo
├── probar_herramientas.py    # prueba las herramientas sin LLM
├── requirements.txt
└── planta.db                 # se crea sola al ejecutar (no se sube a Git)
```

## Herramientas

| Herramienta | Qué hace |
|---|---|
| `buscar_repuesto(codigo_o_descripcion)` | Busca en el catálogo por código o palabras (ignora tildes y mayúsculas) |
| `consultar_almacen(codigo)` | Devuelve existencias y ubicación |
| `generar_orden_trabajo(equipo, falla)` | Crea la orden con número, fecha y prioridad (ALTA / MEDIA / BAJA según la falla) |
| `actualizar_historial_fallas(equipo, falla, orden)` | Registra la falla asociada a una orden existente |

Detalles de diseño:
- El historial solo se actualiza si la orden existe, así el modelo no puede registrar números inventados.
- Si el modelo repite la llamada, no se duplican órdenes ni registros del historial.
- El límite `MAX_ITERACIONES` evita ciclos infinitos.

## Requisitos

- Python 3.9 o superior
- [Ollama](https://ollama.com/download) instalado y ejecutándose
- Unos 4 GB libres para el modelo

## Instalación

```bash
# 1. Descargar el modelo
ollama pull qwen3.5:4b

# 2. Crear el entorno virtual
python -m venv .venv

# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
# Linux / macOS
source .venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt
```

## Uso

**Paso 1: probar las herramientas sin el LLM** (usa una base temporal):

```bash
python probar_herramientas.py
```

**Paso 2: ejecutar el agente:**

```bash
python main.py
```

Comandos dentro del programa:

| Comando | Acción |
|---|---|
| `/ordenes` | Muestra las órdenes de trabajo guardadas |
| `/historial` | Muestra el historial de fallas |
| `/reiniciar` | Borra la memoria de la conversación |
| `salir` | Termina el programa |

## Ejemplo de uso

Entrada sugerida (incluye el repuesto, para que la ejecución sea reproducible):

```text
La Bomba 3 presenta vibración y fuga. Necesito un sello mecánico para bomba.
Busca el repuesto, consulta el almacén, genera la orden de trabajo y registra la falla.
```

El agente debería llamar, en orden, a `buscar_repuesto`, `consultar_almacen`, `generar_orden_trabajo` y `actualizar_historial_fallas`, y resumir al final el repuesto (`REP-SEL-001`), las existencias (3), la ubicación, el número de orden y la prioridad (ALTA, por la fuga). El número de orden y las fechas cambian en cada ejecución.

Para comprobar la **memoria**, haz después una pregunta como `¿Dónde estaba el repuesto?`: el agente responde sin volver a consultar, porque el contexto sigue en `messages`.

Para comprobar la **persistencia**, escribe `/ordenes` y `/historial`.

> Agrega aquí una captura de pantalla de tu propia ejecución.

## Problemas frecuentes

| Problema | Causa y solución |
|---|---|
| `No se pudo conectar con Ollama` | Ollama no está ejecutándose. Abre la aplicación o corre `ollama serve`. |
| `El modelo ... no está descargado` | Ejecuta `ollama pull qwen3.5:4b`. |
| Error con el parámetro `think` | Actualiza el cliente: `pip install -U ollama`. |
| El modelo responde sin llamar a las herramientas | Es común en modelos pequeños. Prueba una petición más explícita, o un modelo más grande (por ejemplo `qwen3.5:9b`) cambiando `MODELO` en `main.py`. |
| Poca RAM | Prueba `qwen3.5:2b`, aunque puede ser menos consistente con herramientas. |
| El agente se queda repitiendo llamadas | Se detiene solo tras `MAX_ITERACIONES` rondas; reformula la petición. |

## Posibles ampliaciones

- **RAG:** cargar manuales técnicos (bombas, motores, rodamientos) en una base vectorial para que el agente sugiera causas y repuestos a partir de la documentación. Así, RAG aporta el conocimiento técnico, las herramientas las acciones y los datos actuales, y el LLM la coordinación.
- **MCP:** exponer las 4 herramientas como un servidor MCP, para separarlas del agente y reutilizarlas desde otros clientes.
- **Memoria persistente:** guardar la conversación en disco para recuperarla entre sesiones.

## Notas

- El agente usa directamente el cliente oficial de Ollama (sin LangChain) para que el ciclo del agente se vea de forma explícita.
- Las herramientas y la base de datos se probaron con `probar_herramientas.py`. El comportamiento con el modelo depende de tu instalación de Ollama y debe verificarse al ejecutarlo.
