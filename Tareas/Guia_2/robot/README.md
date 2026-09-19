# Robot Evitador de Obstáculos

Simulación en pygame de un robot con tracción diferencial (2 ruedas) y 3 sensores de proximidad que evita obstáculos usando un control tipo Braitenberg.

El espacio es un recinto cerrado: el robot detecta las paredes con sus sensores y nunca sale de la arena. Dentro hay 4 bloques de tamaño/posición aleatorios.

## Setup

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Ejecutar

```bash
.venv/bin/python robot.py
```

## Controles

| Tecla | Acción            |
|-------|-------------------|
| R     | Regenerar obstáculos |
| P     | Pausa / Play      |
| S     | Mostrar/ocultar sensores |
