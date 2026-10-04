# Clasificación de prendas con Fashion MNIST y TensorFlow

Ejercicio de la materia **Redes Neuronales** (Capítulo 5, sección 5.9, punto 2).

## Enunciado del ejercicio

> Con base en la librería TensorFlow, descargue el dataset Fashion MNIST. Haga una clasificación de prendas de vestir. Explique cada una de las funciones y las principales instrucciones, saque conclusiones.

## Prompt utilizado

Para desarrollar el codigo se utilizó un asistente de IA con el siguiente prompt:

> "Con base en la librería TensorFlow, descargue el dataset Fashion MNIST. Haga una clasificación de prendas de vestir. Explique cada una de las funciones y las principales instrucciones, saque conclusiones." Dame un notebook para Google Colab, con celdas separadas y comentarios en español, que: - cargue Fashion MNIST, muestre algunas imágenes y normalice los datos - entrene una red neuronal densa (Flatten, capa oculta ReLU, salida softmax de 10 clases) con validation_split - grafique pérdida y exactitud de entrenamiento vs validación - evalúe en el conjunto de prueba, muestre predicciones y una matriz de confusión

## Contenido del repositorio

- `Fashion_MNIST_TensorFlow_Clasificacion.ipynb`: notebook completo (código, explicaciones y conclusiones).
- `README.md`: este archivo.

## Descripción del modelo

Red neuronal densa para clasificar imágenes de 28×28 píxeles en escala de grises en 10 categorías de prendas:

| Capa | Descripción |
|------|-------------|
| `Flatten` | Convierte cada imagen 28×28 en un vector de 784 valores |
| `Dense(128, activation='relu')` | Capa oculta con 128 neuronas |
| `Dense(10, activation='softmax')` | Salida con una probabilidad por cada clase |

- **Optimizador:** Adam (`learning_rate=0.001`)
- **Pérdida:** `sparse_categorical_crossentropy`
- **Métrica:** `accuracy`
- **Entrenamiento:** 10 épocas, `batch_size=128`, `validation_split=0.10`

Clases: Camiseta/top, Pantalón, Suéter, Vestido, Abrigo, Sandalia, Camisa, Zapatilla, Bolso, Botín.

## Cómo ejecutarlo

1. Abrir el notebook en [Google Colab](https://colab.research.google.com).
2. Ir a **Entorno de ejecución > Ejecutar todo**.
3. TensorFlow ya viene instalado en Colab, no hay que instalar nada.

La exactitud y las conclusiones se calculan automáticamente al ejecutar el notebook.

## Código

```python
# ============================================================
# 1. Importación de librerías
# ============================================================
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf

from tensorflow import keras
from tensorflow.keras import layers
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay, classification_report

# Semillas para favorecer resultados reproducibles.
np.random.seed(42)
tf.random.set_seed(42)

print(f"TensorFlow: {tf.__version__}")


# ============================================================
# 2. Carga del dataset Fashion MNIST
# ============================================================
(x_train, y_train), (x_test, y_test) = keras.datasets.fashion_mnist.load_data()

# Nombres de las 10 clases, según la codificación del dataset.
class_names = [
    "Camiseta/top", "Pantalón", "Suéter", "Vestido", "Abrigo",
    "Sandalia", "Camisa", "Zapatilla", "Bolso", "Botín"
]

print("Forma de x_train:", x_train.shape)
print("Forma de y_train:", y_train.shape)
print("Forma de x_test :", x_test.shape)
print("Forma de y_test :", y_test.shape)
print("Número de clases:", len(class_names))


# ============================================================
# 3. Visualización de algunas imágenes
# ============================================================
plt.figure(figsize=(10, 7))

for i in range(12):
    plt.subplot(3, 4, i + 1)
    plt.imshow(x_train[i], cmap="gray")
    plt.title(class_names[y_train[i]])
    plt.axis("off")

plt.suptitle("Ejemplos de Fashion MNIST", fontsize=14)
plt.tight_layout()
plt.show()


# ============================================================
# 4. Normalización de los datos
# ============================================================
# Convertimos los valores de los píxeles de 0-255 a 0-1.
x_train = x_train.astype("float32") / 255.0
x_test = x_test.astype("float32") / 255.0

print("Valor mínimo después de normalizar:", x_train.min())
print("Valor máximo después de normalizar:", x_train.max())


# ============================================================
# 5. Construcción de la red neuronal densa
# ============================================================
model = keras.Sequential([
    # Convierte cada imagen 28x28 en un vector de 784 elementos.
    layers.Flatten(input_shape=(28, 28)),

    # Capa oculta: 128 neuronas y función de activación ReLU.
    layers.Dense(128, activation="relu"),

    # Capa de salida: 10 neuronas, una por cada clase.
    # Softmax produce probabilidades que suman aproximadamente 1.
    layers.Dense(10, activation="softmax")
])

model.summary()


# ============================================================
# 6. Compilación del modelo
# ============================================================
model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=0.001),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

print("Modelo compilado correctamente.")


# ============================================================
# 7. Entrenamiento con validation_split
# ============================================================
history = model.fit(
    x_train,
    y_train,
    epochs=10,
    batch_size=128,
    validation_split=0.10,
    shuffle=True,
    verbose=1
)


# ============================================================
# 8. Gráficas de pérdida y exactitud
# ============================================================
epochs = range(1, len(history.history["loss"]) + 1)

# Gráfica de pérdida.
plt.figure(figsize=(8, 5))
plt.plot(epochs, history.history["loss"], marker="o", label="Entrenamiento")
plt.plot(epochs, history.history["val_loss"], marker="o", label="Validación")
plt.xlabel("Época")
plt.ylabel("Pérdida (loss)")
plt.title("Pérdida: entrenamiento vs. validación")
plt.grid(True, alpha=0.3)
plt.legend()
plt.show()

# Gráfica de exactitud.
plt.figure(figsize=(8, 5))
plt.plot(epochs, history.history["accuracy"], marker="o", label="Entrenamiento")
plt.plot(epochs, history.history["val_accuracy"], marker="o", label="Validación")
plt.xlabel("Época")
plt.ylabel("Exactitud (accuracy)")
plt.title("Exactitud: entrenamiento vs. validación")
plt.grid(True, alpha=0.3)
plt.legend()
plt.show()


# ============================================================
# 9. Evaluación con el conjunto de prueba
# ============================================================
test_loss, test_accuracy = model.evaluate(x_test, y_test, verbose=0)

print(f"Pérdida en prueba: {test_loss:.4f}")
print(f"Exactitud en prueba: {test_accuracy:.4%}")


# ============================================================
# 10. Predicciones sobre imágenes de prueba
# ============================================================
y_prob = model.predict(x_test, verbose=0)

# Convertimos las probabilidades en la clase con mayor probabilidad.
y_pred = np.argmax(y_prob, axis=1)

# Mostramos 12 predicciones.
plt.figure(figsize=(12, 8))

for i in range(12):
    plt.subplot(3, 4, i + 1)
    plt.imshow(x_test[i], cmap="gray")
    real = class_names[y_test[i]]
    pred = class_names[y_pred[i]]
    prob = y_prob[i][y_pred[i]]

    titulo = f"Real: {real}\nPred: {pred} ({prob:.1%})"
    plt.title(titulo, fontsize=9)
    plt.axis("off")

plt.suptitle("Ejemplos de predicciones", fontsize=14)
plt.tight_layout()
plt.show()

print("Primeras 12 clases reales:     ", y_test[:12])
print("Primeras 12 clases predichas: ", y_pred[:12])


# ============================================================
# 11. Matriz de confusión
# ============================================================
cm = confusion_matrix(y_test, y_pred)

disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=class_names)
fig, ax = plt.subplots(figsize=(11, 10))
disp.plot(ax=ax, cmap="Blues", xticks_rotation=45, colorbar=False)
ax.set_title("Matriz de confusión - Fashion MNIST")
ax.set_xlabel("Clase predicha")
ax.set_ylabel("Clase real")
plt.tight_layout()
plt.show()


# ============================================================
# 12. Identificación de las prendas que más se confunden
# ============================================================
pair_confusions = []

for i in range(len(class_names)):
    for j in range(i + 1, len(class_names)):
        total = cm[i, j] + cm[j, i]
        pair_confusions.append((total, i, j))

pair_confusions.sort(reverse=True)

print("Cinco pares de prendas con mayor confusión:")
for rank, (total, i, j) in enumerate(pair_confusions[:5], start=1):
    print(f"{rank}. {class_names[i]} <-> {class_names[j]}: {total} errores")

print("\nReporte de clasificación:")
print(classification_report(y_test, y_pred, target_names=class_names, digits=4))


# ============================================================
# 13. Conclusiones automáticas para el informe
# ============================================================
train_acc_final = history.history["accuracy"][-1]
val_acc_final = history.history["val_accuracy"][-1]
best_val_acc = max(history.history["val_accuracy"])
min_val_loss = min(history.history["val_loss"])
final_val_loss = history.history["val_loss"][-1]
acc_gap = train_acc_final - val_acc_final

# Criterio sencillo para señalar un posible sobreajuste.
possible_overfitting = (acc_gap > 0.03) and (final_val_loss > min_val_loss * 1.05)

top_pair = pair_confusions[0]
top_total, top_i, top_j = top_pair

print("=" * 72)
print("CONCLUSIONES")
print("=" * 72)
print(f"1. Exactitud en el conjunto de prueba: {test_accuracy:.2%}.")
print(
    f"   Durante el entrenamiento, la exactitud final fue {train_acc_final:.2%} "
    f"y la de validación {val_acc_final:.2%}."
)

if possible_overfitting:
    print(
        "2. Se observa evidencia de posible overfitting: la exactitud de entrenamiento "
        "queda apreciablemente por encima de la de validación y la pérdida de validación "
        "aumenta respecto a su mínimo."
    )
else:
    print(
        "2. No se observa un overfitting marcado con el criterio utilizado; las métricas "
        "de entrenamiento y validación permanecen relativamente cercanas."
    )

print(
    f"3. La mayor confusión mutua se presenta entre {class_names[top_i]} y "
    f"{class_names[top_j]}, con {top_total} errores combinados."
)

print(
    "4. La principal causa esperable de confusión es la similitud visual entre algunas "
    "prendas en imágenes pequeñas de 28x28 píxeles, especialmente entre categorías "
    "como camisa, camiseta/top, suéter y abrigo."
)

print(
    "5. Para mejorar el modelo se podría utilizar una red convolucional (CNN), añadir "
    "regularización como Dropout, ajustar el número de neuronas y épocas, usar "
    "EarlyStopping y realizar una búsqueda de hiperparámetros. Una CNN suele aprovechar "
    "mejor la estructura espacial de las imágenes que una red completamente densa."
)
```

## Explicación de las funciones principales

| Instrucción | Qué hace y por qué se usa |
|-------------|---------------------------|
| `load_data()` | Descarga Fashion MNIST y devuelve imágenes y etiquetas de entrenamiento y de prueba (28×28 píxeles, etiquetas de 0 a 9). |
| `x / 255.0` | Normaliza los píxeles de 0-255 a 0-1 para facilitar el entrenamiento. |
| `Flatten` | Convierte cada imagen 28×28 en un vector de 784 valores para poder conectarla con capas `Dense`. No tiene pesos. |
| `Dense` | Capa completamente conectada: cada neurona combina las entradas con pesos y un sesgo. |
| `compile()` | Configura el entrenamiento: optimizador, función de pérdida y métricas. |
| `optimizer` (Adam) | Decide cómo actualizar los pesos después de calcular el error; adapta el tamaño de los pasos. |
| `loss` (`sparse_categorical_crossentropy`) | Mide el error de las predicciones cuando las etiquetas son enteros (0 a 9) y la salida son probabilidades. |
| `fit()` | Entrena la red: propagación hacia adelante, cálculo de la pérdida, gradientes (backpropagation) y actualización de pesos en cada época. |
| `validation_split` | Reserva una parte de los datos de entrenamiento para observar la generalización durante el entrenamiento. |
| `evaluate()` | Calcula pérdida y exactitud sobre el conjunto de prueba, que no se usó para ajustar pesos. |
| `predict()` | Devuelve 10 probabilidades por imagen; `np.argmax` elige la clase más probable. |
