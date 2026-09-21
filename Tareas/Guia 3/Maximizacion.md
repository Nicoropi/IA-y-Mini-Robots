# Ejercicio 1 — Algoritmo Genético: Maximizar f(x) = x·sen(10πx) + 1

Implementación de un **Algoritmo Genético Simple (AGS)** en Google Sheets / Excel,
para resolver el problema de optimización:

$$\text{Maximizar } f(x) = x \cdot \text{sen}(10\pi x) + 1, \quad x \in [0,1]$$

Esta función tiene múltiples máximos locales, lo que la hace un buen caso de
prueba clásico para algoritmos de optimización bioinspirados.

## Contenido del repositorio

| Archivo | Descripción |
|---|---|
| `Ejercicio1_AG_Maximizar_fx.xlsx` | Hoja de cálculo con el AG implementado con fórmulas |

## ¿Cómo funciona el Algoritmo Genético?

Un Algoritmo Genético es una técnica de optimización inspirada en la selección
natural: se mantiene una **población** de soluciones candidatas (cromosomas),
que evoluciona generación tras generación aplicando tres operadores:

1. **Selección** — los individuos más aptos tienen mayor probabilidad de
   convertirse en padres de la siguiente generación (selección por ruleta).
2. **Cruce** — se combinan partes de dos cromosomas padres para producir dos
   cromosomas hijos.
3. **Mutación** — con una probabilidad baja, se altera aleatoriamente algún
   gen del cromosoma, para mantener diversidad genética y evitar quedar
   atrapado en óptimos locales.

## Diseño de este AG (siguiendo los 6 pasos clásicos de diseño)

### 1. Definición del problema
Encontrar el valor de `x` en el intervalo `[0,1]` que maximiza
`f(x) = x·sen(10πx) + 1`.

### 2. Representación del cromosoma
Cada individuo es una cadena binaria de **9 bits**. Esos bits se interpretan
como un número decimal (0 a 511), que luego se transforma al rango real
`[0,1]` mediante:

```
x = Dec / 511
```

Con 9 bits se logra una resolución de aproximadamente 0.00196 en el dominio,
suficiente precisión para este problema.

### 3. Función de aptitud
```
Aptitud = f(x) = x·sen(10πx) + 1
```
Se usa directamente el valor de la función (sin transformación adicional),
porque `f(x) ≥ 0` en todo el dominio `[0,1]` — no hace falta ajustar el signo
como sí sería necesario si se buscara *minimizar* una distancia (como en el
ejemplo clásico de búsqueda de raíces).

### 4. Operadores genéticos
- **Selección**: por ruleta — la probabilidad de que un individuo sea
  seleccionado como padre es proporcional a su aptitud respecto al total
  de la población.
- **Cruce**: de un punto — se elige una posición al azar dentro del
  cromosoma y se intercambian los bits posteriores a ese punto entre
  la pareja de padres.
- **Mutación**: por bit — cada bit tiene una probabilidad fija (`pm = 5%`)
  de invertirse (0→1 o 1→0).

### 5. Criterio de parada
Para esta implementación en hoja de cálculo se demuestra el mecanismo con
una generación completa (Generación 1 → Generación 2), comparando la
aptitud total y el mejor individuo de cada una. El proceso puede repetirse
manualmente cuantas veces se desee, copiando los bits de la Mutación sobre
la Población inicial y recalculando.

### 6. Parámetros usados
| Parámetro | Valor |
|---|---|
| `l` (bits por cromosoma) | 9 |
| `K` (individuos en la población) | 8 |
| `pm` (probabilidad de mutación) | 5% |

## Resultado

Tras una generación de evolución, la aptitud total de la población mejoró
de forma medible:

| | Aptitud total |
|---|---|
| Generación 1 | 8.99 |
| Generación 2 | **11.30** |

Esto representa una mejora de aproximadamente **25.6%** en una sola
generación, gracias a que la selección por ruleta favoreció a los
individuos más aptos, y el cruce + mutación permitieron explorar el
espacio de soluciones. El máximo teórico de `f(x)` en `[0,1]` es
aproximadamente `f(x) ≈ 1.85` en `x ≈ 0.85`; el mejor individuo de la
Generación 2 alcanzó una aptitud de 1.85, muy cerca de ese óptimo.

## Referencias

- Holland, J. (1975). *Adaptation in Natural and Artificial Systems*.
- Goldberg, D. (1989). *Genetic Algorithms in Search, Optimization and
  Machine Learning*. Addison Wesley.
