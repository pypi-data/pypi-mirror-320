import pyperclip


class ClipboardHelper:
    def __init__(self):
        self.methods_info = {
            "naive_matmul": "Наивное умножение матрицы на вектор, умножение матриц",
            "cache_lru": "Ииерархия памяти, план кеша и LRU, промахи в обращении к кешу.",
            "strassen": "Алгоритм Штрассена",
            "eigenvec": "Собственные векторы, собственные значения (важность, Google PageRank)",
            "shure_qr": "Разложение Шура и QR-алгоритм",
            "power_method": "Степенной метод",
            "gershkorin": "Круги Гершгорина",
            "shure_decompose": "Разложение Шура, теорема Шура",
            "matrix_norm": "Нормальные матрицы, эрмитовы матрицы, унитарно диагонализуемые матрицы, верхне-гессенбергова форма матриц.",
            "spectre": "Спектр и псевдоспектр",
            "implicit_qr": "Неявный QR алгоритм (со сдвигами).",
            "divide_rule": "Алгоритм на основе стратегии 'разделяй и властвуй'",
            "sparse_matrix": "Разреженные матрицы, форматы хранения разреженных матриц, прямые методы для решения больших разреженных систем.",
            "diff_eq": "Обыкновенные дифференциальные уравнения, задача Коши.",
            "lte_gte": "Локальная, глобальная ошибки.",
            "central_diff": "Метод центральной разности",
            "euler_method": "Метод Эйлера",
            "predictor_corrector": "Метод предиктора-корректора",
            "runge_kutta": "Метод Рунге-Кутты 1-4 порядков",
            "odu": "Точное решение ОДУ",
            "adams_multon": "Методы Адамса-Мултона, методы Адамса-Бэшфорта.",
            "milne": "Метод Милна",
            "convergence": "Согласованность, устойчивость, сходимость, условия устойчивости",
            "wave_modelling": "Моделирование волны с использованием математических инструментов (амплитуда, период, длина волны, частота, Герц, дискретизация, частота дискретизации, фаза, угловая частота).",
            "discrete_fourier": "Дискретное преобразование Фурье, обратное дискретное преобразование Фурье их ограничения, симметрии в дискретном преобразовании Фурье.",
            "fast_fourier": "Быстрое преобразование Фурье, его принципы, фильтрация сигнала с использованием быстрого преобразования Фурье.",
            "conv": "Операции свёртки, связь с быстрым преобразованием Фурье, операции дискретной свёртки.",
            "discrete_conv": "Дискретная свёртка и Тёплицевы матрицы (Ганкелевы матрицы).",
            "fourier_matrix": "Циркулянтные матрицы. Матрицы Фурье.",
            "matvec_circ": "Быстрый матвек с циркулянтом",
            "help": "Выводит справку о всех доступных методах.",
        }

    def naive_matmul(self):
        """Наивное умножение матрицы на вектор, умножение матриц"""
        code = """
import numpy as np


def naive_mat_vec(matrix, vector):
    result = [0] * len(matrix)
    for i in range(len(matrix)):
        for j in range(len(vector)):
            result[i] += matrix[i][j] * vector[j]
    return result

matrix = [[1, 2, 3],
          [4, 5, 6],
          [7, 8, 9]]

vector = [1, 0, -1]

naive_mat_vec(matrix, vector)

def naive_mat_mul(matrix1, matrix2):
    result = [[0 for _ in range(len(matrix2[0]))] for _ in range(len(matrix1))]
    for i in range(len(matrix1)):
        for j in range(len(matrix2[0])):
            for k in range(len(matrix2)):
                result[i][j] += matrix1[i][k] * matrix2[k][j]
    return result

matrix1 = [[1, 2, 3],
           [4, 5, 6],
           [7, 8, 9]]

matrix2 = [[9, 8, 7],
           [6, 5, 4],
           [3, 2, 1]]

naive_mat_mul(matrix1, matrix2)
        """
        pyperclip.copy(code)

    def cache_lru(self):
        """Ииерархия памяти, план кеша и LRU, промахи в обращении к кешу."""
        code = """
class LRUCache:
    def __init__(self, capacity: int):
        self.cache = {}
        self.capacity = capacity
        self.order = []

    def get(self, key: int) -> int:
        if key in self.cache:
            self.order.remove(key)
            self.order.append(key)
            return self.cache[key]
        return -1

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self.order.remove(key)
        elif len(self.cache) >= self.capacity:
            oldest = self.order.pop(0)
            del self.cache[oldest]
        self.cache[key] = value
        self.order.append(key)

# Пример использования
cache = LRUCache(2)
cache.put(1, 1)
cache.put(2, 2)
print(cache.get(1))    # Возвращает 1
cache.put(3, 3)        # Удаляет ключ 2 и добавляет ключ 3
print(cache.get(2))    # Возвращает -1 (не найдено)
cache.put(4, 4)        # Удаляет ключ 1 и добавляет ключ 4
print(cache.get(1))    # Возвращает -1 (не найдено)
print(cache.get(3))    # Возвращает 3
print(cache.get(4))    # Возвращает 4
"""
        pyperclip.copy(code.strip())

    def strassen(self):
        """Алгоритм Штрассена"""
        code = """
'''Алгоритм Штрассена - это эффективный метод умножения матриц, который использует 
менее O(n^3) умножений, чем наивный метод. Он особенно полезен для больших матриц.

Вот как работает алгоритм Штрассена в кратком изложении:

Разделение каждой матрицы на четыре подматрицы одинакового размера.

Применение нескольких шагов для вычисления промежуточных матриц.

Использование промежуточных матриц для получения результата.

'''
import numpy as np
import matplotlib.pyplot as plt

# Strassen's Algorithm for Matrix Multiplication
def strassen(A, B):
    if A.shape[0] == 1:
        return A * B
    
    # Split the matrices into submatrices
    n = A.shape[0] // 2
    A11, A12, A21, A22 = A[:n, :n], A[:n, n:], A[n:, :n], A[n:, n:]
    B11, B12, B21, B22 = B[:n, :n], B[:n, n:], B[n:, :n], B[n:, n:]
    
    # Strassen's 7 matrix products
    M1 = strassen(A11 + A22, B11 + B22)
    M2 = strassen(A21 + A22, B11)
    M3 = strassen(A11, B12 - B22)
    M4 = strassen(A22, B21 - B11)
    M5 = strassen(A11 + A12, B22)
    M6 = strassen(A21 - A11, B11 + B12)
    M7 = strassen(A12 - A22, B21 + B22)
    
    # Combine results into the resulting matrix
    C11 = M1 + M4 - M5 + M7
    C12 = M3 + M5
    C21 = M2 + M4
    C22 = M1 + M3 - M2 + M6
    
    # Combine submatrices into one
    C = np.vstack((np.hstack((C11, C12)), np.hstack((C21, C22))))
    return C

# Function to generate random matrices
def generate_matrices(size, low=0, high=10):
    A = np.random.randint(low, high, (size, size))
    B = np.random.randint(low, high, (size, size))
    return A, B

# Helper function to pad matrices to next power of 2
def pad_to_power_of_2(matrix):
    size = matrix.shape[0]
    next_power_of_2 = 1 << (size - 1).bit_length()
    if size == next_power_of_2:
        return matrix
    padded_matrix = np.zeros((next_power_of_2, next_power_of_2), dtype=matrix.dtype)
    padded_matrix[:size, :size] = matrix
    return padded_matrix

# Convergence Test
size = 8  # Matrix size
A, B = generate_matrices(size)

# Initialize error list
errors = []

# Test for submatrices of increasing size
for i in range(1, size + 1):
    sub_A = A[:i, :i]
    sub_B = B[:i, :i]
    
    # Pad submatrices to next power of 2 for Strassen's algorithm
    sub_A_padded = pad_to_power_of_2(sub_A)
    sub_B_padded = pad_to_power_of_2(sub_B)
    
    # Compute results
    sub_C_strassen = strassen(sub_A_padded, sub_B_padded)[:i, :i]  # Slice back to original size
    sub_C = sub_A @ sub_B  
    
    # Calculate error
    error = np.linalg.norm(sub_C_strassen - sub_C)
    errors.append(error)

# Plotting the convergence
plt.figure(figsize=(10, 6))
plt.plot(range(1, size + 1), errors, marker='o', label="Error")
plt.title("Convergence of Strassen's Algorithm")
plt.xlabel("Matrix Size (n x n)")
plt.ylabel("Error")
plt.grid()
plt.legend()
plt.show()

# Output matrices for verification
print("Matrix A:")
print(A)
print("\nMatrix B:")
print(B)
"""
        pyperclip.copy(code.strip())

    def eigenvec(self):
        """Собственные векторы, собственные значения (важность, Google PageRank)"""
        code = """
import numpy as np

# Матрица A
A = np.array([[4, 1],
              [2, 3]])

# 1. Нахождение собственных значений
# Характеристический многочлен det(A - \lambda*I) = 0
# Для 2x2 матрицы характеристическое уравнение имеет вид:
# \lambda^2 - (trace(A)) * \lambda + det(A) = 0
trace = A[0, 0] + A[1, 1]  # След матрицы

determinant = A[0, 0] * A[1, 1] - A[0, 1] * A[1, 0]  # Определитель

# Решение квадратного уравнения
# \lambda = (-b \pm sqrt(b^2 - 4ac)) / 2a
a = 1
b = -trace
c = determinant
discriminant = b**2 - 4*a*c

if discriminant < 0:
    raise ValueError("Матрица имеет комплексные собственные значения, текущая реализация не поддерживает их нахождение.")

lambda1 = (-b + discriminant**0.5) / (2 * a)
lambda2 = (-b - discriminant**0.5) / (2 * a)

eigenvalues = [lambda1, lambda2]

# 2. Нахождение собственных векторов
# Для каждого собственного значения решаем систему (A - \lambda*I)x = 0

def find_eigenvector(matrix, eigenvalue):
    size = matrix.shape[0]
    I = np.eye(size)
    B = matrix - eigenvalue * I

    # Решаем систему Bx = 0
    # Для 2x2 матрицы вручную:
    # x2 = 1 (произвольное значение)
    # x1 = -B[0, 1] / B[0, 0] (если B[0, 0] != 0)
    if B[0, 0] != 0:
        x1 = -B[0, 1] / B[0, 0]
        x2 = 1
    else:
        x1 = 1
        x2 = -B[1, 0] / B[1, 1]

    return np.array([x1, x2])

# Вычисляем собственные векторы

eigenvectors = np.array([find_eigenvector(A, eigenvalue) for eigenvalue in eigenvalues]).T

print("Собственные значения:", eigenvalues)
print("Собственные векторы:")
print(eigenvectors)


# Пример использования: Google PageRank
import numpy as np

# Матрица переходов (граф)
# Пример для 4 страниц
M = np.array([[0, 0, 1, 0],
              [1, 0, 0, 1],
              [0, 1, 0, 0],
              [0, 0, 0, 0]])

# 1. Приведение к вероятностной матрице
n = M.shape[0]
damping_factor = 0.85

# Сумма строк
row_sums = M.sum(axis=1)
G = np.zeros_like(M, dtype=float)

for i in range(n):
    if row_sums[i] == 0:
        # Если строка пуста, равномерно распределяем вероятности
        G[i, :] = 1 / n
    else:
        G[i, :] = M[i, :] / row_sums[i]

# Применяем фактор затухания
A = damping_factor * G + (1 - damping_factor) / n * np.ones((n, n))

# 2. Нахождение собственных значений и векторов
# Решаем уравнение: A * r = \lambda * r
# Где r - собственный вектор, \lambda - собственное значение

def find_eigenvector(matrix, eigenvalue):
    size = matrix.shape[0]
    I = np.eye(size)
    B = matrix - eigenvalue * I

    # Решаем систему Bx = 0
    # Для упрощения:
    # x2 = 1 (произвольное значение)
    # x1 = -B[0, 1] / B[0, 0] (если B[0, 0] != 0)
    if B[0, 0] != 0:
        x1 = -B[0, 1] / B[0, 0]
        x2 = 1
    else:
        x1 = 1
        x2 = -B[1, 0] / B[1, 1]

    return np.array([x1, x2])

eigenvalues, eigenvectors = np.linalg.eig(A)

# Находим индекс максимального собственного значения
max_eigenvalue_index = np.argmax(eigenvalues)
pagerank_vector = eigenvectors[:, max_eigenvalue_index].real

# Нормализуем собственный вектор
pagerank_vector /= pagerank_vector.sum()

print("PageRank Вектор:")
print(pagerank_vector)
        """

        pyperclip.copy(code.strip())

    def shure_qr(self):
        """Разложение Шура и QR-алгоритм"""
        code = """
'''Разложение Шура утверждает, что любую квадратную комплексную матрицу A можно разложить в произведение 
унитарной матрицы Q (Q*Q^T=I) и верхнетреугольной матрицы T - A=QTQ∗'''

'''
Метод вращения предпочтителен, когда нужно работать с симметричными матрицами и требуется высокая точность, но матрицы не слишком велики. 
Метод QR-разложения же более универсален и подходит для больших матриц, а также для решения более широкого круга задач.
'''

import numpy as np

def schur_decomposition(A, max_iterations=1000, tol=1e-10):
    n = A.shape[0]
    Ak = A.copy()
    Q_total = np.eye(n)
    for _ in range(max_iterations):
        Q, R = qr_decomposition(Ak)
        Ak = R @ Q
        Q_total = Q_total @ Q
        # Проверяем, стала ли матрица почти верхнетреугольной
        off_diagonal_norm = np.linalg.norm(np.tril(Ak, -1))
        if off_diagonal_norm < tol:
            break
    T = Ak
    Q = Q_total
    return T, Q

def qr_decomposition(A):
    n = A.shape[0]
    Q = np.eye(n)
    R = A.copy()
    for i in range(n - 1):
        # Вектор Хаусхолдера
        x = R[i:, i]
        e = np.zeros_like(x)
        e[0] = np.linalg.norm(x)
        u = x - e
        v = u / np.linalg.norm(u)
        # Матрица Хаусхолдера
        H = np.eye(n)
        H_i = np.eye(len(x)) - 2.0 * np.outer(v, v)
        H[i:, i:] = H_i
        R = H @ R
        Q = Q @ H.T
    return Q, R

A = np.array([[4, 1],
              [2, 3]], dtype=float)

T, Q = schur_decomposition(A)

print("Верхнетреугольная матрица T:")
print(T)
print("Унитарная матрица Q:")
print(Q)

'''QR-алгоритм - это метод для нахождения собственных значений матрицы путём разложения её на произведение ортогональной матрицы 
Q и верхнетреугольной матрицы R, а затем итеративного обновления:
Ak = QkRk, Ak+1 = RkQk
Ak- матрица на k-й итерации. Этот процесс продолжается до тех пор, пока Ak не станет почти верхнетреугольной.
'''

def qr_algorithm(A, max_iterations=1000, tol=1e-10):
    Ak = A.copy()
    for _ in range(max_iterations):
        Q, R = qr_decomposition(Ak)
        Ak = R @ Q
        # Проверяем сходимость диагонали
        off_diagonal_norm = np.linalg.norm(np.tril(Ak, -1))
        if off_diagonal_norm < tol:
            break
    return np.diag(Ak)

A = np.array([[4, 1, 2],
              [1, 3, 0],
              [2, 0, 2]], dtype=float)

eigenvalues = qr_algorithm(A)

print("Собственные значения матрицы:")
print(eigenvalues)
        """
        pyperclip.copy(code.strip())

    def power_method(self):
        """Степенной метод"""
        code = """
''' Степенной метод - это численный алгоритм для нахождения наибольшего по модулю собственного значения матрицы. 
Этот метод использует итеративный подход, который быстро сходится к доминирующему собственному значению и соответствующему ему собственному вектору.
Алгоритм степенного метода
Основные шаги степенного метода:
Выбираем произвольный начальный ненулевой вектор b0.
Нормализуем этот вектор.
Итеративно вычисляем bk+1=A*bk и нормализуем его.
Продолжаем итерации, пока не достигнем сходимости.
'''

import numpy as np

def custom_dot(a, b):
    if isinstance(a, np.ndarray):
        a = a.tolist()
    if isinstance(b, np.ndarray):
        b = b.tolist()

    # Handle the case where both inputs are 1D vectors
    if isinstance(a[0], (int, float)) and isinstance(b[0], (int, float)):
        return sum(x * y for x, y in zip(a, b))

    # Handle 2D * 1D or 2D * 2D multiplication
    result = []
    for row in a:
        if isinstance(b[0], list):  # b is a 2D matrix
            result_row = []
            for col in zip(*b):  # Transpose b to iterate over columns
                result_row.append(sum(x * y for x, y in zip(row, col)))
            result.append(result_row)
        else:  # b is a 1D vector
            result.append(sum(x * y for x, y in zip(row, b)))

    return result

def power_method(A, max_iterations=1000, tol=1e-10):
    b_k = np.random.rand(A.shape[1])
    
    # Нормализуем начальный вектор
    b_k = b_k / np.linalg.norm(b_k)
    
    for _ in range(max_iterations):
        b_k1 = np.dot(A, b_k)
        b_k1 = b_k1 / np.linalg.norm(b_k1)
        
        # Проверка сходимости
        if np.allclose(b_k, b_k1, atol=tol):
            break
        
        b_k = b_k1
    
    eigenvalue = custom_dot(b_k.T, np.dot(A, b_k))  
    return eigenvalue, b_k

A = np.array([[4, 1],
              [2, 3]])

eigenvalue, eigenvector = power_method(A)
print(f"Наибольшее собственное значение: {eigenvalue} Соответствующий собственный вектор{eigenvector}")
        """

        pyperclip.copy(code.strip())

    def gershkorin(self):
        """Круги Гершгорина"""
        code = """
''' Круги Гершгорина — это способ визуализации спектра квадратной матрицы.
Теорема Гершгорина утверждает, что все собственные значения матрицы находятся внутри объединения кругов Гершгорина,
определяемых следующим образом:
1. Каждый круг соответствует одной строке матрицы.
2. Центр круга — это диагональный элемент строки $A_{ii}$.
3. Радиус круга — это сумма модулей всех недиагональных элементов строки, то есть $ R_i = \sum_{j \neq i} |A_{ij}| $.
 
Геометрически это позволяет определить область на комплексной плоскости, где могут находиться собственные значения.
Если круги перекрываются, то они могут содержать общие собственные значения.
Круги Гершгорина часто используются в численном анализе и линейной алгебре для оценки спектра матрицы и анализа её свойств.'''

import numpy as np
import matplotlib.pyplot as plt

def plot_gershgorin_circles(matrix):

    n = matrix.shape[0]

    plt.figure(figsize=(8, 8))
    plt.axhline(0, color='black', linewidth=0.5, linestyle='--') 
    plt.axvline(0, color='black', linewidth=0.5, linestyle='--') 

    for i in range(n):
        center = matrix[i, i]
        radius = sum(abs(matrix[i, j]) for j in range(n) if j != i)
        
        # Рисуем круг
        circle = plt.Circle((center.real, center.imag), radius, color='b', fill=False, linestyle='--')
        plt.gca().add_artist(circle)
        plt.plot(center.real, center.imag, 'ro')

    plt.gca().set_aspect('equal', adjustable='datalim')
    plt.grid(True, linestyle='--', linewidth=0.5)
    plt.title('Круги Гершгорина')
    plt.xlabel('Re')
    plt.ylabel('Im')
    plt.show()

A = np.array([
        [4, -1, 0],
        [1, 3, 2],
        [-1, 1, 2]], dtype=complex)

plot_gershgorin_circles(A)
        """

        pyperclip.copy(code.strip())

    def shure_decompose(self):
        """Разложение Шура, теорема Шура"""
        code = """
import numpy as np

'''
Теорема Шура утверждает, что для любой квадратной матрицы A существует унитарная матрица Q и верхнетреугольная матрица T,
такие, что выполняется разложение: A = Q * T * Q^H, где Q^H — эрмитово-сопряжённая матрица Q (то есть транспонированная и комплексно-сопряжённая).
Матрица T называется шуровой формой матрицы A, и её диагональные элементы являются собственными значениями матрицы A.
Это разложение важно в численном анализе и используется для вычисления собственных значений и анализа структуры матриц.'''

import numpy as np

def schur_decomposition(A, max_iterations=1000, tol=1e-10):
    n = A.shape[0]
    Ak = A.copy()
    Q_total = np.eye(n)
    for _ in range(max_iterations):
        Q, R = qr_decomposition(Ak)
        Ak = R @ Q
        Q_total = Q_total @ Q
        # Проверяем, стала ли матрица почти верхнетреугольной
        off_diagonal_norm = np.linalg.norm(np.tril(Ak, -1))
        if off_diagonal_norm < tol:
            break
    T = Ak
    Q = Q_total
    return T, Q

def qr_decomposition(A):
    n = A.shape[0]
    Q = np.eye(n)
    R = A.copy()
    for i in range(n - 1):
        # Вектор Хаусхолдера
        x = R[i:, i]
        e = np.zeros_like(x)
        e[0] = np.linalg.norm(x)
        u = x - e
        v = u / np.linalg.norm(u)
        # Матрица Хаусхолдера
        H = np.eye(n)
        H_i = np.eye(len(x)) - 2.0 * np.outer(v, v)
        H[i:, i:] = H_i
        R = H @ R
        Q = Q @ H.T
    return Q, R


A = np.array([
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9]])

Q, T = schur_decomposition(A)
print(f"Матрица Q {Q} Матрица T(верхнетреугольная): {T} ")
print("Проверка восстановления матрицы A:", Q @ T @ Q.conj().T)
        """

        pyperclip.copy(code.strip())

    def matrix_norm(self):
        """Нормальные матрицы, эрмитовы матрицы, унитарно диагонализуемые матрицы, верхне-гессенбергова форма матриц."""
        code = """
'''
1. Нормальные матрицы
Матрица $A$ называется нормальной, если выполняется равенство:$A^HA=AA^H,$
где $A^H$ — эрмитово-сопряжённая матрица (транспонированная и комплексно-сопряжённая).
Примеры нормальных матриц включают:
Эрмитовы матрицы: $A = A^H$;
Унитарные матрицы: $A^H = A^{-1}$;
Диагональные матрицы.
2. Эрмитовы матрицы
Матрица $A$ называется эрмитовой, если A=A^H
Это означает, что она равна своей транспонированной и комплексно-сопряжённой матрице.

Свойства:
Все собственные значения эрмитовой матрицы вещественны.
Пример эрмитовой матрицы:
A=(1  2+i)
(2−i  3)

3. Унитарно диагонализуемые матрицы

Матрица $A$ называется унитарно диагонализуемой, если существует унитарная матрица $U$ (т.е. $U^H U = I$), такая что:

$A=UΛU^H$

где $\Lambda$ — диагональная матрица, содержащая собственные значения $A$.

Свойства:

Все нормальные матрицы унитарно диагонализуемы.
Применение: Унитарная диагонализация используется в квантовой механике и спектральном анализе.

4. Верхне-гессенбергова форма матриц

Матрица $A$ называется верхне-гессенберговой, если  все элементы ниже первой поддиагонали равны нулю
пример:
(1 2 3 4)
A = (5 6 7 8)
(0 9 1 2)
(0 0 3 4)
'''

#Проверка нормальности матрицы
import numpy as np

import numpy as np

def eig(matrix, max_iterations=1000, tol=1e-8):
    def power_method(A, max_iterations, tol):
        n = A.shape[1]
        b_k = np.random.rand(n)
        b_k = b_k / np.linalg.norm(b_k)  # Normalize the initial vector
        
        for _ in range(max_iterations):
            # Matrix-vector multiplication
            b_k1 = A @ b_k
            # Normalize the resulting vector
            b_k1_norm = np.linalg.norm(b_k1)
            b_k1 = b_k1 / b_k1_norm
            
            # Check for convergence
            if np.allclose(b_k, b_k1, atol=tol):
                break
            b_k = b_k1
        
        # Rayleigh quotient for eigenvalue
        eigenvalue = b_k.T @ A @ b_k
        return eigenvalue, b_k

    def deflation(A, eigenvalue, eigenvector):
        eigenvector = eigenvector.reshape(-1, 1)  
        return A - eigenvalue * (eigenvector @ eigenvector.T)

    n = matrix.shape[0]
    A = matrix.copy()
    eigenvalues = []
    eigenvectors = []

    for _ in range(n):
        eigenvalue, eigenvector = power_method(A, max_iterations, tol)
        eigenvalues.append(eigenvalue)
        eigenvectors.append(eigenvector)
        A = deflation(A, eigenvalue, eigenvector)

    return np.array(eigenvalues), np.array(eigenvectors).T


def allclose(a, b, tol=1e-8):
    return np.max(np.abs(a - b)) <= tol

def is_normal(matrix):
    left = matrix @ matrix.conj().T
    right = matrix.conj().T @ matrix
    return allclose(left, right)

A = np.array([[1, 2], [2, 1]])
print("Нормальная матрица:", is_normal(A))

#Проверка эрмитовости
def is_hermitian(matrix):
    return allclose(matrix, matrix.conj().T)


A = np.array([[1, 2 + 1j], [2 - 1j, 3]])
print("Эрмитова матрица:", is_hermitian(A))

#Унитарная диагонализация
def unitary_diagonalization(matrix):
    eigenvalues, eigenvectors = eig(matrix)
    eigenvectors = np.array(eigenvectors, dtype=np.complex128)
    for i in range(len(eigenvectors)):
        eigenvectors[:, i] /= np.linalg.norm(eigenvectors[:, i]) 
    idx = np.argsort(eigenvalues)
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]
    return eigenvectors, np.diag(eigenvalues)


A = np.array([[2, 1], [1, 2]])
U, D = unitary_diagonalization(A)
print("Унитарная матрица U:", U)
print("Диагональная матрица D:", D)


#Приведение к верхне-гессенберговой форме
def to_hessenberg_custom(matrix):
    n = len(matrix)
    H = matrix.astype(np.float64).copy()
    Q = np.eye(n)
    
    for k in range(n - 2):
        x = H[k + 1:, k]
        norm_x = np.linalg.norm(x)
        if norm_x == 0:
            continue
        r = -np.sign(x[0]) * norm_x
        u = x.copy()
        u[0] -= r
        u /= np.linalg.norm(u)

        H[k + 1:, k:] -= 2 * np.outer(u, u @ H[k + 1:, k:])
        H[:, k + 1:] -= 2 * np.outer(H[:, k + 1:] @ u, u)
        Q[k + 1:] -= 2 * np.outer(u, u @ Q[k + 1:])
    
    return H, Q.T

A = np.array([[4, 3, 2], [3, 2, 1], [2, 1, 0]])
H, Q = to_hessenberg_custom(A)
print("Верхне-гессенбергова форма H:", H)
        """

        pyperclip.copy(code.strip())

    def spectre(self):
        """Спектр и псевдоспектр"""
        code = """
'''
1. Спектр матрицы

Спектр матрицы $A \in \mathbb{C}^{n \times n}$ — это множество всех собственных значений матрицы $A$.

Определение: Собственное значение $\lambda \in \mathbb{C}$ удовлетворяет следующему уравнению:
det(A−λI)=0,
где $I$ — единичная матрица размерности $n \times n$, а $\det$ обозначает определитель.

Свойства спектра:

Собственные значения являются корнями характеристического многочлена $\det(A - \lambda I)$.
Спектр матрицы обозначается как $\sigma(A)$:
σ(A)={λ∈C:det(A−λI)=0}.
Для диагональных матриц элементы на диагонали являются собственными значениями.
Если $A$ — нормальная матрица, то её спектр совпадает с диагональными элементами её унитарной диагонализации.
2. Псевдоспектр матрицы

Псевдоспектр — это обобщение понятия спектра, полезное для анализа невозмущённой устойчивости спектра или в случае неустойчивых матриц.

Определение: $\epsilon$-псевдоспектр матрицы $A$ определяется как множество всех $\lambda \in \mathbb{C}$, таких что:

λ∈σ_ϵ(A)⟺∥(A−λI)^{−1}∥≥ 1/ϵ
где $\epsilon > 0$ и $| \cdot |$ обозначает норму матрицы (обычно спектральную норму).


Различия между спектром и псевдоспектром:

Спектр $A$ включает только собственные значения матрицы.
Псевдоспектр учитывает возмущения матрицы и позволяет анализировать её чувствительность к малым изменениям.
'''

import numpy as np
import matplotlib.pyplot as plt

# Функция для вычисления спектра
def compute_spectrum(matrix):
    return np.linalg.eigvals(matrix)

# Функция для построения псевдоспектра
def compute_pseudospectrum(matrix, epsilon, grid_size=500):
    x = np.linspace(-5, 5, grid_size)
    y = np.linspace(-5, 5, grid_size)
    X, Y = np.meshgrid(x, y)
    Z = X + 1j * Y
    pseudospectrum = np.zeros_like(Z, dtype=float)

    for i in range(grid_size):
        for j in range(grid_size):
            pseudospectrum[i, j] = np.linalg.cond(matrix - Z[i, j] * np.eye(matrix.shape[0]))

    return X, Y, pseudospectrum


A = np.array([[1, 2], [3, 4]])

spectrum = compute_spectrum(A)
print("Собственные значения матрицы A:", spectrum)

epsilon = 0.1
X, Y, pseudospectrum = compute_pseudospectrum(A, epsilon)

plt.figure(figsize=(8, 6))
plt.contourf(X, Y, np.log10(pseudospectrum), levels=50, cmap='viridis')
plt.colorbar(label='log10(cond(A - zI))')
plt.scatter(spectrum.real, spectrum.imag, color='red', label='Собственные значения')
plt.title('Псевдоспектр матрицы A')
plt.xlabel('Re')
plt.ylabel('Im')
plt.legend()
plt.grid()
plt.show()
        """

        pyperclip.copy(code.strip())

    def implicit_qr(self):
        """Неявное QR-разложение"""
        code = """
'''
Неявный qr-алгоритм имеет ряд преимуществ на явным. 
Он более производительный, имеет высокую численную устойчивость и более эффективен при обработке больших матриц. Однако он имеет недостатки - он имеет более сложное устройство и менее эффективен для работы с разреженными или структурированный матрицами
'''

import math

def qr_algorithm(A):
    m, n = len(A), len(A[0])
    Q = [[0] * m for i in range(m)]  # Инициализируем ортогональную матрицу Q нулями
    R = [[10**(-100)] * n for i in range(m)]  # Инициализируем верхнетреугольную матрицу R крайне малыми числами для избежания деления на ноль

    for j in range(n):
        # Получаем j-й столбец матрицы A
        v = [A[i][j] for i in range(m)]
        for i in range(j):
            # Вычисляем скалярное произведение столбца v и i-го столбца матрицы Q
            R[i][j] = sum(Q[k][i] * A[k][j] for k in range(m))
            # Вычитаем проекцию v на i-й столбец матрицы Q
            v = [v[k] - R[i][j] * Q[k][i] for k in range(m)]
        # Нормируем вектор v и сохраняем его в j-й столбец матрицы Q
        R[j][j] = math.sqrt(sum(v[k] * v[k] for k in range(m)))
        Q = [[v[k] / R[j][j] if j == k else Q[k][j] for j in range(n)] for k in range(m)]
    return Q, R



# Функция для вычисления сдвига
def shift(A):
    m, n = len(A), len(A[0])
    d = (A[n-2][n-2] - A[n-1][n-1]) / 2  # Разница между последними двумя диагональными элементами
    sign = 1 if d >= 0 else -1  # Определяем знак d
    # Вычисляем сдвиг mu
    mu = A[n-1][n-1] - sign * (A[n-1][n-2]**2 / (abs(d) + (d**2 + A[n-1][n-2]**2)**0.5))
    return mu

def qr_algorithm_2(A, tol=10**(-10)):

    n = len(A)  # Размер матрицы
    A = [row[:] for row in A]  # Копируем матрицу A
    num = []  # Список для хранения собственных значений

    while n > 1:
        # Пока последний элемент верхнетреугольной матрицы больше заданной точности
        while abs(A[n-1][n-2]) > tol:
            mu = shift(A)  # Вычисляем сдвиг Вилькинсона
            # Вычитаем сдвиг mu из диагональных элементов матрицы A
            A = [[A[i][j] - mu * (1 if i == j else 0) for j in range(n)] for i in range(n)]
            Q, R = qr_algorithm(A)  # Выполняем QR-разложение
            # Перемножаем R и Q, добавляя обратно сдвиг mu
            A = [[sum(R[i][k] * Q[k][j] for k in range(n)) for j in range(n)] for i in range(n)]
            A = [[A[i][j] + mu * (1 if i == j else 0) for j in range(n)] for i in range(n)]

        num.append(A[n-1][n-1])  # Добавляем собственное значение в список
        A = [row[:n-1] for row in A[:n-1]]  # Уменьшаем размер матрицы
        n -= 1

    num.append(A[0][0])  # Добавляем последнее собственное значение
    return num

# Пример
A = [[12, -51, 4],
     [6, 167, -68],
     [-4, 24, -41]]

qr_algorithm_2(A)
        """

        pyperclip.copy(code.strip())

    def divide_rule(self):
        """Стратегия разделяй и властвуй"""
        code = """
''' Стратегия "разделяй и властвуй" — это подход к проектированию алгоритмов, основанный на рекурсивном разбиении задачи на более мелкие подзадачи, решение которых затем объединяется для получения ответа на исходную задачу.


Основные этапы алгоритма:


Разделение (Divide):
Задача разбивается на несколько подзадач меньшего размера.
Каждая из них должна быть похожа по структуре на исходную задачу.


Решение подзадач (Conquer):
Каждая подзадача решается рекурсивно. Если подзадача достаточно мала, решается напрямую.


Объединение (Combine):
Результаты решения подзадач комбинируются для получения решения исходной задачи.


Примеры алгоритмов "разделяй и властвуй"


Сортировка слиянием:
Сортировка массива путём деления его на две половины, рекурсивной сортировки каждой половины и последующего их слияния.


Быстрая сортировка:
Разбиение массива на две части относительно опорного элемента и рекурсивная сортировка каждой части.'''

#Реализация: Сортировка слиянием на Python
def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return merge(left, right)

def merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    
    result.extend(left[i:])
    result.extend(right[j:])
    
    return result

arr = [38, 27, 43, 3, 9, 82, 10]
print(f"Исходный массив:{arr}\nОтсортированный массив:{merge_sort(arr)}")
"""

        pyperclip.copy(code.strip())

    def sparse_matrix(self):
        """Разреженные матрицы, форматы хранения разреженных матриц, прямые методы для решения больших разреженных систем."""
        code = """
'''
1. Разреженные матрицы


Разреженная матрица — это матрица, большая часть элементов которой равна нулю.
Для таких матриц плотность ненулевых элементов, определяемая как отношение числа 
ненулевых элементов к общему числу элементов, значительно меньше 1.


2. Форматы хранения разреженных матриц


Так как большинство элементов равны нулю, для экономии памяти используются специальные форматы хранения, которые хранят только ненулевые элементы и их индексы.

Основные форматы хранения разреженных матриц:
1)COO (Coordinate Format) - 
Хранятся три массива:
массив строк,
массив столбцов,
массив значений.


Пример:
    (0 8 0)
A = (0 0 3)
    (5 0 0)

row = [0, 1, 2], col = [1, 2, 0], data = [8, 3, 5]

2)CSR (Compressed Sparse Row):
Хранит:
массив значений,
массив индексов столбцов,
массив указателей строк.

data=[8,3,5],col_indices=[1,2,0],row_ptr=[0,1,2,3]

3)CSC (Compressed Sparse Column):
Аналогично CSR, но используется сжатие по столбцам.
Хранит:
массив значений,
массив индексов строк,
массив указателей столбцов.
4)DIA (Diagonal Format):
Используется для матриц с большим числом диагоналей.
Хранит:
массив диагоналей,
смещение каждой диагонали относительно главной.
5)LIL (List of Lists):
Каждая строка хранится как список пар (column_index, value).

Прямые методы для решения больших разреженных систем

Для решения систем линейных уравнений вида $Ax = b$, где $A$ — разреженная матрица, используются специализированные алгоритмы, которые учитывают её структуру.

Прямые методы решения:
LU-разложение для разреженных матриц:
Разложение $A = LU$, где $L$ — нижняя треугольная матрица, а $U$ — верхняя треугольная.
В отличие от обычного LU-разложения, учитывается разреженность, чтобы минимизировать дополнительное заполнение (fill-in).


Cholesky-разложение:
Применимо для симметричных положительно определённых матриц.
Разложение $A = LL^T$, где $L$ — нижняя треугольная матрица.


QR-разложение для разреженных матриц:
Разложение $A = QR$, где $Q$ — ортогональная (унитарная) матрица, а $R$ — верхняя треугольная.
Подходит для переопределённых систем (когда $A$ прямоугольная).


Метод обратного хода:
После разложения (например, LU) используется подстановка для получения решения.


Метод минимального заполнения:
Разреженные алгоритмы LU или Cholesky-разложения минимизируют заполнение матрицы ненулевыми элементами
'''

import numpy as np

def lu_decomposition_sparse(A):
    '''
    Computes LU decomposition of a sparse matrix A without fill-ins.
    A must be a square matrix.
    Returns L and U, where A = LU.
    ''''
    n = len(A)
    L = np.eye(n)  # Initialize L as the identity matrix
    U = A.copy()   # Initialize U as a copy of A

    for i in range(n):
        # Ensure pivot is not zero
        if U[i, i] == 0:
            raise ValueError("Matrix is singular or requires pivoting (not implemented).")

        for j in range(i + 1, n):
            if U[j, i] != 0:  # Check for non-zero element in the column
                factor = U[j, i] / U[i, i]
                L[j, i] = factor
                U[j, i:] -= factor * U[i, i:]  # Update row j in U

    return L, U

def forward_substitution(L, b):
    '''
    Solves Ly = b for y using forward substitution.
    L must be a lower triangular matrix.
    '''
    n = len(b)
    y = np.zeros_like(b, dtype=float)

    for i in range(n):
        y[i] = b[i] - np.dot(L[i, :i], y[:i])

    return y

def backward_substitution(U, y):
    '''
    Solves Ux = y for x using backward substitution.
    U must be an upper triangular matrix.
    '''
    n = len(y)
    x = np.zeros_like(y, dtype=float)

    for i in range(n - 1, -1, -1):
        x[i] = (y[i] - np.dot(U[i, i + 1:], x[i + 1:])) / U[i, i]

    return x


A = np.array([
        [4, 1, 0],
        [1, 4, 1],
        [0, 1, 3]
    ], dtype=float)

b = np.array([1, 2, 3], dtype=float)


L, U = lu_decomposition_sparse(A)

# Solve Ly = b
y = forward_substitution(L, b)

# Solve Ux = y
x = backward_substitution(U, y)

print("Solution x:", x)
print("L:\n", L)
print("U:\n", U)
    """

        pyperclip.copy(code.strip())

    def diff_eq(self):
        """Обыкновенные дифференциальные уравнения, задача Коши."""
        code = """
'''Обыкновенное дифференциальное уравнение — это уравнение вида:

$F(x, y, y', y'', ...., y^{(n)}) = 0$


y = y(x) - искомая функция, $y'...y^{(n)}$~— её производные, а F — заданная функция, зависящая от x, y и её производных.

Уравнение называется:


Уравнением первого порядка, если участвует только первая производная y′


Уравнением n-го порядка, если участвует $y^{(n)}$


 Задача Коши

Задача Коши для ОДУ первого порядка формулируется следующим образом:
y'(x) = f(x, y); y(x0) = y0


Решение задачи Коши заключается в нахождении функции y(x), удовлетворяющей уравнению и начальному условию.
'''
#Метод Эйлера
def euler_method(f, x0, y0, h, x_end):
    x = [x0]
    y = [y0]

    while x[-1] < x_end:
        y_new = y[-1] + h * f(x[-1], y[-1])
        x_new = x[-1] + h
        x.append(x_new)
        y.append(y_new)
    
    return x, y


f = lambda x, y: x + y  # Правая часть y'(x) = x + y
x0, y0 = 0, 1           
h = 0.1                 
x_end = 1.0             

x, y = euler_method(f, x0, y0, h, x_end)
print("Решение методом Эйлера:")
for xi, yi in zip(x, y):
    print(f"x = {xi:.2f}, y = {yi:.4f}")

#Метод Рунге-Кутты 4-го порядка

def runge_kutta_4(f, x0, y0, h, x_end):
    x = [x0]
    y = [y0]

    while x[-1] < x_end:
        k1 = h * f(x[-1], y[-1])
        k2 = h * f(x[-1] + h / 2, y[-1] + k1 / 2)
        k3 = h * f(x[-1] + h / 2, y[-1] + k2 / 2)
        k4 = h * f(x[-1] + h, y[-1] + k3)
        
        y_new = y[-1] + (k1 + 2 * k2 + 2 * k3 + k4) / 6
        x_new = x[-1] + h
        x.append(x_new)
        y.append(y_new)
    
    return x, y

x, y = runge_kutta_4(f, x0, y0, h, x_end)
print("\nРешение методом Рунге-Кутты 4-го порядка:")
for xi, yi in zip(x, y):
    print(f"x = {xi:.2f}, y = {yi:.4f}")



#Метод Эйлера прост в реализации, но может быть менее точным при большом шаге.
#Метод Рунге-Кутты 4-го порядка (RK4) является более точным, но требует больше вычислений.
"""

        pyperclip.copy(code.strip())

    def lte_gte(self):
        """Локальная, глобальная ошибки."""
        code = """
'''
Локальная ошибка — это ошибка, возникающая на одном шаге численного метода при решении задачи Коши. Она оценивает разницу между точным решением 
y(x) и приближённым решением yn на следующем шаге $x_{n+1} = x_n + h$ 


Для уравнения y'(x) = f(x, y); y(x0) = y0 локальная ошибка метода рассчитывается как LTE = $y(x_{n+1}) - y_{n+1}^*$


Глобальная ошибка — это совокупная ошибка, возникающая на всём интервале интегрирования. Она учитывает накопление ошибок, возникающих на каждом шаге численного метода.


$GTE = |y(x_n) - y_n|$

Примеры локальной и глобальной ошибки

Для метода Эйлера (первого порядка точности, p=1):

Локальная ошибка: 
LTE=O(h^2),
Глобальная ошибка:GTE=O(h).
Для метода Рунге-Кутты 4-го порядка (p=4):


Локальная ошибка: LTE=O(h^5),
Глобальная ошибка: GTE=O(h^4).
'''
"""

        pyperclip.copy(code.strip())

    def central_diff(self):
        """Метод центральной разности"""
        code = """
'''
Метод центральной разности используется для численного решения дифференциальных уравнений. Он заменяет производные функции приближёнными разностями на сетке дискретных значений.
Для первой производной y′(x) можно использовать метод центральной разности:

$y'(x) ≈ \frac{y(x+h)-y(x-h)}{2h}$

Для второй производной $y′′(x): y''(x) = \frac{y(x+h) - 2y(x)+y(x-h)}{h^2}$

h — шаг сетки
'''

import numpy as np
import matplotlib.pyplot as plt


f = lambda x: np.sin(x)
f_proiz = lambda x: np.cos(x) #производная

# Метод центральной разности
def diff(f, x, h):
    return (f(x + h) - f(x - h)) / (2 * h)


x_points = np.linspace(0, 2 * np.pi, 100)
h = 0.01  # Шаг

print(diff(f, x_points, h), f_proiz(x_points))
"""

        pyperclip.copy(code.strip())

    def euler_method(self):
        """Метод Эйлера"""
        code = """
def euler_method(f, x0, y0, h, x_end):
    x = [x0]
    y = [y0]

    while x[-1] < x_end:
        y_new = y[-1] + h * f(x[-1], y[-1])
        x_new = x[-1] + h
        x.append(x_new)
        y.append(y_new)
    
    return x, y


f = lambda x, y: x + y 
x0, y0 = 0, 1           
h = 0.1                 
x_end = 1.0             

x, y = euler_method(f, x0, y0, h, x_end)
print("Решение методом Эйлера:")
for xi, yi in zip(x, y):
    print(f"x = {xi:.2f}, y = {yi:.4f}")
        """

        pyperclip.copy(code.strip())

    def predictor_corrector(self):
        """Метод предиктора-корректора"""
        code = """
'''
Метод предиктора-корректора — это численный метод для решения обыкновенных дифференциальных уравнений (ОДУ). Он относится к группе многошаговых методов и сочетает преимущества эксплицитных (явных) и имплицитных (неявных) методов.

Основная идея метода заключается в использовании двух стадий:

Предиктор — вычисление приближённого значения решения на новом шаге с использованием явного метода.

Корректор — уточнение результата с помощью неявного метода на основе предсказанного значения.

Формулировка метода

Рассмотрим задачу Коши:

y′(x)=f(x,y),y(x0)=y0

Метод предиктора-корректора выполняется в два этапа:

Шаг предиктора (явный метод):
Используется для предсказания значения y_{n+1}^P на новом шаге:

$y_{n+1}^P=y_n+h⋅Φ(x_n,y_n)$ где Φ — некоторая функция, зависящая от f(x,y).

Шаг корректора (неявный метод):
Уточняется значение y_{n+1} на основе формулы:

$y_{n+1}=y_n+h⋅Ψ(x_{n+1},y_{n+1},x_n,y_n)$
где Ψ — корректирующая функция, зависящая как от текущего шага, так и от предыдущих данных.

Применение

Метод предиктора-корректора применяется для решения:

Обыкновенных дифференциальных уравнений.
Систем ОДУ, где требуются относительно точные решения на длинных интервалах.
Задач, где важно найти баланс между точностью и вычислительными затратами.
'''

import numpy as np
import matplotlib.pyplot as plt

# Правая часть ОДУ: y'(x) = f(x, y)
def f(x, y):
    return x + y

# Метод предиктора-корректора
def predictor_corrector(f, x0, y0, h, x_end):
    # Сетка значений x
    x = np.arange(x0, x_end + h, h)
    y = np.zeros(len(x))  # Массив значений y
    y[0] = y0            # Начальное условие

    # Основной цикл
    for n in range(len(x) - 1):
        # Предиктор: явный метод Эйлера
        y_predict = y[n] + h * f(x[n], y[n])
        
        # Корректор: метод трапеций
        y[n+1] = y[n] + (h / 2) * (f(x[n], y[n]) + f(x[n+1], y_predict))
    
    return x, y


x0, y0 = 0, 1   
h = 0.1         
x_end = 1.0     

x, y = predictor_corrector(f, x0, y0, h, x_end)

# Точное решение для сравнения
exact_solution = lambda x: -x - 1 + 2 * np.exp(x)
y_exact = exact_solution(x)

# Вывод результатов
plt.plot(x, y, label="Предиктор-корректор", marker='o')
plt.plot(x, y_exact, label="Точное решение", linestyle="--")
plt.xlabel("x")
plt.ylabel("y")
plt.title("Метод предиктора-корректора")
plt.legend()
plt.grid(True)
plt.show()

# Ошибка
error = np.abs(y_exact - y)
print("Максимальная ошибка:", np.max(error))
        """

        pyperclip.copy(code.strip())

    def odu(self):
        """ОДУ – Точное решение уравнений и систем"""
        code = """
# Решение уравнения
import sympy as sp
from sympy import Function, dsolve, Eq, Derivative, symbols, exp

x = symbols('x')
y = Function('y')

ode = Eq(Derivative(y(x), x), x + y(x))

ics = {y(0): 1}

solution = dsolve(ode, y(x), ics=ics)

print("Точное решение ОДУ:")
print(solution)

import numpy as np

y_exact = sp.lambdify(x, solution.rhs, modules=['numpy'])

print(f"y(1) = {y_exact(1)}")

# Решение системы
import sympy as sp
from sympy import Function, dsolve, Eq, Derivative, symbols, simplify

t = symbols('t')

x = Function('x')(t)
y = Function('y')(t)

ode1 = Eq(Derivative(x, t), 3*x + 4*y)
ode2 = Eq(Derivative(y, t), -4*x + 3*y)

ics = {x.subs(t, 0): 1, y.subs(t, 0): 0}

solution = dsolve([ode1, ode2], [x, y], ics=ics)

for sol in solution:
    print(sol)

# Решение системы с визуализацией
import sympy as sp
from sympy import Function, dsolve, Eq, Derivative, symbols, solve, exp
import numpy as np
import matplotlib.pyplot as plt

t = symbols('t')

x = Function('x')(t)
y = Function('y')(t)
z = Function('z')(t)

ode1 = Eq(Derivative(x, t), 2*x + 3*y)
ode2 = Eq(Derivative(y, t), -x + 4*y)
ode3 = Eq(Derivative(z, t), z)

ics = {x.subs(t, 0): 1, y.subs(t, 0): 0, z.subs(t, 0): 2}

solution = dsolve([ode1, ode2, ode3], [x, y, z], ics=ics)

x_sol = solution[0].rhs
y_sol = solution[1].rhs
z_sol = solution[2].rhs

x_num = sp.lambdify(t, x_sol, 'numpy')
y_num = sp.lambdify(t, y_sol, 'numpy')
z_num = sp.lambdify(t, z_sol, 'numpy')

t_vals = np.linspace(0, 2, 400)

x_vals = x_num(t_vals)
y_vals = y_num(t_vals)
z_vals = z_num(t_vals)

plt.figure(figsize=(10, 6))
plt.plot(t_vals, x_vals, label='x(t)')
plt.plot(t_vals, y_vals, label='y(t)')
plt.plot(t_vals, z_vals, label='z(t)')
plt.xlabel('t')
plt.ylabel('Значение функции')
plt.title('Решения системы ОДУ')
plt.legend()
plt.grid(True)
plt.show()
"""
        pyperclip.copy(code)

    def runge_kutta(self):
        """Метод Рунге-Кутты"""
        code = """
'''
1. Метод Рунге-Кутты 1-го порядка (Метод Эйлера)
Метод Эйлера — это самый простой метод Рунге-Кутты: $y_{n+1} = y_n + h*f(xn, yn)$
Он имеет первый порядок точности $O(h^2)$ и подходит для грубых приближений.

Метод Рунге-Кутты 2-го порядка
Метод второго порядка точности использует среднее значение производной между двумя точками:
$k1 = f(x_n, y_n)

k2=f(x_n+h, y_n+h*k_1)

y_{n+1} = y_n + h/2*(k1+k2)$

Метод Рунге-Кутты 3-го порядка
Для повышения точности используется три промежуточных значения:

$k1 = f(x_n, y_n)

k2=f(x_n+h/2, y_n+h/2*k_1)

k3=f(x_n+h, y_n-h*k_1 + 2h*k_2)

y_{n+1} = y_n + h/6*(k1+4k2+k3)$

Метод Рунге-Кутты 4-го порядка 

Метод четвёртого порядка — наиболее популярный вариант из-за баланса между точностью и вычислительной сложностью.

$k1 = f(x_n, y_n)

k2=f(x_n+h/2, y_n+h/2*k_1)

k2=f(x_n+h/2, y_n+h/2*k_2)

k4=f(x_n+h, y_n+h*k_3)

y_{n+1} = y_n + h/6*(k1+2k2+2k3+k4)$

Он имеет порядок точности $O(h^5)$.
'''

import numpy as np
import matplotlib.pyplot as plt


def f(x, y):
    return x + y


def runge_kutta(f, x0, y0, h, x_end, order=4):
    x = np.arange(x0, x_end + h, h)
    y = np.zeros(len(x))  
    y[0] = y0           

    for n in range(len(x) - 1):
        if order == 1:  # Метод Эйлера
            k1 = f(x[n], y[n])
            y[n+1] = y[n] + h * k1

        elif order == 2:  # Метод Рунге-Кутты 2-го порядка
            k1 = f(x[n], y[n])
            k2 = f(x[n] + h, y[n] + h * k1)
            y[n+1] = y[n] + (h / 2) * (k1 + k2)

        elif order == 3:  # Метод Рунге-Кутты 3-го порядка
            k1 = f(x[n], y[n])
            k2 = f(x[n] + h / 2, y[n] + h / 2 * k1)
            k3 = f(x[n] + h, y[n] - h * k1 + 2 * h * k2)
            y[n+1] = y[n] + (h / 6) * (k1 + 4 * k2 + k3)

        elif order == 4:  # Метод Рунге-Кутты 4-го порядка
            k1 = f(x[n], y[n])
            k2 = f(x[n] + h / 2, y[n] + h / 2 * k1)
            k3 = f(x[n] + h / 2, y[n] + h / 2 * k2)
            k4 = f(x[n] + h, y[n] + h * k3)
            y[n+1] = y[n] + (h / 6) * (k1 + 2 * k2 + 2 * k3 + k4)

    return x, y


x0, y0 = 0, 1  
h = 0.1         
x_end = 1.0     

x, y_rk1 = runge_kutta(f, x0, y0, h, x_end, order=1)  
_, y_rk2 = runge_kutta(f, x0, y0, h, x_end, order=2)  
_, y_rk3 = runge_kutta(f, x0, y0, h, x_end, order=3)  
_, y_rk4 = runge_kutta(f, x0, y0, h, x_end, order=4)  

# Точное решение
exact_solution = lambda x: -x - 1 + 2 * np.exp(x)
y_exact = exact_solution(x)

# Графики решений
plt.plot(x, y_exact, label="Точное решение", linestyle="--", color="black")
plt.plot(x, y_rk1, label="Метод Эйлера (RK1)", marker='o')
plt.plot(x, y_rk2, label="Рунге-Кутта 2-го порядка (RK2)", marker='x')
plt.plot(x, y_rk3, label="Рунге-Кутта 3-го порядка (RK3)", marker='s')
plt.plot(x, y_rk4, label="Рунге-Кутта 4-го порядка (RK4)", marker='d')
plt.xlabel("x")
plt.ylabel("y")
plt.title("Методы Рунге-Кутты 1-4 порядков")
plt.legend()
plt.grid(True)
plt.show()

# Вывод ошибок
print("Максимальные ошибки:")
print(f"Метод Эйлера (RK1): {np.max(np.abs(y_exact - y_rk1))}")
print(f"Рунге-Кутта 2-го порядка (RK2): {np.max(np.abs(y_exact - y_rk2))}")
print(f"Рунге-Кутта 3-го порядка (RK3): {np.max(np.abs(y_exact - y_rk3))}")
print(f"Рунге-Кутта 4-го порядка (RK4): {np.max(np.abs(y_exact - y_rk4))}")
        """

        pyperclip.copy(code.strip())

    def runge_kutta_system(self):
        """Метод Рунге-Кутта (система)"""
        code = """
import numpy as np
import matplotlib.pyplot as plt

def runge_kutta_system(f, x0, y0, h, x_end, order=4):
    x = np.arange(x0, x_end + h, h)
    y = np.zeros((len(x), len(y0)))
    y[0] = y0

    for n in range(len(x) - 1):
        if order == 1:  # РК1
            k1 = f(x[n], y[n])
            y[n+1] = y[n] + h * k1

        elif order == 2:  # РК2
            k1 = f(x[n], y[n])
            k2 = f(x[n] + h/2, y[n] + h/2 * k1)
            y[n+1] = y[n] + h * k2

        elif order == 3:  # РК3
            k1 = f(x[n], y[n])
            k2 = f(x[n] + h/2, y[n] + h/2 * k1)
            k3 = f(x[n] + h, y[n] - h * k1 + 2 * h * k2)
            y[n+1] = y[n] + (h / 6) * (k1 + 4 * k2 + k3)

        elif order == 4:  # РК4
            k1 = f(x[n], y[n])
            k2 = f(x[n] + h/2, y[n] + h/2 * k1)
            k3 = f(x[n] + h/2, y[n] + h/2 * k2)
            k4 = f(x[n] + h, y[n] + h * k3)
            y[n+1] = y[n] + (h / 6) * (k1 + 2*k2 + 2*k3 + k4)

    return x, y

# Пример системы ОДУ:
# dx/dt = 3x + 4y
# dy/dt = -4x + 3y

def system(t, Y):
    x, y = Y
    dxdt = 3*x + 4*y
    dydt = -4*x + 3*y
    return np.array([dxdt, dydt])

# Параметры
x0 = 0
y0 = np.array([1, 0])  # Начальные условия: x(0)=1, y(0)=0
h = 0.1
x_end = 1.0

# Решение РК1-4
x, Y_rk1 = runge_kutta_system(system, x0, y0, h, x_end, order=1)
_, Y_rk2 = runge_kutta_system(system, x0, y0, h, x_end, order=2)
_, Y_rk3 = runge_kutta_system(system, x0, y0, h, x_end, order=3)
_, Y_rk4 = runge_kutta_system(system, x0, y0, h, x_end, order=4)

# Точное решение
exact_solution_x = lambda t: (np.exp(3*t) * (np.cos(5*t) + np.sin(5*t)))
exact_solution_y = lambda t: (np.exp(3*t) * (-np.sin(5*t) + np.cos(5*t)))

y_exact_x = exact_solution_x(x)
y_exact_y = exact_solution_y(x)

# Графики для x
plt.plot(x, y_exact_x, label="Точное решение x(t)", linestyle="--", color="black")
plt.plot(x, Y_rk1[:,0], label="РК1 x(t)", marker='o')
plt.plot(x, Y_rk2[:,0], label="РК2 x(t)", marker='x')
plt.plot(x, Y_rk3[:,0], label="РК3 x(t)", marker='s')
plt.plot(x, Y_rk4[:,0], label="РК4 x(t)", marker='d')
plt.xlabel("t")
plt.ylabel("x(t)")
plt.title("Методы Рунге-Кутты I-IV порядков для системы ОДУ (x)")
plt.legend()
plt.grid(True)
plt.show()

# Графики для y
plt.plot(x, y_exact_y, label="Точное решение y(t)", linestyle="--", color="black")
plt.plot(x, Y_rk1[:,1], label="РК1 y(t)", marker='o')
plt.plot(x, Y_rk2[:,1], label="РК2 y(t)", marker='x')
plt.plot(x, Y_rk3[:,1], label="РК3 y(t)", marker='s')
plt.plot(x, Y_rk4[:,1], label="РК4 y(t)", marker='d')
plt.xlabel("t")
plt.ylabel("y(t)")
plt.title("Методы Рунге-Кутты I-IV порядков для системы ОДУ (y)")
plt.legend()
plt.grid(True)
plt.show()

# Вывод ошибок
error_rk1 = np.max(np.abs(y_exact_x - Y_rk1[:,0]))
error_rk2 = np.max(np.abs(y_exact_x - Y_rk2[:,0]))
error_rk3 = np.max(np.abs(y_exact_x - Y_rk3[:,0]))
error_rk4 = np.max(np.abs(y_exact_x - Y_rk4[:,0]))
print("Максимальные ошибки для x(t):")
print(f"РК1: {error_rk1}")
print(f"РК2: {error_rk2}")
print(f"РК3: {error_rk3}")
print(f"РК4: {error_rk4}")

error_rk1_y = np.max(np.abs(y_exact_y - Y_rk1[:,1]))
error_rk2_y = np.max(np.abs(y_exact_y - Y_rk2[:,1]))
error_rk3_y = np.max(np.abs(y_exact_y - Y_rk3[:,1]))
error_rk4_y = np.max(np.abs(y_exact_y - Y_rk4[:,1]))
print("\nМаксимальные ошибки для y(t):")
print(f"РК1: {error_rk1_y}")
print(f"РК2: {error_rk2_y}")
print(f"РК3: {error_rk3_y}")
print(f"РК4: {error_rk4_y}")
"""

        pyperclip.copy(code)

    def adams_multon(self):
        """Метод Адамса-Мультона"""
        code = """
'''
Методы Адамса-Бэшфорта (явные)
Методы Адамса-Бэшфорта используют только значения f(x,y) из предыдущих шагов и относятся к явным методам. Формула p-го порядка имеет вид

$y_{n+1} = y_n + h*\Sigma_{k=0}^{p-1}\beta_kf(x_{n-k}, y_{n-k})$

$\beta_k$ — коэффициенты метода, зависящие от порядка p

Методы Адамса-Мултона (неявные)
Методы Адамса-Мултона являются имплицитными и используют значения f(x,y) как из предыдущих шагов, так и на текущем шаге. Формула p-го порядка:

$y_{n+1} = y_n + h*\Sigma_{k=0}^{p}\alpha_kf(x_{n-k+1}, y_{n-k+1})$

$\alpha_k$ — коэффициенты метода, зависящие от порядка p

Часто методы Адамса-Бэшфорта и Адамса-Мултона применяются вместе в составе схемы предиктора-корректора
'''
import numpy as np
import matplotlib.pyplot as plt

# Правая часть ОДУ: y'(x) = f(x, y)
def f(x, y):
    return x + y

# Метод Адамса-Бэшфорта 2-го порядка
def adams_bashforth(f, x0, y0, h, x_end):
    # Сетка значений x
    x = np.arange(x0, x_end + h, h)
    y = np.zeros(len(x))
    y[0] = y0  # Начальное условие
    
    # Первое значение находим методом Эйлера
    y[1] = y[0] + h * f(x[0], y[0])
    
    # Основной цикл
    for n in range(1, len(x) - 1):
        y[n+1] = y[n] + h * (1.5 * f(x[n], y[n]) - 0.5 * f(x[n-1], y[n-1]))
    
    return x, y

# Метод Адамса-Мултона 2-го порядка
def adams_moulton(f, x0, y0, h, x_end):
    # Сетка значений x
    x = np.arange(x0, x_end + h, h)
    y = np.zeros(len(x))
    y[0] = y0  # Начальное условие
    
    # Первое значение находим методом Эйлера
    y[1] = y[0] + h * f(x[0], y[0])
    
    # Основной цикл
    for n in range(1, len(x) - 1):
        # Предиктор: метод Адамса-Бэшфорта
        y_predict = y[n] + h * (1.5 * f(x[n], y[n]) - 0.5 * f(x[n-1], y[n-1]))
        # Корректор: метод Адамса-Мултона
        y[n+1] = y[n] + (h / 2) * (f(x[n], y[n]) + f(x[n+1], y_predict))
    
    return x, y

# Параметры задачи
x0, y0 = 0, 1   # Начальные условия
h = 0.1         # Шаг интегрирования
x_end = 1.0     # Конец интервала

# Решение методами Адамса
x, y_ab = adams_bashforth(f, x0, y0, h, x_end)
_, y_am = adams_moulton(f, x0, y0, h, x_end)

# Точное решение
exact_solution = lambda x: -x - 1 + 2 * np.exp(x)
y_exact = exact_solution(x)

# Графики решений
plt.plot(x, y_exact, label="Точное решение", linestyle="--", color="black")
plt.plot(x, y_ab, label="Адамс-Бэшфорт (2-й порядок)", marker='o')
plt.plot(x, y_am, label="Адамс-Мултон (2-й порядок)", marker='x')
plt.xlabel("x")
plt.ylabel("y")
        """

        pyperclip.copy(code.strip())

    def milne(self):
        """Метод Милна"""
        code = """
'''
Метод Милна — это многошаговый численный метод решения обыкновенных дифференциальных уравнений (ОДУ). Он используется для приближённого вычисления значений функции y(x) в задаче Коши:

$y'(x) = f(x, y); y(x_0)=y_0$

Метод Милна относится к явно-неявным методам и состоит из двух этапов:

Предиктор (явная формула): вычисляет приближённое значение $y_{n+1} = y_{n-3} + 4h/3(2f(x_n, y_n)-f(x_{n-1}, y_{n-1})+2f(x_{n-2}, y_{n-2}))$

Корректор (неявная формула): уточняет это значение.  $y_{n+1} = y_{n-1} + h/3(f(x_{n+1}, y_{n+1})+4f(x_n, y_n)+f(x_{n-1}, y_{n-1}))$

Шаги метода Милна
1.Для начала расчёта требуется значение y и f(x,y) в четырёх точках (y0,y1,y2,y3)
 Эти значения можно получить любым одношаговым методом (например, методом Рунге-Кутты).
2.Вычисляется предсказанное значение $y_{n+1}$ с помощью предиктора.
3.Вычисляется уточнённое значение $y_{n+1}$с помощью корректора.
4.Шаги повторяются для всех последующих точек.

'''

import numpy as np
import matplotlib.pyplot as plt

# Правая часть ОДУ: y'(x) = f(x, y)
def f(x, y):
    return x + y

# Метод Милна
def milne_method(f, x0, y0, h, x_end):
    # Сетка значений x
    x = np.arange(x0, x_end + h, h)
    n_points = len(x)
    
    y = np.zeros(n_points)  # Массив значений y
    y[0] = y0              # Начальное условие
    
    # Инициализация первых четырёх значений методом Рунге-Кутты 4-го порядка
    def runge_kutta_step(f, x, y, h):
        k1 = f(x, y)
        k2 = f(x + h / 2, y + h / 2 * k1)
        k3 = f(x + h / 2, y + h / 2 * k2)
        k4 = f(x + h, y + h * k3)
        return y + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
    
    for i in range(3):
        y[i+1] = runge_kutta_step(f, x[i], y[i], h)
    
    # Основной цикл
    for n in range(3, n_points - 1):
        # Предикторная формула
        y_pred = y[n-3] + (4 * h / 3) * (2 * f(x[n], y[n]) - f(x[n-1], y[n-1]) + 2 * f(x[n-2], y[n-2]))
        
        # Корректорная формула
        y_corr = y[n-1] + (h / 3) * (f(x[n+1], y_pred) + 4 * f(x[n], y[n]) + f(x[n-1], y[n-1]))
        
        # Итеративное уточнение
        y[n+1] = y_corr
    
    return x, y

# Параметры задачи
x0, y0 = 0, 1   # Начальные условия
h = 0.1         # Шаг интегрирования
x_end = 1.0     # Конец интервала

# Решение методом Милна
x, y_milne = milne_method(f, x0, y0, h, x_end)

# Точное решение
exact_solution = lambda x: -x - 1 + 2 * np.exp(x)
y_exact = exact_solution(x)

# Графики решений
plt.plot(x, y_exact, label="Точное решение", linestyle="--", color="black")
plt.plot(x, y_milne, label="Метод Милна", marker='o')
plt.xlabel("x")
plt.ylabel("y")
plt.title("Метод Милна")
plt.legend()
plt.grid(True)
plt.show()

# Вывод ошибки
print("Максимальная ошибка метода Милна:", np.max(np.abs(y_exact - y_milne)))
        """

        pyperclip.copy(code.strip())

    def convergence(self):
        """Согласованность, устойчивость, сходимость, условия устойчивости"""
        code = """
'''
Численные методы для решения обыкновенных дифференциальных уравнений (ОДУ) оцениваются по трём ключевым свойствам: согласованность, устойчивость и сходимость. Эти свойства обеспечивают, что численное решение будет близко к точному решению задачи Коши.

Численный метод называется согласованным с исходным дифференциальным уравнением, если локальная погрешность метода стремится к нулю при h -> 0

Локальная погрешность — это ошибка, возникающая на одном шаге метода при предположении, что предыдущие значения известны точно. Для численного метода $τ(h) = \frac{y_{n+1} - y(t_{n+1})}{h}$ Метод согласован, если $lim_{h->0}τ(h)=0$

Устойчивость — это свойство численного метода сохранять ограниченность решения при наличии ошибок округления или начальных условий.

Численная устойчивость:

Метод устойчив, если численное решение yn остаётся ограниченным при любом конечном интервале времени [0,T] и при любых малых возмущениях исходных данных.

Сходимость численного метода
Численный метод называется сходящимся, если приближённое решение yn стремится к точному решению y(tn) задачи Коши при h→0. 

$lim_{h->0}max_{0<=n<=N}|yn - y(tn)|=0$

N - число шагов на интервале интегрирования.

Теорема Лакса о сходимости: Численный метод сходится, если он согласован и устойчив.

4. Условия устойчивости

Необходимое условие устойчивости: Метод должен сохранять ограниченность численного решения при малых возмущениях начальных условий.

Достаточное условие устойчивости: Для обеспечения устойчивости метод должен сохранять решение в пределах области абсолютной устойчивости, которая определяется параметром z=λh

'''

import numpy as np
import matplotlib.pyplot as plt

# Определяем тестовое уравнение y'(x) = λy(x)
lambda_value = -2  # Пример значения λ (отрицательное для проверки устойчивости)

# Аналитическое решение тестового уравнения
def exact_solution(x, y0, lambda_value):
    return y0 * np.exp(lambda_value * x)

# Численный метод: Явный метод Эйлера
def explicit_euler_step(y, h, f):
    return y + h * f(y)

# Определяем функцию производной f(y)
def f(y):
    return lambda_value * y

# Проверка согласованности: локальная ошибка
def check_consistency():
    h_values = np.logspace(-4, -1, 10)  # Шаги h для проверки (от маленьких до больших)
    errors = []
    for h in h_values:
        # Точное решение в следующей точке
        y_exact = exact_solution(h, y0=1, lambda_value=lambda_value)
        # Численное решение с использованием одного шага метода
        y_approx = explicit_euler_step(1, h, f)
        # Локальная ошибка
        local_error = abs(y_exact - y_approx)
        errors.append(local_error)
    # Построение графика
    plt.loglog(h_values, errors, marker='o', label="Локальная ошибка")
    plt.loglog(h_values, h_values, linestyle='--', label="$O(h)$")
    plt.xlabel("Шаг (h)")
    plt.ylabel("Локальная ошибка")
    plt.title("Проверка согласованности: локальная ошибка от шага")
    plt.legend()
    plt.grid()
    plt.show()

# Проверка устойчивости: область абсолютной устойчивости
def check_stability():
    # Условие устойчивости для явного метода Эйлера: |1 + hλ| <= 1
    h_values = np.linspace(0, 2, 100)
    stability = [abs(1 + h * lambda_value) for h in h_values]
    # Построение графика
    plt.plot(h_values, stability, label="|1 + hλ|")
    plt.axhline(1, color='r', linestyle='--', label="Порог устойчивости")
    plt.xlabel("Шаг (h)")
    plt.ylabel("|1 + hλ|")
    plt.title("Проверка устойчивости для явного метода Эйлера")
    plt.legend()
    plt.grid()
    plt.show()

# Проверка сходимости: глобальная ошибка
def check_convergence():
    h_values = np.logspace(-4, -1, 10)  # Шаги h для проверки
    errors = []
    for h in h_values:
        x_end = 1  # Конечная точка интервала (интегрируем до x = 1)
        n_steps = int(x_end / h)  # Количество шагов
        x = 0
        y = 1  # Начальное условие
        for _ in range(n_steps):
            y = explicit_euler_step(y, h, f)
            x += h
        # Точное решение в конечной точке
        y_exact = exact_solution(x_end, y0=1, lambda_value=lambda_value)
        # Глобальная ошибка
        global_error = abs(y_exact - y)
        errors.append(global_error)
    # Построение графика
    plt.loglog(h_values, errors, marker='o', label="Глобальная ошибка")
    plt.loglog(h_values, h_values, linestyle='--', label="$O(h)$")
    plt.xlabel("Шаг (h)")
    plt.ylabel("Глобальная ошибка")
    plt.title("Проверка сходимости: глобальная ошибка от шага")
    plt.legend()
    plt.grid()
    plt.show()

# Запуск проверок
print("Проверка согласованности...")
check_consistency()

print("Проверка устойчивости...")
check_stability()

print("Проверка сходимости...")
check_convergence()
        """

        pyperclip.copy(code.strip())

    def wave_modelling(self):
        """Моделирование волны с использованием математических инструментов (амплитуда, период, длина волны, частота, Герц, дискретизация, частота дискретизации, фаза, угловая частота)."""
        code = """
'''
Амплитуда (A): Максимальное отклонение волны от среднего значения (равновесного положения).

Период (T): Время, за которое волна совершает один полный цикл. Связан с частотой как 1/f; f-Частота

Частота (f): Количество колебаний в секунду (в герцах, Гц)

Угловая частота (ω): Частота в радианах в секунду

Длина волны (λ): Расстояние, которое волна проходит за один период

Фаза (ϕ): Смещение волны во времени или пространстве. Измеряется в радианах. y(t) = A*sin(ωt+ϕ)

Частота дискретизации ($f_s$): Частота, с которой аналоговый сигнал дискретизируется для численного моделирования.
'''

import numpy as np
import matplotlib.pyplot as plt

# Параметры волны
A = 1.0          # Амплитуда
f = 5.0          # Частота (Гц)
T = 1 / f        # Период
omega = 2 * np.pi * f  # Угловая частота
phi = np.pi / 4  # Фаза (в радианах)
v = 343          # Скорость распространения (например, звук в воздухе, м/с)
lambda_wave = v / f  # Длина волны

# Параметры дискретизации
f_s = 1000       # Частота дискретизации (Гц)
t = np.linspace(0, 2 * T, int(2 * T * f_s))  # Массив времени (2 периода)

# Моделирование волны
y = A * np.sin(omega * t + phi)

# Визуализация
plt.figure(figsize=(10, 6))
plt.plot(t, y, label="Синусоидальная волна")
plt.axhline(0, color='black', linewidth=0.8, linestyle='--')  # Ось x
plt.title("Синусоидальная волна")
plt.xlabel("Время (с)")
plt.ylabel("Амплитуда")
plt.grid(True)
plt.legend()
plt.show()
        """

        pyperclip.copy(code.strip())

    def discrete_fourier(self):
        """Дискретное преобразование Фурье, обратное дискретное преобразование Фурье их ограничения, симметрии в дискретном преобразовании Фурье."""
        code = """
        '''
Дискретное преобразование Фурье (ДПФ) — это математический инструмент, который используется для анализа частотного содержания сигналов, представленных в виде дискретных точек. Оно преобразует сигнал из временной области в частотную область.

ДПФ преобразует последовательность x[n] длиной N (дискретный сигнал) в комплексный спектр $X[k]= \Sigma_{n=0}^{N-1}x[n]e^{-j\frac{2\pi}{N}kn}$

X[k] — спектральные коэффициенты, представляющие амплитуду и фазу частоты k

x[n] — значения временного сигнала

N — количество точек.

Обратное дискретное преобразование Фурье (ОДПФ):

ОДПФ восстанавливает временной сигнал из частотного представления:

$X[k]= \Sigma_{k=0}^{N-1}X[k]e^{j\frac{2\pi}{N}kn}$

Ограничения ДПФ:

Ограниченная длина:
ДПФ работает только с конечными сигналами длиной N. Для бесконечных сигналов требуется оконное преобразование.

Разрешение частот: зависит от длины сигнала. Чем больше N, тем лучше разрешение частот.

Эффект наложения (aliasing):
Если частота дискретизации fs меньше, чем удвоенная максимальная частота сигнала (fmax), высокие частоты могут наложиться на низкие.

Выходные данные комплексные:
Результат X[k] включает как амплитуду, так и фазу, что может быть сложным для интерпретации.

Ограничение временной области:
При анализе конечного сигнала возможны утечки спектра (spectral leakage), что требует оконных функций для сглаживания.

Симметрии в ДПФ:
Для сигналов, которые являются действительными (реальными числами):

Симметрия спектра:
X[k]=X*[N−k],k=1,2,…,N/2−1,
где X*— комплексно-сопряжённое значение.

Амплитуда симметрична:
∣X[k]∣=∣X[N−k]∣.

Фаза антисимметрична:
∠X[k]=−∠X[N−k].
        '''
import math
import matplotlib.pyplot as plt

# Параметры сигнала
N = 64  # Длина сигнала (дискретизация)
f1 = 5  # Частота первого синуса (Гц)
f2 = 10 # Частота второго синуса (Гц)
fs = 64 # Частота дискретизации (Гц)
T = 1 / fs  # Шаг дискретизации (с)

# Генерация временного сигнала
t = [n * T for n in range(N)]  # Временной вектор
x = [math.sin(2 * math.pi * f1 * tn) + 0.5 * math.sin(2 * math.pi * f2 * tn) for tn in t]  # Сигнал: сумма двух синусов

# Вычисление ДПФ
X = []  # Спектральные коэффициенты
for k in range(N):
    real = 0
    imag = 0
    for n in range(N):
        angle = -2 * math.pi * k * n / N
        real += x[n] * math.cos(angle)
        imag += x[n] * math.sin(angle)
    X.append(complex(real, imag))

# Вычисление частот
frequencies = [k / (N * T) for k in range(N)]

# Амплитудный спектр
amplitude = [abs(Xk) / N for Xk in X]

# Восстановление сигнала с помощью ОДПФ
x_reconstructed = []
for n in range(N):
    real = 0
    for k in range(N):
        angle = 2 * math.pi * k * n / N
        real += (X[k].real * math.cos(angle) - X[k].imag * math.sin(angle)) / N
    x_reconstructed.append(real)

# Визуализация
plt.figure(figsize=(12, 6))

# Оригинальный сигнал
plt.subplot(2, 2, 1)
plt.plot(t, x, label="Оригинальный сигнал")
plt.xlabel("Время (с)")
plt.ylabel("Амплитуда")
plt.title("Оригинальный временной сигнал")
plt.grid()
plt.legend()

# Амплитудный спектр
plt.subplot(2, 2, 2)
plt.stem(frequencies[:N // 2], amplitude[:N // 2], basefmt=" ")  # Отображение половины спектра
plt.xlabel("Частота (Гц)")
plt.ylabel("Амплитуда")
plt.title("Амплитудный спектр")
plt.grid()

# Сравнение сигнала до и после ОДПФ
plt.subplot(2, 1, 2)
plt.plot(t, x, label="Оригинальный сигнал")
plt.plot(t, x_reconstructed, linestyle="--", label="Восстановленный сигнал")
plt.xlabel("Время (с)")
plt.ylabel("Амплитуда")
plt.title("Сравнение: до и после обратного ДПФ")
plt.legend()
plt.grid()

plt.tight_layout()
plt.show()
        """

        pyperclip.copy(code.strip())

    def fast_fourier(sefl):
        """Быстрое преобразование Фурье, его принципы, фильтрация сигнала с использованием быстрого преобразования Фурье."""
        code = """
'''Быстрое преобразование Фурье (БПФ) — это оптимизированный алгоритм для вычисления дискретного преобразования Фурье (ДПФ). Оно сокращает вычислительную сложность с O(N^2) до O(NlogN), что особенно важно при работе с большими массивами данных.
Принципы БПФ:
Декомпозиция сигнала:
БПФ основано на разбиении входного сигнала на чётные и нечётные индексы:

$X[k]=\Sigma_{n=0}^{N−1}x[n]e^{−j\frac{2π}{N}kn}$

При этом сигнал разлагается на два подмассива меньшего размера, чтобы вычисления могли выполняться рекурсивно.

Рекурсивное вычисление:
Используются свойства экспоненты $e^{−jθ}$, чтобы вычислить ДПФ для частей сигнала: $X[k]=E[k]+e^{−j\frac{2π}{N}k}O[k]$

E[k] — ДПФ для чётных индексов, 

O[k] — для нечётных.

Быстродействие:
Благодаря разделению данных рекурсивно и оптимальному пересчёту, БПФ значительно ускоряет вычисления.

Размер сигнала:
Алгоритм работает наиболее эффективно, если длина сигнала 

N — степень двойки. Если это не так, сигнал часто дополняют нулями.

Фильтрация сигнала с использованием БПФ:
Фильтрация — это процесс удаления или выделения определённых частот из сигнала. Она включает несколько этапов:

Преобразование сигнала из временной области в частотную с помощью БПФ.

Применение фильтра (обнуление нежелательных частот).

Обратное преобразование Фурье для восстановления сигнала.

Типы фильтров:

Низкочастотный фильтр: удаляет высокие частоты.

Высокочастотный фильтр: удаляет низкие частоты.

Полосовой фильтр: выделяет определённый диапазон частот.
'''
import math
import matplotlib.pyplot as plt

# Параметры сигнала
fs = 1000  # Частота дискретизации (Гц)
t = [i / fs for i in range(fs)]  # Вектор времени (1 секунда)
f1, f2, f3 = 50, 150, 300  # Частоты сигналов (Гц)

# Сигнал: сумма трёх синусоид
signal = [math.sin(2 * math.pi * f1 * ti) + 0.5 * math.sin(2 * math.pi * f2 * ti) + 0.3 * math.sin(2 * math.pi * f3 * ti) for ti in t]

# Реализация дискретного преобразования Фурье (ДПФ)
def dft(signal):
    N = len(signal)
    result = []
    for k in range(N):
        real = 0
        imag = 0
        for n in range(N):
            angle = -2 * math.pi * k * n / N
            real += signal[n] * math.cos(angle)
            imag += signal[n] * math.sin(angle)
        result.append(complex(real, imag))
    return result

# Обратное дискретное преобразование Фурье (ОДПФ)
def idft(spectrum):
    N = len(spectrum)
    result = []
    for n in range(N):
        real = 0
        imag = 0
        for k in range(N):
            angle = 2 * math.pi * k * n / N
            real += spectrum[k].real * math.cos(angle) - spectrum[k].imag * math.sin(angle)
            imag += spectrum[k].real * math.sin(angle) + spectrum[k].imag * math.cos(angle)
        result.append(real / N)
    return result

# Вычисление БПФ вручную
fft_signal = dft(signal)
N = len(fft_signal)
frequencies = [i * fs / N for i in range(N)]

# Фильтрация (удаляем частоты выше 100 Гц)
fft_filtered = fft_signal.copy()
for i, freq in enumerate(frequencies):
    if freq > 100 and freq < fs / 2:
        fft_filtered[i] = 0
    elif freq >= fs / 2 and freq < fs - 100:
        fft_filtered[i] = 0

# Обратное БПФ для восстановления сигнала
filtered_signal = idft(fft_filtered)

# Визуализация
plt.figure(figsize=(12, 8))

# Исходный сигнал
plt.subplot(3, 1, 1)
plt.plot(t, signal)
plt.title("Исходный сигнал (сумма трёх синусоид)")
plt.xlabel("Время (с)")
plt.ylabel("Амплитуда")
plt.grid()

# Амплитудный спектр сигнала
plt.subplot(3, 1, 2)
plt.stem(frequencies[:N // 2], [abs(x) / N for x in fft_signal[:N // 2]], basefmt=" ")
plt.title("Амплитудный спектр исходного сигнала")
plt.xlabel("Частота (Гц)")
plt.ylabel("Амплитуда")
plt.grid()

# Фильтрованный сигнал
plt.subplot(3, 1, 3)
plt.plot(t, filtered_signal, label="Фильтрованный сигнал")
plt.title("Сигнал после низкочастотной фильтрации")
plt.xlabel("Время (с)")
plt.ylabel("Амплитуда")
plt.grid()

plt.tight_layout()
plt.show()
        """

        pyperclip.copy(code.strip())

    def conv(self):
        """Операции свёртки, связь с быстрым преобразованием Фурье, операции дискретной свёртки."""
        code = """
        '''
Свёртка — это операция, применяемая для обработки сигналов и изображений. Она используется в фильтрации, выделении особенностей, обработке временных рядов и многих других задачах. Свёртка имеет тесную связь с быстрым преобразованием Фурье (БПФ) благодаря свёрточной теореме.

Свёрточная теорема утверждает:

Свёртка двух функций во временной области эквивалентна умножению их преобразований Фурье в частотной области:

F{f*g}=F{f}⋅F{g}.

Аналогично, умножение двух функций во временной области эквивалентно свёртке их преобразований Фурье в частотной области:

F{f⋅g}=F{f}*F{g}.

Операции дискретной свёртки

$y[n] = \Sigma_{m=0}^{M-1}f[m]g[n-m]$
'''
def discrete_convolution_manual(x, h):
    # Длина входного сигнала и фильтра
    N = len(x)
    M = len(h)

    # Длина результата свёртки
    y_length = N + M - 1
    y = [0] * y_length  # Инициализация результата нулями

    # Прямой расчёт свёртки вручную
    for n in range(y_length):
        for m in range(M):
            if 0 <= n - m < N:
                y[n] += x[n - m] * h[m]

    return y

# Входные данные
x = [1, 2, 3, 4]  # Сигнал
h = [0.2, 0.5, 0.2]  # Фильтр

# Результат дискретной свёртки
result_manual = discrete_convolution_manual(x, h)

print("Дискретная свёртка вручную:", result_manual)

# Реализация свёртки через БПФ без numpy

def fft_manual(signal):
    '''Вспомогательная функция для ручного БПФ.'''
    N = len(signal)
    if N <= 1:
        return signal

    # Разделение на чётные и нечётные индексы
    even = fft_manual(signal[0::2])
    odd = fft_manual(signal[1::2])

    # Комбинирование результатов
    combined = [0] * N
    for k in range(N // 2):
        t = odd[k] * complex(math.cos(-2 * math.pi * k / N), math.sin(-2 * math.pi * k / N))
        combined[k] = even[k] + t
        combined[k + N // 2] = even[k] - t

    return combined

import math

def ifft_manual(signal):
    '''Обратное БПФ вручную.'''
    N = len(signal)
    conjugated = [complex(c.real, -c.imag) for c in signal]
    transformed = fft_manual(conjugated)
    return [c.conjugate().real / N for c in transformed]

# Применение свёртки через БПФ вручную
N = len(x) + len(h) - 1
x_padded = x + [0] * (N - len(x))
h_padded = h + [0] * (N - len(h))

X = fft_manual(x_padded)  # Прямое БПФ для сигнала
H = fft_manual(h_padded)  # Прямое БПФ для фильтра

# Умножение в частотной области
Y = [X[k] * H[k] for k in range(N)]

# Обратное БПФ для получения результата свёртки
y_fft_manual = ifft_manual(Y)

print("Свёртка через БПФ вручную:", y_fft_manual)
        """

        pyperclip.copy(code.strip())

    def discrete_conv(self):
        """Дискретная свёртка и Тёплицевы матрицы (Ганкелевы матрицы)."""
        code = """
'''
Тёплицева матрица — это квадратная или прямоугольная матрица, где элементы вдоль любой диагонали (от верхнего левого угла к нижнему правому) одинаковы.

$\pmatrix{h_0 & 0 & 0 \\ h_1 & h_0 & 0 \\ h_2 & h_1 & h_0}$

Ганкелева матрица — это матрица, где элементы постоянны вдоль антидиагоналей (от верхнего правого угла к нижнему левому). Для свёртки Ганкелева матрица часто используется для представления "обратной" задачи или задач интерполяции.
'''
def convolution_with_toeplitz(x, h):
    # Длина результата свёртки
    N = len(x) + len(h) - 1

    # Дополнение фильтра нулями до необходимой длины
    h_padded = [0] * (len(x) - 1) + list(h) + [0] * (len(x) - 1)

    # Формирование Тёплицевой матрицы вручную
    toeplitz_matrix = []
    for i in range(len(x)):
        row = h_padded[len(x) - 1 - i : len(x) - 1 - i + len(x)]
        toeplitz_matrix.append(row)

    # Выполнение свёртки (умножение матрицы на вектор)
    result = [
        sum(toeplitz_matrix[i][j] * x[j] for j in range(len(x)))
        for i in range(len(toeplitz_matrix))
    ]
    return result

# Функция для формирования Ганкелевой матрицы вручную
def hankel_matrix(h):
    N = len(h)
    H = [[0] * N for _ in range(N)]
    for i in range(N):
        for j in range(N):
            if i + j < N:
                H[i][j] = h[i + j]
    return H

# Пример сигналов
x = [1, 2, 3, 4]  # Входной сигнал
h = [0.2, 0.5, 0.2]  # Фильтр

# Результат свёртки
y = convolution_with_toeplitz(x, h)
print("Результат свёртки через Тёплицеву матрицу:", y)

# Пример Ганкелевой матрицы
h_g = [1, 2, 3, 4]
H = hankel_matrix(h_g)
print("Ганкелева матрица:")
for row in H:
    print(row)
        """
        pyperclip.copy(code.strip())

    def fourier_matrix(self):
        """Циркулянтные матрицы. Матрицы Фурье."""
        code = """
'''
Циркулянтная матрица — это квадратная матрица, где каждая строка является циклическим сдвигом предыдущей строки.

$\pmatrix{h_0 & h_{n-1} & h_{n-2} & ... & h_1 \\ h_1 & h_0 & h_{n-1} & ... & h_2 \\ h_2 & h_1 & h_0 & .... & h_3\\ ...&...&...&...&... \\ h_{n-1} & h_{n-2} & h_{n-3}&...&h_0}$

Свойства:

Диагонализируемость: Циркулянтная матрица диагонализируется с помощью матрицы Фурье:

$C=F^*ΛF,$
где 
F — матрица Фурье, 
$F^∗$— её эрмитово-сопряжённая (комплексно сопряжённая и транспонированная), а 

Λ — диагональная матрица, содержащая собственные значения C

Собственные значения: Собственные значения λk вычисляются как БПФ вектора c:

$λ_k=\Sigma_{j=0}^{n−1}c_je^{−2πikj/n},k=0,1,…,n−1.$

Циклическая свёртка: Циркулянтные матрицы используются для реализации циклической свёртки, что тесно связано с дискретным преобразованием Фурье (ДПФ).

Матрицы Фурье
Матрица Фурье — это специальная унитарная матрица, связанная с дискретным преобразованием Фурье (ДПФ).

Матрица Фурье F порядка n определяется как: $F_{j, k} = \frac{1}{\sqrt{n}}e^{−2πikj/n}

j,k=0,1,…,n−1.$

Свойства:

Унитарность: Матрица Фурье удовлетворяет уравнению:

$F^∗F=FF^∗=I$,где I — единичная матрица.

Связь с ДПФ: Применение F к вектору x эквивалентно вычислению ДПФ:

$\hat{x} = Fx, \hat{x} $— спектр сигнала.

Обратное преобразование: Обратное преобразование выполняется с помощью сопряжённой матрицы $F^*$

$x = F\hat{x}$

'''
import numpy as np

def circulant_matrix(c):
    n = len(c)
    C = np.zeros((n, n), dtype=complex)  # Циркулянтная матрица
    for i in range(n):
        C[i] = np.roll(c, i)  # Циклический сдвиг
    return C


c = np.array([1, 2, 3, 4])
C = circulant_matrix(c)
print("Циркулянтная матрица:")
print(C)

def fourier_matrix(n):
    omega = np.exp(-2j * np.pi / n)  # Корень из единицы
    F = np.array([[omega**(i * j) for j in range(n)] for i in range(n)], dtype=complex)
    return F / np.sqrt(n)  # Нормировка

# Пример
n = 4
F = fourier_matrix(n)
print("Матрица Фурье:")
print(F)
        """

        pyperclip.copy(code.strip())

    def matvec_circ(self):
        """
        Быстрый матвек с циркулянтом
        """
        code = """
'''
Циркулянтные матрицы обладают особой структурой, которая позволяет значительно ускорить их умножение на вектор. Это возможно благодаря их связи с быстрым преобразованием Фурье (БПФ). Вместо прямого умножения, которое имеет вычислительную сложность O(n^2), можно свести задачу к выполнению преобразований Фурье, что сокращает сложность до O(nlogn)

Если C — циркулянтная матрица, построенная из вектора c, то её умножение на вектор x может быть вычислено следующим образом:

Вычисляется дискретное преобразование Фурье (ДПФ) для c и x:

$\hat{c} = FFT(c), \hat{x}=FFT(x)$

Результирующий спектр $\hat{y}$ получается как поэлементное произведение спектров:

$\hat{y} = \hat{c}\hat{x}$ 

Выполняется обратное дискретное преобразование Фурье (ОДПФ), чтобы получить результат:

$y=IFFT(\hat{y})$
'''
import math

# Реализация дискретного преобразования Фурье (ДПФ)
def dft(vector):
    n = len(vector)
    result = [0] * n
    for k in range(n):
        for j in range(n):
            angle = -2 * math.pi * k * j / n
            result[k] += vector[j] * complex(math.cos(angle), math.sin(angle))
    return result

# Реализация обратного дискретного преобразования Фурье (ОДПФ)
def idft(vector):
    n = len(vector)
    result = [0] * n
    for k in range(n):
        for j in range(n):
            angle = 2 * math.pi * k * j / n
            result[k] += vector[j] * complex(math.cos(angle), math.sin(angle))
    return [x / n for x in result]

# Быстрое умножение циркулянтной матрицы на вектор

def circulant_multiply_manual(c, x):
    '''
    Быстрое умножение циркулянтной матрицы на вектор без использования готовых методов.
    '''
    # Прямое преобразование Фурье
    c_fft = dft(c)
    x_fft = dft(x)

    # Поэлементное произведение в спектральной области
    y_fft = [c_fft[i] * x_fft[i] for i in range(len(c))]

    # Обратное преобразование Фурье
    y = idft(y_fft)

    # Возврат только вещественной части (если исходные данные вещественные)
    return [value.real for value in y]

# Пример использования
c = [1, 2, 3, 4]  # Первый столбец циркулянтной матрицы
x = [5, 6, 7, 8]  # Вектор для умножения

result = circulant_multiply_manual(c, x)
print("Результат быстрого умножения циркулянтной матрицы на вектор:")
print(result)

"""

        pyperclip.copy(code.strip())

    def dft_system(self):
        """Дисретное преобразование системы"""
        code = """
import math
import matplotlib.pyplot as plt

# Parameters
N = 64  # Length of the signal (number of samples)
k_values = [k - N // 2 for k in range(N)]  # Symmetric k-values centered around 0

# Define the function F(k)
def F(k):
    if abs(k) <= 3:
        return k * math.sin(3 * k) * math.atan(2 * k)
    else:
        return 0

# Generate the signal F(k)
F_k = [F(k) for k in k_values]

# Compute the Discrete Fourier Transform (DFT)
X = []  # Spectral coefficients
for n in range(N):
    real = 0
    imag = 0
    for k in range(N):
        angle = -2 * math.pi * n * k / N
        real += F_k[k] * math.cos(angle)
        imag += F_k[k] * math.sin(angle)
    X.append(complex(real, imag))

# Compute the inverse DFT to reconstruct the signal
F_reconstructed = []
for k in range(N):
    real = 0
    for n in range(N):
        angle = 2 * math.pi * n * k / N
        real += (X[n].real * math.cos(angle) - X[n].imag * math.sin(angle)) / N
    F_reconstructed.append(real)

# Visualization
plt.figure(figsize=(12, 6))

# Original signal F(k)
plt.subplot(2, 1, 1)
plt.stem(k_values, F_k, basefmt=" ", label="Оригинальная функция F(k)")
plt.xlabel("k")
plt.ylabel("Амплитуда")
plt.title("Оригинальная функция F(k)")
plt.grid()
plt.legend()

# Reconstructed signal
plt.subplot(2, 1, 2)
plt.stem(k_values, F_reconstructed, basefmt=" ", label="Восстановленный сигнал", markerfmt="rx")
plt.xlabel("k")
plt.ylabel("Амплитуда")
plt.title("Восстановленный сигнал (обратное ДПФ)")
plt.grid()
plt.legend()

plt.tight_layout()
plt.show()
"""

        pyperclip.copy(code)

    def help(self):
        """Выводит справку о всех доступных методах."""
        help_message = "Справка по методам:\n"
        for method, description in self.methods_info.items():
            help_message += f"- {method}: {description}\n"
        pyperclip.copy(help_message)
