# Máquinas de Vectores de Soporte (SVM)

Estudio del algoritmo SVM, código documentado en español y una aplicación de reconocimiento de dígitos escritos a mano.


## 1. Fundamentos teóricos

### 1.1 El problema que resuelve una SVM

Se tienen $m$ ejemplos $\mathbf{x}^{(i)}$ (vectores de $n$ características) con una etiqueta de clase. Para dos clases, es cómodo codificar la etiqueta como $t^{(i)} \in \{-1, +1\}$. La SVM busca un **hiperplano** (en 2 dimensiones, una recta) que separe las dos clases.

### 1.2 Función de decisión

$$
h(\mathbf{x}) = \mathbf{w}^T \mathbf{x} + b
$$

- $\mathbf{w}$ es el vector de pesos y $b$ es el sesgo. Es la misma neurona $z = \sum_j w_j x_j + b$ de la sección 5.2 de la guía.
- Se predice la clase $+1$ si $h(\mathbf{x}) \ge 0$ y la clase $-1$ si $h(\mathbf{x}) < 0$.
- La **frontera de decisión** es el conjunto de puntos donde $h(\mathbf{x}) = 0$.

### 1.3 El margen

La distancia de un punto $\mathbf{x}$ a la frontera es $|h(\mathbf{x})| / \|\mathbf{w}\|$. Se imponen dos rectas paralelas a la frontera, donde $h(\mathbf{x}) = +1$ y $h(\mathbf{x}) = -1$. Entre ellas queda una "calle" cuyo ancho es

$$
\text{ancho de la calle} = \frac{2}{\|\mathbf{w}\|}
$$

**Idea clave:** un vector $\mathbf{w}$ pequeño produce una calle ancha. Entre todas las rectas que separan los datos, la SVM elige la de calle más ancha, porque es la que mejor generaliza ante datos nuevos. Los puntos que quedan sobre los bordes de la calle son los **vectores de soporte**: solo ellos determinan la solución, y borrar los demás puntos no cambia nada.

### 1.4 Margen duro (*hard margin*)

Si los datos son separables con una recta, se resuelve:

$$
\min_{\mathbf{w}, b} \ \tfrac{1}{2}\,\mathbf{w}^T\mathbf{w}
\quad \text{sujeto a} \quad
t^{(i)}\left(\mathbf{w}^T\mathbf{x}^{(i)} + b\right) \ge 1 \quad \text{para todo } i
$$

Minimizar $\tfrac{1}{2}\|\mathbf{w}\|^2$ equivale a maximizar el ancho de la calle. La restricción obliga a que todos los puntos queden en su lado correcto y fuera de la calle. Tiene dos problemas: solo existe solución si los datos son perfectamente separables, y es muy sensible a los *outliers* (valores atípicos).

### 1.5 Margen blando (*soft margin*) y el parámetro $C$

Se permite que algunos puntos entren en la calle o queden mal clasificados, con una variable de holgura $\zeta^{(i)} \ge 0$ por ejemplo:

$$
\min_{\mathbf{w}, b, \boldsymbol{\zeta}} \ \tfrac{1}{2}\,\mathbf{w}^T\mathbf{w} + C \sum_{i=1}^{m} \zeta^{(i)}
\quad \text{sujeto a} \quad
t^{(i)}\left(\mathbf{w}^T\mathbf{x}^{(i)} + b\right) \ge 1 - \zeta^{(i)}
$$

El hiperparámetro $C$ equilibra dos objetivos que compiten:

| $C$ | Margen | Violaciones permitidas | Riesgo |
|-----|--------|------------------------|--------|
| **Grande** | Calle estrecha | Pocas | Sobreajuste (*overfitting*) |
| **Pequeño** | Calle ancha | Muchas | Subajuste (*underfitting*) |

Se observa que $C$ actúa como el inverso de la regularización: a menor $C$, más regularización.

### 1.6 Pérdida *hinge*: la SVM como minimización de una función de costo

El problema anterior es equivalente a minimizar, sin restricciones:

$$
J(\mathbf{w}, b) = \tfrac{1}{2}\,\mathbf{w}^T\mathbf{w} + C \sum_{i=1}^{m} \max\left(0,\ 1 - t^{(i)}\left(\mathbf{w}^T\mathbf{x}^{(i)} + b\right)\right)
$$

El término $\max(0, 1 - t)$ es la **pérdida hinge**. Vale 0 si el punto está bien clasificado y fuera de la calle ($t\,h(\mathbf{x}) \ge 1$) y crece linealmente cuanto más adentro o más equivocado esté. Esto conecta con la guía: igual que en una red neuronal, hay una función de pérdida $E$ y se puede minimizar con descenso del gradiente (se hace en la parte 8).

### 1.7 El truco del kernel (formulación dual)

Cuando los datos no se separan con una recta, se pueden llevar a un espacio de más dimensiones donde sí se separen. Calcular esa transformación explícitamente sería muy costoso. La formulación **dual** del problema muestra que la solución solo necesita productos entre pares de puntos, y se pueden reemplazar por una función **kernel** $K(\mathbf{a}, \mathbf{b})$ que calcula directamente el producto en el espacio ampliado, sin construirlo:

$$
h(\mathbf{x}) = \sum_{i=1}^{m} \alpha^{(i)}\, t^{(i)}\, K\left(\mathbf{x}^{(i)}, \mathbf{x}\right) + b
\qquad (0 \le \alpha^{(i)} \le C)
$$

Solo los vectores de soporte tienen $\alpha^{(i)} > 0$, por eso la predicción depende únicamente de ellos.

### 1.8 Más de dos clases

La SVM es binaria por naturaleza. Para $k$ clases, scikit-learn usa:

- **Uno contra uno** (`SVC`): entrena un clasificador por cada par de clases, o sea $k(k-1)/2$ en total. Para los 10 dígitos son 45 clasificadores, y la clase final sale por votación.
- **Uno contra el resto** (`LinearSVC`): entrena un clasificador por clase, $k$ en total.

### 1.9 Regresión con SVM (SVR)

En regresión la idea se invierte: se busca una línea que contenga a **la mayor cantidad posible de puntos dentro de un tubo** de ancho $\varepsilon$ (`epsilon`). Los errores menores que $\varepsilon$ no cuentan:

$$
\text{pérdida}_\varepsilon = \max\left(0,\ |y - \hat{y}| - \varepsilon\right)
$$

### 1.10 Consideraciones prácticas

- **Las variables deben estar en escalas comparables:** la SVM mide distancias, y una variable con valores grandes domina a las demás (parte 4). Se logra con `StandardScaler` o, si todas las variables comparten unidades (como los píxeles de una imagen), dividiendo entre el valor máximo (parte 9).
- **Costo de entrenamiento de `SVC` con kernel:** crece entre $O(m^2)$ y $O(m^3)$ con el número de ejemplos $m$. Sirve muy bien con conjuntos pequeños y medianos, y se vuelve lenta con cientos de miles de ejemplos. `LinearSVC` crece casi linealmente.
- **`SVC` no entrega probabilidades de forma nativa** (entrega puntajes de decisión). Con `probability=True` las estima, con un entrenamiento más lento.
- **Hiperparámetros a ajustar:** `kernel`, `C` y `gamma` (y `degree`, `coef0` en el polinomial). Se ajustan con validación cruzada (parte 9).

---

## 2. Código

### 2. Preparación del entorno

Se importan las librerías base, se fija la semilla aleatoria para que los resultados se puedan repetir y se define `save_fig`, que guarda las figuras en la carpeta `images/`.

En Google Colab no hay que instalar nada: NumPy, Matplotlib y scikit-learn ya vienen incluidos.

```python
# ----- Librerías base -----
import os
import time
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

# Semilla para que los resultados sean reproducibles entre ejecuciones.
np.random.seed(42)

# Tamaños de letra de las gráficas.
plt.rcParams["axes.labelsize"] = 14
plt.rcParams["xtick.labelsize"] = 12
plt.rcParams["ytick.labelsize"] = 12

# ----- Carpeta donde se guardan las figuras -----
IMAGES_DIR = "images"
os.makedirs(IMAGES_DIR, exist_ok=True)


def save_fig(fig_id, tight_layout=True):
    """Guarda la figura activa de Matplotlib en images/<fig_id>.png.

    Parámetros
    ----------
    fig_id : str
        Nombre del archivo, sin extensión.
    tight_layout : bool
        Si es True, ajusta los márgenes para que nada quede cortado.

    Nota: el código original guardaba siempre en un archivo llamado "images",
    por lo que cada figura sobrescribía a la anterior.
    """
    ruta = os.path.join(IMAGES_DIR, fig_id + ".png")
    if tight_layout:
        plt.tight_layout()
    plt.savefig(ruta, format="png", dpi=150)
    print("Figura guardada:", ruta)


print("NumPy:", np.__version__)
print("Matplotlib:", matplotlib.__version__)
```

### 3. Clasificación de margen grande

Se usa el conjunto de datos **Iris** (150 flores de 3 especies). Se toman solo dos características, el largo y el ancho del pétalo, y solo dos especies, *setosa* y *versicolor*, que sí se pueden separar con una recta.

Se entrena una SVM lineal con un $C$ enorme (`1e10`), que en la práctica equivale al **margen duro** de la sección 1.4: no se tolera ninguna violación.

Después de entrenar, `coef_` guarda $\mathbf{w}$, `intercept_` guarda $b$ y `support_vectors_` guarda los vectores de soporte. Con ellos se calcula el ancho de la calle $2/\|\mathbf{w}\|$.

```python
from sklearn import datasets
from sklearn.svm import SVC, LinearSVC, SVR, LinearSVR
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

# ----- Datos: Iris, largo y ancho del pétalo -----
iris = datasets.load_iris()
X = iris["data"][:, (2, 3)]      # columna 2 = largo del pétalo, columna 3 = ancho del pétalo
y = iris["target"]               # 0 = setosa, 1 = versicolor, 2 = virginica

# Nos quedamos solo con setosa y versicolor (dos clases, separables con una recta).
setosa_o_versicolor = (y == 0) | (y == 1)
X = X[setosa_o_versicolor]
y = y[setosa_o_versicolor]

# ----- Modelo: SVM lineal de margen duro (C muy grande) -----
svm_clf = SVC(kernel="linear", C=1e10)
svm_clf.fit(X, y)

# ----- Qué aprendió el modelo -----
w = svm_clf.coef_[0]
b = svm_clf.intercept_[0]
print("Pesos w                    :", w)
print("Sesgo b                    :", round(float(b), 4))
print("Número de vectores soporte :", len(svm_clf.support_vectors_))
print("Ancho de la calle 2/||w||  :", round(2 / np.linalg.norm(w), 4))
```

#### Función para graficar la frontera de decisión

En el plano, la frontera $h(\mathbf{x}) = 0$ es la recta $w_0 x_0 + w_1 x_1 + b = 0$. Despejando $x_1$:

$$
x_1 = -\frac{w_0}{w_1}\,x_0 - \frac{b}{w_1}
$$

Los bordes de la calle ($h = \pm 1$) son esa misma recta desplazada $\pm 1/w_1$ en vertical.

```python
def plot_svc_decision_boundary(clf, xmin, xmax, support_vectors=None):
    """Dibuja la frontera de decisión y los bordes de la calle de una SVM lineal en 2D.

    Parámetros
    ----------
    clf : modelo lineal ya entrenado con atributos coef_ e intercept_
        (SVC con kernel lineal, LinearSVC, SGDClassifier, MyLinearSVC...).
    xmin, xmax : float
        Rango del eje horizontal donde se dibujan las rectas.
    support_vectors : array (k, 2), opcional
        Puntos a resaltar como vectores de soporte. Si no se da, se usa
        clf.support_vectors_ (solo existe en SVC).

    Líneas: continua = frontera (h = 0), punteadas = bordes de la calle (h = +-1).
    """
    w = clf.coef_[0]
    b = clf.intercept_[0]

    # En la frontera: w0*x0 + w1*x1 + b = 0  =>  x1 = -(w0/w1)*x0 - b/w1
    x0 = np.linspace(xmin, xmax, 200)
    frontera = -w[0] / w[1] * x0 - b / w[1]

    # Los bordes de la calle (h = +-1) quedan a 1/|w1| por encima y por debajo.
    margen = 1 / abs(w[1])
    borde_superior = frontera + margen
    borde_inferior = frontera - margen

    if support_vectors is None:
        support_vectors = clf.support_vectors_

    plt.scatter(support_vectors[:, 0], support_vectors[:, 1],
                s=180, facecolors="#FFAAAA")           # vectores de soporte resaltados
    plt.plot(x0, frontera, "k-", linewidth=2)
    plt.plot(x0, borde_superior, "k--", linewidth=2)
    plt.plot(x0, borde_inferior, "k--", linewidth=2)
```

```python
# ----- Comparación: tres rectas "malas" frente a la recta de la SVM -----
x0 = np.linspace(0, 5.5, 200)
pred_1 = 5 * x0 - 20          # recta 1: mala (separa pero pasa muy cerca de los datos)
pred_2 = x0 - 1.8             # recta 2: separa pero con margen pequeño
pred_3 = 0.1 * x0 + 0.5       # recta 3: no separa las clases

plt.figure(figsize=(12, 2.7))

plt.subplot(121)
plt.plot(x0, pred_1, "g--", linewidth=2)
plt.plot(x0, pred_2, "m-", linewidth=2)
plt.plot(x0, pred_3, "r-", linewidth=2)
plt.plot(X[:, 0][y == 1], X[:, 1][y == 1], "bs", label="Iris versicolor")
plt.plot(X[:, 0][y == 0], X[:, 1][y == 0], "yo", label="Iris setosa")
plt.xlabel("Largo del pétalo", fontsize=14)
plt.ylabel("Ancho del pétalo", fontsize=14)
plt.legend(loc="upper left", fontsize=14)
plt.title("Rectas posibles", fontsize=14)
plt.axis([0, 5.5, 0, 2])

plt.subplot(122)
plot_svc_decision_boundary(svm_clf, 0, 5.5)
plt.plot(X[:, 0][y == 1], X[:, 1][y == 1], "bs")
plt.plot(X[:, 0][y == 0], X[:, 1][y == 0], "yo")
plt.xlabel("Largo del pétalo", fontsize=14)
plt.title("Recta de la SVM (margen máximo)", fontsize=14)
plt.axis([0, 5.5, 0, 2])

save_fig("large_margin_classification_plot")
plt.show()
```

**Cómo leer la figura:** a la izquierda hay varias rectas que podrían separar (o no) las clases. A la derecha está la elegida por la SVM: la de calle más ancha. Los puntos con círculo rosado son los vectores de soporte, y la recta no cambiaría si se borraran los demás.

### 4. Sensibilidad a la escala de las variables

Como la SVM trabaja con distancias, si una variable tiene valores mucho más grandes que otra, la primera domina el cálculo. En el ejemplo, $x_0$ va de 1 a 5 y $x_1$ de 20 a 80. Sin escalar, la frontera sale casi horizontal y poco útil. Con `StandardScaler` (que resta la media y divide por la desviación estándar de cada variable) el problema desaparece.

**Regla práctica:** siempre se escala antes de entrenar una SVM.

```python
# ----- Datos de juguete con escalas muy distintas -----
Xs = np.array([[1, 50], [5, 20], [3, 80], [5, 60]]).astype(np.float64)
ys = np.array([0, 0, 1, 1])

# ----- Sin escalar -----
svm_clf = SVC(kernel="linear", C=100)
svm_clf.fit(Xs, ys)

plt.figure(figsize=(12, 3.2))
plt.subplot(121)
plt.plot(Xs[:, 0][ys == 1], Xs[:, 1][ys == 1], "bo")
plt.plot(Xs[:, 0][ys == 0], Xs[:, 1][ys == 0], "ms")
plot_svc_decision_boundary(svm_clf, 0, 6)
plt.xlabel("$x_0$", fontsize=20)
plt.ylabel("$x_1$  ", fontsize=20, rotation=0)
plt.title("Sin escalar", fontsize=16)
plt.axis([0, 6, 0, 90])

# ----- Escalando: media 0 y desviación 1 en cada variable -----
scaler = StandardScaler()
X_scaled = scaler.fit_transform(Xs)
svm_clf.fit(X_scaled, ys)

plt.subplot(122)
plt.plot(X_scaled[:, 0][ys == 1], X_scaled[:, 1][ys == 1], "bo")
plt.plot(X_scaled[:, 0][ys == 0], X_scaled[:, 1][ys == 0], "ms")
plot_svc_decision_boundary(svm_clf, -2, 2)
plt.xlabel("$x_0$", fontsize=20)
plt.title("Escalado", fontsize=16)
plt.axis([-2, 2, -2, 2])

save_fig("sensitivity_to_feature_scales_plot")
plt.show()
```

### 5. Margen blando y el parámetro `C`

#### 5.1 Sensibilidad a los *outliers* (margen duro)

Con margen duro, un solo punto atípico puede dejar el problema sin solución (a la izquierda, "imposible") o torcer la recta hacia ese punto (a la derecha).

```python
# ----- Dos puntos atípicos de la clase 0 -----
X_outliers = np.array([[3.4, 1.3], [3.2, 0.8]])
y_outliers = np.array([0, 0])

# Conjunto 1: con el primer outlier (se mete dentro de la clase 1: ya no hay recta posible).
Xo1 = np.concatenate([X, X_outliers[:1]], axis=0)
yo1 = np.concatenate([y, y_outliers[:1]], axis=0)

# Conjunto 2: con el segundo outlier (sigue siendo separable, pero con calle muy estrecha).
Xo2 = np.concatenate([X, X_outliers[1:]], axis=0)
yo2 = np.concatenate([y, y_outliers[1:]], axis=0)

svm_clf2 = SVC(kernel="linear", C=1e9)
svm_clf2.fit(Xo2, yo2)

plt.figure(figsize=(12, 2.7))

plt.subplot(121)
plt.plot(Xo1[:, 0][yo1 == 1], Xo1[:, 1][yo1 == 1], "bs")
plt.plot(Xo1[:, 0][yo1 == 0], Xo1[:, 1][yo1 == 0], "yo")
plt.text(0.3, 1.0, "¡Imposible!", fontsize=24, color="red")
plt.xlabel("Largo del pétalo", fontsize=14)
plt.ylabel("Ancho del pétalo", fontsize=14)
plt.annotate("Outlier",
             xy=(X_outliers[0][0], X_outliers[0][1]),
             xytext=(2.5, 1.7), ha="center",
             arrowprops=dict(facecolor="black", shrink=0.1), fontsize=16)
plt.axis([0, 5.5, 0, 2])

plt.subplot(122)
plt.plot(Xo2[:, 0][yo2 == 1], Xo2[:, 1][yo2 == 1], "bs")
plt.plot(Xo2[:, 0][yo2 == 0], Xo2[:, 1][yo2 == 0], "yo")
plot_svc_decision_boundary(svm_clf2, 0, 5.5)
plt.xlabel("Largo del pétalo", fontsize=14)
plt.annotate("Outlier",
             xy=(X_outliers[1][0], X_outliers[1][1]),
             xytext=(3.2, 0.08), ha="center",
             arrowprops=dict(facecolor="black", shrink=0.1), fontsize=16)
plt.axis([0, 5.5, 0, 2])

save_fig("sensitivity_to_outliers_plot")
plt.show()
```

#### 5.2 Margen blando con `LinearSVC` y distintos valores de `C`

Ahora se usa el problema más difícil de **Iris virginica contra el resto**, cuyas clases se traslapan. Se entrena `LinearSVC` con pérdida *hinge* (sección 1.6) con un $C$ pequeño y uno grande, y se compara el ancho de la calle y las violaciones del margen.

Un punto **viola el margen** cuando $t\,h(\mathbf{x}) < 1$, es decir, cuando está dentro de la calle o del lado equivocado.

Para no modificar los modelos, se entrena en el espacio **escalado** y se grafica ahí, con la función `puntos_en_o_dentro_del_margen` que identifica esos puntos.

```python
def puntos_en_o_dentro_del_margen(X, y01, w, b):
    """Devuelve los puntos que violan el margen: t * (w.x + b) < 1.

    X    : datos (m, n)
    y01  : etiquetas 0/1
    w, b : pesos y sesgo del modelo lineal
    Con t = +1 / -1, un punto está bien clasificado y fuera de la calle solo si t*h >= 1.
    """
    t = 2 * np.asarray(y01) - 1                 # convierte 0/1 en -1/+1
    h = X.dot(w) + b                            # función de decisión
    return X[(t * h) < 1]


# ----- Datos: ¿es Iris virginica? (1 = sí, 0 = no) -----
iris = datasets.load_iris()
X = iris["data"][:, (2, 3)]                    # largo y ancho del pétalo
y = (iris["target"] == 2).astype(int)

scaler = StandardScaler()
X_s = scaler.fit_transform(X)                  # variables escaladas

# ----- Dos modelos: C pequeño (margen ancho) y C grande (margen estrecho) -----
modelos_C = {}
for C in (1, 100):
    clf = LinearSVC(C=C, loss="hinge", max_iter=200000, random_state=42)
    clf.fit(X_s, y)
    modelos_C[C] = clf

for C, clf in modelos_C.items():
    w, b = clf.coef_[0], clf.intercept_[0]
    n_viol = len(puntos_en_o_dentro_del_margen(X_s, y, w, b))
    print(f"C = {C:>3}: ancho de la calle = {2 / np.linalg.norm(w):.3f} | "
          f"puntos que violan el margen = {n_viol}")

# ----- Gráfica -----
plt.figure(figsize=(12, 3.8))
for k, (C, clf) in enumerate(modelos_C.items(), start=1):
    plt.subplot(1, 2, k)
    plt.plot(X_s[:, 0][y == 1], X_s[:, 1][y == 1], "g^", label="Iris virginica")
    plt.plot(X_s[:, 0][y == 0], X_s[:, 1][y == 0], "bs", label="No virginica")
    violadores = puntos_en_o_dentro_del_margen(X_s, y, clf.coef_[0], clf.intercept_[0])
    plot_svc_decision_boundary(clf, -2, 2, support_vectors=violadores)
    plt.xlabel("Largo del pétalo (escalado)", fontsize=14)
    if k == 1:
        plt.ylabel("Ancho del pétalo (escalado)", fontsize=14)
        plt.legend(loc="upper left", fontsize=12)
    plt.title(f"C = {C}", fontsize=16)
    plt.axis([-2, 2, -2, 2])

save_fig("regularization_plot")
plt.show()
```

```python
# ----- Predicción con una SVM de margen blando (con el escalado dentro de un Pipeline) -----
# Un Pipeline encadena pasos: primero escala y luego clasifica. Así, al predecir con
# datos nuevos se aplica automáticamente el mismo escalado del entrenamiento.
svm_clf = Pipeline([
    ("scaler", StandardScaler()),
    ("linear_svc", LinearSVC(C=1, loss="hinge", max_iter=200000, random_state=42)),
])
svm_clf.fit(X, y)

# Una flor con pétalo de 5.5 cm de largo y 1.7 cm de ancho: ¿es virginica?
print("Predicción para [5.5, 1.7]:", svm_clf.predict([[5.5, 1.7]]), "(1 = virginica)")
```

### 6. Clasificación no lineal y kernels

#### 6.1 Idea: llevar los datos a más dimensiones

A la izquierda, datos en una sola dimensión que **no** se pueden separar con un punto (la clase verde queda en el centro y la azul en los extremos). Si se agrega una segunda característica $x_2 = x_1^2$, a la derecha, ya se separan con una recta horizontal.

```python
# ----- Datos en 1D que no se separan con un solo corte -----
X1D = np.linspace(-4, 4, 9).reshape(-1, 1)
X2D = np.c_[X1D, X1D ** 2]                        # nueva característica: x2 = x1^2
y1d = np.array([0, 0, 1, 1, 1, 1, 1, 0, 0])

plt.figure(figsize=(11, 4))

plt.subplot(121)
plt.grid(True, which="both")
plt.axhline(y=0, color="k")
plt.plot(X1D[:, 0][y1d == 0], np.zeros(4), "bs")
plt.plot(X1D[:, 0][y1d == 1], np.zeros(5), "g^")
plt.gca().get_yaxis().set_ticks([])
plt.xlabel(r"$x_1$", fontsize=20)
plt.title("1 dimensión: no separable", fontsize=14)
plt.axis([-4.5, 4.5, -0.2, 0.2])

plt.subplot(122)
plt.grid(True, which="both")
plt.axhline(y=0, color="k")
plt.axvline(x=0, color="k")
plt.plot(X2D[:, 0][y1d == 0], X2D[:, 1][y1d == 0], "bs")
plt.plot(X2D[:, 0][y1d == 1], X2D[:, 1][y1d == 1], "g^")
plt.xlabel(r"$x_1$", fontsize=20)
plt.ylabel(r"$x_2$", fontsize=20, rotation=0)
plt.gca().get_yaxis().set_ticks([0, 4, 8, 12, 16])
plt.plot([-4.5, 4.5], [6.5, 6.5], "r--", linewidth=3)      # recta que ahora sí separa
plt.title("2 dimensiones: separable con una recta", fontsize=14)
plt.axis([-4.5, 4.5, -1, 17])

plt.subplots_adjust(right=1)
save_fig("higher_dimensions_plot", tight_layout=False)
plt.show()
```

#### 6.2 El conjunto de datos de las "lunas" (*moons*)

`make_moons` genera dos medias lunas entrelazadas con algo de ruido. Ninguna recta las separa bien.

```python
from sklearn.datasets import make_moons
from sklearn.preprocessing import PolynomialFeatures

X, y = make_moons(n_samples=100, noise=0.15, random_state=42)


def plot_dataset(X, y, axes):
    """Dibuja los puntos de las dos clases de un conjunto 2D.

    axes = [xmin, xmax, ymin, ymax] define los límites de la gráfica.
    """
    plt.plot(X[:, 0][y == 0], X[:, 1][y == 0], "bs")     # clase 0: cuadrados azules
    plt.plot(X[:, 0][y == 1], X[:, 1][y == 1], "g^")     # clase 1: triángulos verdes
    plt.axis(axes)
    plt.grid(True, which="both")
    plt.xlabel(r"$x_1$", fontsize=20)
    plt.ylabel(r"$x_2$", fontsize=20, rotation=0)


def plot_predictions(clf, axes):
    """Colorea las regiones de decisión de un clasificador entrenado en 2D.

    Evalúa el modelo en una malla de 100x100 puntos. El color de fondo indica la clase
    predicha y el degradado el valor de la función de decisión.
    """
    x0s = np.linspace(axes[0], axes[1], 100)
    x1s = np.linspace(axes[2], axes[3], 100)
    x0, x1 = np.meshgrid(x0s, x1s)
    X_malla = np.c_[x0.ravel(), x1.ravel()]
    y_pred = clf.predict(X_malla).reshape(x0.shape)
    y_decision = clf.decision_function(X_malla).reshape(x0.shape)
    plt.contourf(x0, x1, y_pred, cmap=plt.cm.brg, alpha=0.2)
    plt.contourf(x0, x1, y_decision, cmap=plt.cm.brg, alpha=0.1)


plot_dataset(X, y, [-1.5, 2.5, -1, 1.5])
plt.title("Conjunto de datos: lunas", fontsize=14)
plt.show()
```

#### 6.3 Primer camino: agregar características polinómicas

`PolynomialFeatures(degree=3)` crea explícitamente $x_1^2, x_2^2, x_1x_2, x_1^3, \ldots$ y luego se usa una SVM **lineal** en ese espacio ampliado. Funciona, pero con muchas características o grados altos el número de columnas se dispara.

```python
polynomial_svm_clf = Pipeline([
    ("poly_features", PolynomialFeatures(degree=3)),   # crea las características polinómicas
    ("scaler", StandardScaler()),                      # escala (obligatorio en SVM)
    ("svm_clf", LinearSVC(C=10, loss="hinge", max_iter=200000, random_state=42)),
])
polynomial_svm_clf.fit(X, y)

plot_predictions(polynomial_svm_clf, [-1.5, 2.5, -1, 1.5])
plot_dataset(X, y, [-1.5, 2.5, -1, 1.5])
plt.title("Características polinómicas (grado 3) + LinearSVC", fontsize=13)
save_fig("moons_polynomial_svc_plot")
plt.show()

print("Exactitud en entrenamiento:", polynomial_svm_clf.score(X, y))
```

#### 6.4 Segundo camino: el truco del kernel

Con `SVC(kernel="poly")` se obtiene el mismo efecto que con las características polinómicas **sin construirlas** (sección 1.7). Se comparan dos configuraciones:

- $d=3,\ r=1,\ C=5$: frontera suave.
- $d=10,\ r=100,\ C=5$: frontera mucho más flexible, con riesgo de sobreajuste.

```python
# Kernel polinómico de grado 3: K(a,b) = (gamma * a.b + coef0)^degree
poly_kernel_svm_clf = Pipeline([
    ("scaler", StandardScaler()),
    ("svm_clf", SVC(kernel="poly", degree=3, coef0=1, C=5)),
])
poly_kernel_svm_clf.fit(X, y)

# Kernel polinómico de grado 10 (mucho más flexible)
poly100_kernel_svm_clf = Pipeline([
    ("scaler", StandardScaler()),
    ("svm_clf", SVC(kernel="poly", degree=10, coef0=100, C=5)),
])
poly100_kernel_svm_clf.fit(X, y)

plt.figure(figsize=(11, 4))

plt.subplot(121)
plot_predictions(poly_kernel_svm_clf, [-1.5, 2.5, -1, 1.5])
plot_dataset(X, y, [-1.5, 2.5, -1, 1.5])
plt.title(r"$d=3,\ r=1,\ C=5$", fontsize=18)

plt.subplot(122)
plot_predictions(poly100_kernel_svm_clf, [-1.5, 2.5, -1, 1.5])
plot_dataset(X, y, [-1.5, 2.5, -1, 1.5])
plt.title(r"$d=10,\ r=100,\ C=5$", fontsize=18)

save_fig("moons_kernelized_polynomial_svc_plot")
plt.show()
```

#### 6.5 Kernel gaussiano (RBF) y el hiperparámetro `gamma`

El kernel RBF mide **similitud**: vale 1 cuando dos puntos coinciden y decae hacia 0 al alejarse. El parámetro $\gamma$ controla qué tan rápido decae.

```python
def gaussian_rbf(x, landmark, gamma):
    """Kernel gaussiano: exp(-gamma * ||x - landmark||^2).

    Devuelve 1 si x coincide con el punto de referencia (landmark) y se acerca a 0 a medida
    que se aleja. Acepta x como arreglo (m, n) y landmark como arreglo (n,) o (1, n).
    """
    return np.exp(-gamma * np.linalg.norm(x - landmark, axis=1) ** 2)


# ----- Cómo cambia la similitud con la distancia, para distintos gamma -----
d = np.linspace(0, 3, 200).reshape(-1, 1)                # distancia al punto de referencia
plt.figure(figsize=(6, 3.5))
for g in (0.1, 0.5, 2, 5):
    plt.plot(d, gaussian_rbf(d, 0, g), label=fr"$\gamma = {g}$", linewidth=2)
plt.xlabel("Distancia entre los dos puntos")
plt.ylabel("Similitud")
plt.title("Kernel RBF: efecto de gamma", fontsize=14)
plt.grid(True)
plt.legend()
plt.show()

# ----- Ejemplo numérico: el punto x1 = -1 respecto a dos puntos de referencia (-2 y 1) -----
gamma = 0.3
x1_ejemplo = X1D[3, 0]
for landmark in (-2, 1):
    k = gaussian_rbf(np.array([[x1_ejemplo]]), np.array([[landmark]]), gamma)
    print(f"Similitud entre x1 = {x1_ejemplo} y el punto {landmark:>2}: {k[0]:.4f}")
```

##### Efecto combinado de `gamma` y `C` en un `SVC` con kernel RBF

Se prueban cuatro combinaciones. Observe lo siguiente:

- **`gamma` grande** (5): la frontera se pega a los puntos (más sobreajuste).
- **`gamma` pequeño** (0.1): frontera suave.
- **`C` grande** (1000): se penalizan mucho los errores (más sobreajuste).
- **`C` pequeño** (0.001): se toleran muchos errores (subajuste).

```python
gamma1, gamma2 = 0.1, 5
C1, C2 = 0.001, 1000
hiperparametros = (gamma1, C1), (gamma1, C2), (gamma2, C1), (gamma2, C2)

svm_clfs = []
for gamma, C in hiperparametros:
    rbf_kernel_svm_clf = Pipeline([
        ("scaler", StandardScaler()),
        ("svm_clf", SVC(kernel="rbf", gamma=gamma, C=C)),
    ])
    rbf_kernel_svm_clf.fit(X, y)
    svm_clfs.append(rbf_kernel_svm_clf)

plt.figure(figsize=(11, 7))
for i, clf in enumerate(svm_clfs):
    plt.subplot(221 + i)
    plot_predictions(clf, [-1.5, 2.5, -1, 1.5])
    plot_dataset(X, y, [-1.5, 2.5, -1, 1.5])
    gamma, C = hiperparametros[i]
    plt.title(fr"$\gamma = {gamma},\ C = {C}$", fontsize=16)
    print(f"gamma = {gamma:<4} C = {C:<6} exactitud en entrenamiento = {clf.score(X, y):.2f}")

save_fig("moons_rbf_svc_plot")
plt.show()
```

### 7. Regresión con SVM (SVR)

Aquí la SVM predice un **número** (sección 1.9). El hiperparámetro `epsilon` define el ancho del tubo: dentro de él, el error no cuenta. Un `epsilon` grande da un tubo ancho (pocos vectores de soporte), y uno pequeño da un tubo angosto (más vectores de soporte).

#### 7.1 Regresión lineal: `LinearSVR`

```python
# ----- Datos: una recta con ruido, y = 4 + 3x + ruido -----
np.random.seed(42)
m = 50
X = 2 * np.random.rand(m, 1)
y = (4 + 3 * X + np.random.randn(m, 1)).ravel()


def plot_svm_regression(svm_reg, X, y, axes):
    """Dibuja un modelo de regresión SVM: línea predicha, tubo epsilon y vectores de soporte.

    Los vectores de soporte son los puntos que quedan sobre o fuera del tubo,
    es decir, |y - y_predicho| >= epsilon.
    """
    x1s = np.linspace(axes[0], axes[1], 100).reshape(100, 1)
    y_pred = svm_reg.predict(x1s)
    plt.plot(x1s, y_pred, "k-", linewidth=2, label=r"$\hat{y}$")
    plt.plot(x1s, y_pred + svm_reg.epsilon, "k--")
    plt.plot(x1s, y_pred - svm_reg.epsilon, "k--")

    fuera_del_tubo = np.abs(y - svm_reg.predict(X)) >= svm_reg.epsilon
    plt.scatter(X[fuera_del_tubo], y[fuera_del_tubo], s=180, facecolors="#FFAAAA")
    plt.plot(X, y, "bo")
    plt.xlabel(r"$x_1$", fontsize=18)
    plt.legend(loc="upper left", fontsize=18)
    plt.axis(axes)


svm_reg1 = LinearSVR(epsilon=1.5, max_iter=200000, random_state=42).fit(X, y)
svm_reg2 = LinearSVR(epsilon=0.5, max_iter=200000, random_state=42).fit(X, y)

plt.figure(figsize=(9, 4))
plt.subplot(121)
plot_svm_regression(svm_reg1, X, y, [0, 2, 3, 11])
plt.title(fr"$\epsilon = {svm_reg1.epsilon}$", fontsize=18)
plt.ylabel(r"$y$", fontsize=18, rotation=0)
plt.subplot(122)
plot_svm_regression(svm_reg2, X, y, [0, 2, 3, 11])
plt.title(fr"$\epsilon = {svm_reg2.epsilon}$", fontsize=18)
save_fig("svm_regression_plot")
plt.show()
```

#### 7.2 Regresión no lineal: `SVR` con kernel polinómico

Los datos siguen una parábola. `C` controla la regularización: `C` grande se ajusta más a los datos y `C` pequeño da una curva más plana.

```python
np.random.seed(42)
m = 100
X = 2 * np.random.rand(m, 1) - 1
y = (0.2 + 0.1 * X + 0.5 * X ** 2 + np.random.randn(m, 1) / 10).ravel()

svm_poly_reg1 = SVR(kernel="poly", degree=2, C=100, epsilon=0.1).fit(X, y)
svm_poly_reg2 = SVR(kernel="poly", degree=2, C=0.01, epsilon=0.1).fit(X, y)

plt.figure(figsize=(9, 4))
plt.subplot(121)
plot_svm_regression(svm_poly_reg1, X, y, [-1, 1, 0, 1])
plt.title(fr"grado={svm_poly_reg1.degree}, $C$={svm_poly_reg1.C}, $\epsilon$={svm_poly_reg1.epsilon}", fontsize=14)
plt.ylabel(r"$y$", fontsize=18, rotation=0)
plt.subplot(122)
plot_svm_regression(svm_poly_reg2, X, y, [-1, 1, 0, 1])
plt.title(fr"grado={svm_poly_reg2.degree}, $C$={svm_poly_reg2.C}, $\epsilon$={svm_poly_reg2.epsilon}", fontsize=14)
save_fig("svm_with_polynomial_kernel_plot")
plt.show()
```

### 8. Por dentro: pérdida hinge y SVM programada desde cero

#### 8.1 La pérdida hinge

Vale 0 cuando $t \ge 1$ (bien clasificado y fuera de la calle) y crece linealmente cuando $t < 1$.

```python
t = np.linspace(-2, 4, 200)
h = np.where(1 - t < 0, 0, 1 - t)          # max(0, 1 - t)

plt.figure(figsize=(5, 2.8))
plt.plot(t, h, "b-", linewidth=2, label="$max(0, 1 - t)$")
plt.grid(True, which="both")
plt.axhline(y=0, color="k")
plt.axvline(x=0, color="k")
plt.yticks(np.arange(-1, 2.5, 1))
plt.xlabel("$t$", fontsize=16)
plt.axis([-2, 4, -1, 2.5])
plt.legend(loc="upper right", fontsize=16)
save_fig("hinge_plot")
plt.show()
```

#### 8.2 SVM lineal con descenso del gradiente (por lotes)

Se programa la SVM minimizando directamente la función de costo de la sección 1.6:

$$
J(\mathbf{w}, b) = \tfrac{1}{2}\,\mathbf{w}^T\mathbf{w} + C \sum_{i \in V}\left(1 - t^{(i)}\left(\mathbf{w}^T\mathbf{x}^{(i)} + b\right)\right)
$$

donde $V$ es el conjunto de puntos que violan el margen ($t\,h < 1$), porque para los demás la pérdida hinge es 0. Las derivadas son:

$$
\frac{\partial J}{\partial \mathbf{w}} = \mathbf{w} - C \sum_{i \in V} t^{(i)} \mathbf{x}^{(i)}
\qquad
\frac{\partial J}{\partial b} = -C \sum_{i \in V} t^{(i)}
$$

Y la actualización es la misma de la guía (sección 5.5): $\mathbf{w} \leftarrow \mathbf{w} - \eta\, \partial J/\partial \mathbf{w}$, con una tasa de aprendizaje $\eta$ que va disminuyendo con las épocas.

```python
from sklearn.base import BaseEstimator


class MyLinearSVC(BaseEstimator):
    """SVM lineal de margen blando entrenada con descenso del gradiente por lotes.

    Minimiza  J(w, b) = 1/2 * ||w||^2 + C * suma( max(0, 1 - t * (w.x + b)) ).

    Parámetros
    ----------
    C : float
        Penalización de las violaciones del margen (mayor C = calle más estrecha).
    eta0 : float
        Numerador de la tasa de aprendizaje: eta(epoca) = eta0 / (epoca + eta_d).
    eta_d : float
        Desplazamiento del denominador de la tasa de aprendizaje.
    n_epochs : int
        Número de épocas (pasadas completas sobre los datos).
    random_state : int o None
        Semilla para la inicialización aleatoria de los pesos.

    Atributos (después de fit)
    --------------------------
    coef_ : array (1, n)         pesos w
    intercept_ : array (1,)      sesgo b
    support_vectors_ : array     puntos que violan el margen o están sobre él
    Js : list                    valor de la función de costo en cada época

    Correcciones respecto al código original: usa self.C (antes usaba una variable global),
    calcula los vectores de soporte con t*b (antes se omitía t) y guarda coef_ con forma (1, n).
    """

    def __init__(self, C=1, eta0=1, eta_d=10000, n_epochs=1000, random_state=None):
        self.C = C
        self.eta0 = eta0
        self.eta_d = eta_d
        self.n_epochs = n_epochs
        self.random_state = random_state

    def eta(self, epoch):
        """Tasa de aprendizaje, decreciente con las épocas."""
        return self.eta0 / (epoch + self.eta_d)

    def fit(self, X, y):
        X = np.asarray(X, dtype=float)
        y = np.asarray(y).reshape(-1, 1)             # etiquetas 0/1 como columna

        # Inicialización aleatoria de los pesos y sesgo en cero.
        if self.random_state is not None:
            np.random.seed(self.random_state)
        w = np.random.randn(X.shape[1], 1)           # un peso por característica
        b = 0.0

        t = y * 2 - 1                                # 0/1  ->  -1/+1
        X_t = X * t                                  # cada fila multiplicada por su t
        self.Js = []

        for epoch in range(self.n_epochs):
            # Puntos que violan el margen: t * (w.x + b) < 1  <=>  X_t.w + t*b < 1
            viola = (X_t.dot(w) + t * b < 1).ravel()
            X_t_v = X_t[viola]
            t_v = t[viola]

            # Función de costo (solo los que violan aportan pérdida hinge).
            J = 0.5 * np.sum(w * w) + self.C * (np.sum(1 - X_t_v.dot(w)) - b * np.sum(t_v))
            self.Js.append(J)

            # Gradientes (ver fórmulas arriba).
            grad_w = w - self.C * np.sum(X_t_v, axis=0).reshape(-1, 1)
            grad_b = -self.C * np.sum(t_v)

            # Actualización por descenso del gradiente.
            w = w - self.eta(epoch) * grad_w
            b = b - self.eta(epoch) * grad_b

        self.coef_ = w.reshape(1, -1)
        self.intercept_ = np.array([b])
        viola = (X_t.dot(w) + t * b < 1).ravel()
        self.support_vectors_ = X[viola]
        return self

    def decision_function(self, X):
        """Valor h(x) = w.x + b para cada ejemplo."""
        return np.asarray(X, dtype=float).dot(self.coef_[0]) + self.intercept_[0]

    def predict(self, X):
        """Clase 1 si h(x) >= 0 y clase 0 en caso contrario."""
        return (self.decision_function(X) >= 0).astype(np.float64)


# ----- Datos: Iris virginica contra el resto -----
iris = datasets.load_iris()
X = iris["data"][:, (2, 3)]
y = (iris["target"] == 2).astype(np.float64)

C = 2
inicio = time.time()
mi_svm = MyLinearSVC(C=C, eta0=10, eta_d=1000, n_epochs=60000, random_state=2)
mi_svm.fit(X, y)
print(f"Entrenamiento propio: {time.time() - inicio:.1f} s")
print("Predicciones para [5, 2] y [4, 1]:", mi_svm.predict(np.array([[5, 2], [4, 1]])))
```

```python
# ----- La función de costo debe bajar con las épocas (igual que la pérdida de la guía) -----
plt.figure(figsize=(6, 3.5))
plt.plot(range(mi_svm.n_epochs), mi_svm.Js)
plt.axis([0, mi_svm.n_epochs, 0, 100])
plt.xlabel("Época")
plt.ylabel("Costo J")
plt.title("Evolución de la función de costo", fontsize=14)
plt.grid(True)
plt.show()
```

#### 8.3 Comparación con scikit-learn

Se comparan los pesos y el sesgo de tres implementaciones del mismo problema:

- `MyLinearSVC`: la programada arriba.
- `SVC(kernel="linear")`: la de scikit-learn.
- `SGDClassifier(loss="hinge")`: descenso del gradiente estocástico, con `alpha = 1/(m*C)` para que minimice el mismo costo y una tasa de aprendizaje constante.

Si todo está bien, los tres resultados deben ser parecidos. El `SGDClassifier` es el más sensible a la tasa de aprendizaje: con la tasa automática por defecto (`learning_rate="optimal"`) se queda lejos de la solución con estos datos sin escalar, por eso aquí se fija una tasa constante.

```python
from sklearn.linear_model import SGDClassifier

yr = y.astype(int)
m = len(X)

svm_sk = SVC(kernel="linear", C=C).fit(X, yr)
sgd_clf = SGDClassifier(loss="hinge", alpha=1 / (m * C), learning_rate="constant", eta0=0.001,
                        max_iter=50000, tol=None, random_state=42).fit(X, yr)

print("Pesos y sesgo del mismo problema:")
print(f"  MyLinearSVC : w = {mi_svm.coef_[0].round(3)}, b = {mi_svm.intercept_[0]:.3f}")
print(f"  SVC         : w = {svm_sk.coef_[0].round(3)}, b = {svm_sk.intercept_[0]:.3f}")
print(f"  SGD         : w = {sgd_clf.coef_[0].round(3)}, b = {sgd_clf.intercept_[0]:.3f}")

# ----- Gráfica comparativa -----
vs_sgd = puntos_en_o_dentro_del_margen(X, yr, sgd_clf.coef_[0], sgd_clf.intercept_[0])
plt.figure(figsize=(15, 3.6))
for k, (nombre, clf, vs) in enumerate([("MyLinearSVC", mi_svm, None),
                                       ("SVC", svm_sk, None),
                                       ("SGDClassifier", sgd_clf, vs_sgd)], start=1):
    plt.subplot(1, 3, k)
    plt.plot(X[:, 0][yr == 1], X[:, 1][yr == 1], "g^", label="Iris virginica")
    plt.plot(X[:, 0][yr == 0], X[:, 1][yr == 0], "bs", label="No virginica")
    plot_svc_decision_boundary(clf, 4, 6, support_vectors=vs)
    plt.xlabel("Largo del pétalo", fontsize=14)
    if k == 1:
        plt.ylabel("Ancho del pétalo", fontsize=14)
        plt.legend(loc="upper left", fontsize=11)
    plt.title(nombre, fontsize=14)
    plt.axis([4, 6, 0.8, 2.8])

save_fig("comparacion_implementaciones")
plt.show()
```

### 9. Aplicación: reconocimiento de dígitos escritos a mano con SVM

#### 9.1 Planteamiento

Es la misma tarea que se ve en la guía de clase con MNIST (sección 5.4), pero resuelta con una SVM: dada la imagen de un dígito escrito a mano, decir cuál es (0 al 9). Se usa el conjunto `digits` de scikit-learn:

- 1797 imágenes en escala de grises de **8×8 píxeles** (más pequeñas que las de MNIST, que son de 28×28).
- Cada píxel tiene un valor de 0 (blanco) a 16 (negro).
- 10 clases (los dígitos del 0 al 9).
- Cada imagen se aplana en un vector de **64 características**, igual que `Flatten` en la red de Fashion MNIST.
- Los píxeles se **normalizan a [0, 1]** dividiendo entre 16, igual que se dividía entre 255 en Fashion MNIST.

#### 9.2 Flujo de trabajo

1. Cargar y explorar los datos.
2. Separar entrenamiento (80 %) y prueba (20 %), manteniendo la proporción de cada dígito.
3. Comparar kernels con **validación cruzada** en el conjunto de entrenamiento.
4. Buscar los mejores hiperparámetros `C` y `gamma` con `GridSearchCV`.
5. Evaluar **una sola vez** con el conjunto de prueba.
6. Analizar errores, vectores de soporte y comparar con una red neuronal.
7. Guardar el modelo y usarlo en una función de reconocimiento.

#### 9.3 Carga y exploración de los datos

```python
from sklearn.datasets import load_digits

digitos = load_digits()
X_dig = digitos.data / 16.0       # (1797, 64): cada fila es una imagen aplanada, normalizada a [0, 1]
y_dig = digitos.target            # (1797,)   : el dígito real, de 0 a 9
imagenes = digitos.images         # (1797, 8, 8): las mismas imágenes en forma de matriz

print("Forma de X (ejemplos, características):", X_dig.shape)
print("Forma de y                             :", y_dig.shape)
print("Clases                                 :", np.unique(y_dig))
print("Rango de los píxeles (normalizados)    :", X_dig.min(), "a", X_dig.max())
print("Ejemplos por clase                     :", np.bincount(y_dig))

# ----- Algunas imágenes con su etiqueta -----
plt.figure(figsize=(10, 4.2))
for i in range(15):
    plt.subplot(3, 5, i + 1)
    plt.imshow(imagenes[i], cmap="gray_r")
    plt.title(f"Dígito: {y_dig[i]}")
    plt.axis("off")
plt.suptitle("Ejemplos del conjunto digits (8x8 píxeles)", fontsize=14)
plt.tight_layout()
plt.show()
```

#### 9.4 División en entrenamiento y prueba

`stratify=y_dig` conserva en cada conjunto la misma proporción de cada dígito. El conjunto de prueba **no se toca** hasta la evaluación final, para que mida cómo se comporta el modelo con datos que nunca vio (sección 5.4 de la guía).

```python
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X_dig, y_dig,
    test_size=0.20,          # 20 % para prueba
    stratify=y_dig,          # misma proporción de cada dígito en ambos conjuntos
    random_state=42,
)

print("Entrenamiento:", X_train.shape, "| Prueba:", X_test.shape)
```

#### 9.5 Comparación de kernels con validación cruzada

**Validación cruzada de 5 particiones (*5-fold*):** el conjunto de entrenamiento se divide en 5 partes. Se entrena con 4 y se evalúa con la restante, y se repite 5 veces rotando la parte de evaluación. El promedio de las 5 exactitudes es una estimación más confiable que una sola división.

Se comparan los tres kernels de la sección 1.7 con hiperparámetros por defecto.

**Sobre el escalado:** aquí no se usa `StandardScaler`. Todos los píxeles están en las mismas unidades, por lo que basta con la normalización a [0, 1] que ya se hizo. Además, `StandardScaler` amplificaría mucho los píxeles de los bordes de la imagen, que casi siempre valen 0 y casi no varían. `StandardScaler` es necesario cuando las variables tienen unidades distintas, como en los ejemplos de las partes 4 y 5.

```python
from sklearn.model_selection import cross_val_score, StratifiedKFold

validacion = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

kernels = {
    "Lineal": SVC(kernel="linear"),
    "Polinomial (grado 3)": SVC(kernel="poly", degree=3),
    "Gaussiano (RBF)": SVC(kernel="rbf"),
}

resultados_kernel = {}
print(f"{'Kernel':<22}{'Exactitud media':>16}{'Desv. est.':>12}")
for nombre, modelo in kernels.items():
    puntajes = cross_val_score(modelo, X_train, y_train, cv=validacion)
    resultados_kernel[nombre] = puntajes.mean()
    print(f"{nombre:<22}{puntajes.mean():>16.4f}{puntajes.std():>12.4f}")
```

#### 9.6 Búsqueda de hiperparámetros (`GridSearchCV`)

Se afina el kernel RBF, que es el más usado en la práctica (si en la comparación anterior otro kernel hubiera quedado claramente por encima, se afinaría ese). Sus dos hiperparámetros, `C` y `gamma`, se ajustan probando todas las combinaciones de una **malla** con validación cruzada. Para evitar que pase lo mismo que en el ejemplo de las lunas (sobreajuste con `gamma` o `C` grandes), la elección se hace con datos de validación, no de entrenamiento.

```python
from sklearn.model_selection import GridSearchCV

# Malla de valores a probar: se entrena y evalúa una SVM por cada pareja (C, gamma).
malla = {
    "C": [0.1, 1, 10, 100, 1000],
    "gamma": [0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0],
}

busqueda = GridSearchCV(SVC(kernel="rbf"), malla, cv=validacion, scoring="accuracy", n_jobs=-1)
inicio = time.time()
busqueda.fit(X_train, y_train)
print(f"Búsqueda terminada en {time.time() - inicio:.1f} s")
print("Mejores hiperparámetros :", busqueda.best_params_)
print(f"Mejor exactitud (CV)    : {busqueda.best_score_:.4f}")

mejor_modelo = busqueda.best_estimator_        # SVC ya reentrenado con todo el conjunto de entrenamiento
```

```python
# ----- Mapa de calor: exactitud de validación para cada combinación (C, gamma) -----
puntajes = busqueda.cv_results_["mean_test_score"].reshape(len(malla["C"]),
                                                           len(malla["gamma"]))

plt.figure(figsize=(9, 4.8))
# El rango de colores se acota a los 10 puntos porcentuales superiores para distinguir las mejores combinaciones.
vmin = max(puntajes.min(), puntajes.max() - 0.10)
plt.imshow(puntajes, cmap="viridis", vmin=vmin, vmax=puntajes.max())
plt.colorbar(label="Exactitud de validación")
plt.xticks(range(len(malla["gamma"])), malla["gamma"])
plt.yticks(range(len(malla["C"])), malla["C"])
plt.xlabel("gamma")
plt.ylabel("C")
plt.title("Búsqueda en malla: exactitud para cada (C, gamma)", fontsize=13)
for i in range(puntajes.shape[0]):
    for j in range(puntajes.shape[1]):
        plt.text(j, i, f"{puntajes[i, j]:.3f}", ha="center", va="center",
                 color="white" if puntajes[i, j] < (vmin + puntajes.max()) / 2 else "black", fontsize=8)
save_fig("heatmap_busqueda_svm")
plt.show()
```

**Cómo leer el mapa:** las combinaciones con `C` y `gamma` muy pequeños subajustan, y las de `gamma` muy alto sobreajustan, como se vio con las lunas en la sección 6.5. Conviene revisar que el mejor punto no quede en el borde de la malla: si queda en un borde, hay que ampliar la malla en esa dirección y repetir.

#### 9.7 Evaluación final con el conjunto de prueba

Se evalúa **una sola vez**. El reporte de clasificación da, para cada dígito:

- **Precisión (*precision*):** de las veces que el modelo dijo "es un 7", cuántas acertó.
- **Exhaustividad (*recall*):** de todos los 7 reales, cuántos encontró.
- **F1:** promedio armónico de las dos.

```python
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, ConfusionMatrixDisplay

y_pred = mejor_modelo.predict(X_test)
exactitud_svm = accuracy_score(y_test, y_pred)

print(f"Exactitud en el conjunto de prueba: {exactitud_svm:.4%}\n")
print(classification_report(y_test, y_pred, digits=4))
```

```python
# ----- Matriz de confusión: fila = dígito real, columna = dígito predicho -----
cm = confusion_matrix(y_test, y_pred)

fig, ax = plt.subplots(figsize=(7.5, 6.5))
ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=range(10)).plot(
    ax=ax, cmap="Blues", colorbar=False)
ax.set_title("Matriz de confusión: SVM (kernel RBF)")
ax.set_xlabel("Dígito predicho")
ax.set_ylabel("Dígito real")
plt.tight_layout()
save_fig("matriz_confusion_svm")
plt.show()

# ----- Pares de dígitos que más se confunden -----
pares = []
for i in range(10):
    for j in range(i + 1, 10):
        pares.append((cm[i, j] + cm[j, i], i, j))
pares.sort(reverse=True)
print("Pares de dígitos con más confusiones (en ambos sentidos):")
for total, i, j in pares[:3]:
    print(f"  {i} <-> {j}: {total} errores")
```

#### 9.8 Análisis de los errores

Se muestran los dígitos que el modelo clasificó mal. Suelen ser trazos ambiguos que también costaría leer a una persona.

```python
indices_error = np.where(y_pred != y_test)[0]
print(f"El modelo se equivocó en {len(indices_error)} de {len(y_test)} imágenes de prueba.")

if len(indices_error) > 0:
    n_mostrar = min(8, len(indices_error))
    plt.figure(figsize=(10, 2.8))
    for k, idx in enumerate(indices_error[:n_mostrar]):
        plt.subplot(1, n_mostrar, k + 1)
        plt.imshow(X_test[idx].reshape(8, 8), cmap="gray_r")
        plt.title(f"Real: {y_test[idx]}\nPred: {y_pred[idx]}", fontsize=10)
        plt.axis("off")
    plt.suptitle("Imágenes mal clasificadas", fontsize=13)
    plt.tight_layout()
    plt.show()
```

#### 9.9 Vectores de soporte

Solo los vectores de soporte definen el modelo (sección 1.3). Se cuenta cuántos usa cada dígito. Entre menos usa un dígito, más fácil de separar le resultó al modelo.

```python
n_soporte = mejor_modelo.n_support_               # vectores de soporte por clase

print("Vectores de soporte por dígito:", {d: int(n) for d, n in enumerate(n_soporte)})
print(f"Total: {n_soporte.sum()} de {len(X_train)} ejemplos de entrenamiento "
      f"({n_soporte.sum() / len(X_train):.1%})")
print("Clasificadores internos (uno contra uno): ", 10 * 9 // 2)

plt.figure(figsize=(7, 3.2))
plt.bar(range(10), n_soporte, color="steelblue")
plt.xticks(range(10))
plt.xlabel("Dígito")
plt.ylabel("Vectores de soporte")
plt.title("Vectores de soporte por clase", fontsize=13)
plt.grid(True, axis="y", alpha=0.3)
plt.show()
```

#### 9.10 Comparación con una red neuronal

Para conectar con el resto de la materia, se entrena una red neuronal del tipo de la guía (capa oculta densa con 128 neuronas) con **los mismos datos**, y se compara exactitud y tiempo. Se usa `MLPClassifier` de scikit-learn, que implementa propagación hacia adelante y retropropagación.

No es una comparación definitiva de los dos métodos: con otros datos, otras arquitecturas o ajustes de hiperparámetros los resultados pueden cambiar. Sirve para ver cómo se comportan ambos en el mismo problema.

```python
from sklearn.neural_network import MLPClassifier

red = MLPClassifier(hidden_layer_sizes=(128,), activation="relu",
                    max_iter=500, random_state=42)

inicio = time.time()
red.fit(X_train, y_train)
tiempo_red = time.time() - inicio

inicio = time.time()
mejor_modelo.fit(X_train, y_train)               # se vuelve a entrenar solo para medir el tiempo
tiempo_svm = time.time() - inicio

exactitud_red = accuracy_score(y_test, red.predict(X_test))

print(f"{'Modelo':<28}{'Exactitud (prueba)':>20}{'Tiempo de entrenamiento':>26}")
print(f"{'SVM (RBF, mejor C y gamma)':<28}{exactitud_svm:>20.4%}{tiempo_svm:>22.3f} s")
print(f"{'Red neuronal (128 ReLU)':<28}{exactitud_red:>20.4%}{tiempo_red:>22.3f} s")
```

#### 9.11 Guardar el modelo y usarlo en una aplicación

Una aplicación real no reentrena cada vez: entrena una vez, **guarda el modelo** en un archivo y lo **carga** cuando lo necesita. Se usa `joblib` y se define una función `reconocer_digito` que recibe una imagen de 8×8 con intensidades de 0 a 16, la normaliza y devuelve el dígito reconocido junto con los tres dígitos con mayor puntaje.

```python
import joblib

# ----- Guardar y volver a cargar el modelo entrenado -----
joblib.dump(mejor_modelo, "modelo_svm_digitos.joblib")
modelo_cargado = joblib.load("modelo_svm_digitos.joblib")

# Comprobación: el modelo cargado debe dar exactamente las mismas predicciones.
assert np.array_equal(modelo_cargado.predict(X_test), mejor_modelo.predict(X_test))
print("Modelo guardado en modelo_svm_digitos.joblib y verificado.")


def reconocer_digito(imagen, modelo=modelo_cargado):
    """Reconoce un dígito escrito a mano a partir de una imagen de 8x8 píxeles.

    Parámetros
    ----------
    imagen : array de forma (8, 8) o (64,)
        Intensidades de 0 (blanco) a 16 (negro), como en el conjunto digits.
    modelo : SVC entrenado con píxeles normalizados a [0, 1]

    Devuelve
    --------
    digito : int
        Dígito reconocido (0 a 9).
    top3 : list de (digito, puntaje)
        Los tres dígitos con mayor puntaje de decisión. Como el SVC compara las clases de
        dos en dos (uno contra uno), el puntaje es aproximadamente el número de duelos
        ganados (máximo 9) más un pequeño ajuste por confianza. No son probabilidades.
    """
    x = np.asarray(imagen, dtype=float).reshape(1, -1) / 16.0   # misma normalización del entrenamiento
    if x.shape[1] != 64:
        raise ValueError("La imagen debe tener 64 valores (8x8 píxeles).")

    digito = int(modelo.predict(x)[0])
    puntajes = modelo.decision_function(x)[0]          # un puntaje por dígito (10 en total)
    orden = np.argsort(puntajes)[::-1][:3]
    top3 = [(int(d), float(puntajes[d])) for d in orden]
    return digito, top3


# ----- Demostración con tres imágenes del conjunto de prueba -----
plt.figure(figsize=(9, 3))
for k, idx in enumerate([0, 1, 2]):
    digito, top3 = reconocer_digito(X_test[idx] * 16)    # X_test está en [0, 1]; la función espera 0-16
    plt.subplot(1, 3, k + 1)
    plt.imshow(X_test[idx].reshape(8, 8), cmap="gray_r")
    plt.title(f"Reconocido: {digito} (real: {y_test[idx]})", fontsize=11)
    plt.axis("off")
    print(f"Imagen {idx}: reconocido {digito}; tres más probables (dígito, puntaje): "
          f"{[(d, round(p, 2)) for d, p in top3]}")
plt.tight_layout()
plt.show()
```

#### 9.12 Robustez ante el ruido

Una aplicación real recibe imágenes imperfectas. Se agrega ruido aleatorio de intensidad creciente a las imágenes de prueba (ya normalizadas a [0, 1]) y se observa cómo cae la exactitud de la SVM y de la red neuronal. La desviación estándar del ruido va de 0 (sin ruido) a 0.4, que ya es una perturbación fuerte para píxeles que valen entre 0 y 1.

```python
rng = np.random.default_rng(42)
niveles_ruido = [0, 0.05, 0.1, 0.15, 0.2, 0.3, 0.4]    # desviación estándar del ruido (píxeles en [0, 1])
exac_svm_ruido, exac_red_ruido = [], []

for sigma in niveles_ruido:
    X_ruido = np.clip(X_test + rng.normal(0, sigma, X_test.shape), 0, 1)    # mantiene el rango 0-1
    exac_svm_ruido.append(accuracy_score(y_test, mejor_modelo.predict(X_ruido)))
    exac_red_ruido.append(accuracy_score(y_test, red.predict(X_ruido)))

plt.figure(figsize=(7, 4))
plt.plot(niveles_ruido, exac_svm_ruido, "o-", label="SVM (RBF)", linewidth=2)
plt.plot(niveles_ruido, exac_red_ruido, "s--", label="Red neuronal", linewidth=2)
plt.xlabel("Intensidad del ruido (desviación estándar)")
plt.ylabel("Exactitud en prueba")
plt.title("Robustez ante el ruido", fontsize=14)
plt.grid(True, alpha=0.3)
plt.legend()
save_fig("robustez_ruido")
plt.show()

for s, a, r in zip(niveles_ruido, exac_svm_ruido, exac_red_ruido):
    print(f"ruido = {s:<4}: SVM = {a:.3f} | Red neuronal = {r:.3f}")
```

### 10. Conclusiones

La siguiente celda genera las conclusiones con los **resultados reales** obtenidos al ejecutar el notebook, sin valores escritos a mano.

```python
mejor_kernel = max(resultados_kernel, key=resultados_kernel.get)
top_total, top_i, top_j = pares[0]

print("=" * 76)
print("CONCLUSIONES")
print("=" * 76)
print(f"1. Con kernels por defecto y validación cruzada, el mejor fue '{mejor_kernel}' "
      f"({resultados_kernel[mejor_kernel]:.2%} de exactitud media).")
print(f"2. La búsqueda en malla eligió C = {busqueda.best_params_['C']} y "
      f"gamma = {busqueda.best_params_['gamma']}, con {busqueda.best_score_:.2%} en validación cruzada.")
print(f"3. En el conjunto de prueba, la SVM obtuvo {exactitud_svm:.2%} de exactitud "
      f"({len(indices_error)} errores de {len(y_test)} imágenes).")
print(f"4. La mayor confusión fue entre los dígitos {top_i} y {top_j} ({top_total} errores combinados).")
print(f"5. El modelo usa {n_soporte.sum()} vectores de soporte, el {n_soporte.sum() / len(X_train):.1%} "
      f"del entrenamiento: solo esos puntos definen la frontera.")
print(f"6. La red neuronal obtuvo {exactitud_red:.2%}; la SVM entrenó en {tiempo_svm:.3f} s y la red en {tiempo_red:.3f} s.")
print(f"7. Con el ruido más fuerte probado (desviación {niveles_ruido[-1]}), la exactitud de la SVM fue "
      f"{exac_svm_ruido[-1]:.2%} y la de la red neuronal {exac_red_ruido[-1]:.2%}.")
print()
print("Observaciones generales:")
print(" - Normalizar los píxeles y ajustar C y gamma con validación cruzada fue decisivo.")
print(" - Con pocos datos (1797 imágenes pequeñas) una SVM con kernel RBF compite bien con una red neuronal.")
print(" - Para imágenes más grandes y conjuntos muy numerosos (como Fashion MNIST), las redes")
print("   convolucionales suelen ser mejores, porque aprenden las características por sí mismas.")
```
