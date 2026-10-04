# K-Nearest Neighbors (KNN)

## 1. Introducción

**K-Nearest Neighbors (K-Vecinos Más Cercanos)** es un algoritmo de aprendizaje supervisado **perezoso** (lazy learning) que se utiliza tanto para **clasificación** como para **regresión**.

El objetivo del algoritmo es simple: **agrupar los elementos similares en el espacio de características**. Esto se debe a que si estan cerca en este espacio, muy probablemente tengan etiquetas similares. Así para predecir la etiqueta de cualquier punto nuevo solo nos basamos en los **K vecinos más cercanos**

---

## 2. ¿Cómo Funciona?

### Para Clasificación:
```
1. Recibir un nuevo punto de consulta → x_new
2. Calcular la distancia entre x_new y TODOS los puntos de entrenamiento
3. Ordenar las distancias de menor a mayor
4. Seleccionar los K puntos con menor distancia (los K vecinos)
5. Votación mayoritaria: la clase que más se repite entre los K vecinos gana
6. Asignar esa clase a x_new
```

### Para Regresión:
```
1-4. Igual que clasificación
5. de los valores objetivo de los K vecinos
6. Asignar ese valor promedio a x_new
```

---

## 3. Métricas de Distancia

La elección de la métrica de distancia **es crítica** y depende del tipo de datos:

| Métrica | Fórmula | Cuándo Usar |
|---------|---------|-------------|
| **Euclidiana** (L2) | `√Σ(xᵢ - yᵢ)²` | Datos numéricos continuos, default estándar |
| **Manhattan** (L1) | `Σ\|xᵢ - yᵢ\|` | Datos con outliers, grid-like (ciudades) |
| **Minkowski** | `(Σ\|xᵢ - yᵢ\|^p)^(1/p)` | Generaliza Euclidiana (p=2) y Manhattan (p=1) |
| **Coseno** | `1 - (A·B)/(\|\|A\|\| \|\|B\|\|)` | Texto, datos dispersos, cuando magnitud no importa |
| **Hamming** | `Σ(xᵢ ≠ yᵢ)` | Datos categóricos/binarios |
| **Mahalanobis** | `√(x-y)ᵀ S⁻¹ (x-y)` | Variables correlacionadas, diferente escala |

> Es importante notar que KNN es **sensible a la escala**. Por esta razón es muy importante estandarizar los features de los datos antes de usar KNN.

---

## 4. El Hiperparámetro K

El hiperparámetro K controla **la cantidad de vecinos a examinar para clasificar un nuevo punto**.

>Regla general: Como punto de partida, generalmente se usa `K = √n`, pero siempre asegurandose que K se **impar**.

### Efecto de K:

| K Pequeño (ej. K=1) | K Grande (ej. K=20) |
|---------------------|---------------------|
| Fronteras de decisión **irregulares/ruidosas** | Fronteras **suaves/generalizadas** |
| **Overfitting** (memoriza ruido) | **Underfitting** (demasiado general) |
| Sensible a outliers | Robusto a outliers |
| Alta varianza, bajo sesgo | Bajo varianza, alto sesgo |

### Cómo Elegir K:
```python
from sklearn.model_selection import cross_val_score
from sklearn.neighbors import KNeighborsClassifier

scores = []
for k in range(1, 31, 2):  # K impares
    knn = KNeighborsClassifier(n_neighbors=k)
    score = cross_val_score(knn, X, y, cv=5, scoring='accuracy').mean()
    scores.append((k, score))

best_k = max(scores, key=lambda x: x[1])[0]
```

---

## 5. Estrategias de Votación

La votación es un paso importante en este algoritmo. La votación hace referencia a el efecto que tienen los vecinos sobre el nuevo punto.

### Votación Simple (Uniforme)
Todos los K vecinos tienen el mismo peso. Este es el más simple, pero tiene un problema importante: un vecino lejano cuenta igual que uno muy cercano.

### Votación Ponderada por Distancia (Recomendada)
```python
# En sklearn:
KNeighborsClassifier(n_neighbors=5, weights='distance')
```
Peso = `1 / distancia` (o `1 / distancia²`). Con esto solucionamos el problema de la votación simple y los vecinos más cercanos influyen más.

### Votación Personalizada
Sin embargo, en caso de que ninguno de estos métodos es posible definir uan función de pesos propia (ej. kernel gaussiano).

---

## 6. Ventajas y Desventajas

### Ventajas
- **Simple de entender e implementar**
- **Sin fase de entrenamiento** (lazy learning) — ideal para datos que cambian frecuentemente
- **Funciona bien con fronteras de decisión no lineales**
- **Interpretable**: "esta predicción se basa en estos K ejemplos"

### Desventajas
- **Lento en predicción** con datasets grandes (O(n) por query)
- **Sensible a features irrelevantes/ruido** → todas las dimensiones cuentan igual
- **Solo para bajas dimensiones** → falla en alta dimensionalidad
- **Desbalance de clases** → clase mayoritaria domina la votación
- **Memoria**: guarda todo el dataset de entrenamiento

---

## 7. Técnicas de Mejora y Variantes

### 7.1 Edición/Condensación del Dataset
Reducir el dataset de entrenamiento manteniendo performance:
- **CNN (Condensed Nearest Neighbor)**: Subconjunto mínimo que clasifica igual
- **ENN (Edited Nearest Neighbor)**: Elimina puntos ruidosos/mal clasificados
- **Tomek Links**: Elimina pares de clases opuestas muy cercanos

### 7.2 Métricas de Distancia Aprendidas
- **LMNN (Large Margin Nearest Neighbor)**: Aprende una transformación lineal que acerca mismos etiquetas y aleja distintas
- **NCA (Neighborhood Component Analysis)**: Optimiza probabilidad de clasificación correcta

### 7.3 KNN Ponderado por Atributos
Asignar pesos a cada feature según su relevancia (ReliefF, Mutual Information, pesos de Random Forest).

### 7.4 Aproximaciones para Escalar
- **ANN (Approximate Nearest Neighbors)**: HNSW, FAISS, Annoy. Más rápido, pero menos preciso.
- **LSH (Locality Sensitive Hashing)**: Hashing que preserva vecindad

---

## 8. Casos de Uso Típicos

| Dominio | Aplicación |
|---------|------------|
| **Recomendación** | "Usuarios similares a ti compraron..." (User-based CF) |
| **NLP** | Clasificación de documentos con TF-IDF + Coseno |
| **Detección de Anomalías** | Puntos con pocos vecinos cercanos = outliers |
| **Sistemas de Recuperación de Información** | Búsqueda por similitud |

---

## 9. Implementación en Python (scikit-learn)

```python
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, mean_squared_error

pipe = Pipeline([
    ('scaler', StandardScaler()),
    ('knn', KNeighborsClassifier())
])

# Búsqueda de hiperparámetros
param_grid = {
    'knn__n_neighbors': [3, 5, 7, 9, 11, 15, 21],
    'knn__weights': ['uniform', 'distance'],
    'knn__metric': ['euclidean', 'manhattan', 'minkowski'],
    'knn__p': [1, 2]  # solo para minkowski
}

grid = GridSearchCV(pipe, param_grid, cv=5, scoring='accuracy', n_jobs=-1)
grid.fit(X_train, y_train)

print(f"Mejor K: {grid.best_params_['knn__n_neighbors']}")
print(f"Mejor peso: {grid.best_params_['knn__weights']}")
print(f"Mejor métrica: {grid.best_params_['knn__metric']}")

# Evaluación
y_pred = grid.predict(X_test)
print(classification_report(y_test, y_pred))
```
