## Ejercicio 1

Enunciado:

Observe sus comportamientos en la casa, en la universidad y en el medio de transporte que utiliza. Encuentre para cada uno de estos escenarios sus reglas básicas.

### Casa:

| Estado           | Simbolo |
| ---------------- | ------- |
| Realizar Deberes | 0       |
| Ocio             | 1       |
| Dormir           | 2       |

| Pregunta (sensor) | Simbolo |
| ----------------- | --------|
| Es de dia         | A       |
| Tengo Energia     | B       |
| Tengo deberes     | C       |

Con estos estados y sensores se define la siguientes reglas

| A | B | C | Estado |
|---|---|---|--------|
| 0 | 0 | 0 | 2      |
| 0 | 0 | 1 | 2      |
| 0 | 1 | 0 | 1      |
| 0 | 1 | 1 | 0      |
| 1 | 0 | 0 | 1      |
| 1 | 0 | 1 | 0      |
| 1 | 1 | 0 | 1      |
| 1 | 1 | 1 | 0      |

### Universidad:

| Estado           | Simbolo |
| ---------------- | ------- |
| Ir a Clase       | 0       |
| Estudiar         | 1       |
| Descansar        | 2       |

| Pregunta (sensor) | Simbolo |
| ----------------- | --------|
| Hay clase ahora   | A       |
| Tengo pereza      | B       |
| Hay parcial       | C       |

Con estos estados y sensores se define la siguientes reglas

| A | B | C | Estado |
|---|---|---|--------|
| 0 | 0 | 0 | 2      |
| 0 | 0 | 1 | 1      |
| 0 | 1 | 0 | 2      |
| 0 | 1 | 1 | 2      |
| 1 | 0 | 0 | 0      |
| 1 | 0 | 1 | 0      |
| 1 | 1 | 0 | 0      |
| 1 | 1 | 1 | 0      |


### Transporte:

| Estado  | Simbolo |
| ------- | ------- |
| Subirme | 0       |
| Bajarme | 1       |
| Esperar | 2       |

| Pregunta (sensor) | Simbolo |
| ----------------- | --------|
| Tengo que bajarme del bus? | A       |
| Tengo que subirme al bus?  | B       |
| Ha llegado el bus?         | C       |

Con estos estados y sensores se define la siguientes reglas

| A | B | C | Estado |
|---|---|---|--------|
| 0 | 0 | 0 | 2      |
| 0 | 0 | 1 | 2      |
| 0 | 1 | 0 | 2      |
| 0 | 1 | 1 | 0      |
| 1 | 0 | 0 | 2      |
| 1 | 0 | 1 | 1      |
