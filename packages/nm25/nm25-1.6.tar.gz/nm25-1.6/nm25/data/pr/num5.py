# ## Разложение Шура и QR алгоритм
# разложение матрицы на унитарную, верхнюю треугольную и обратную унитарную матрицы
# 
# Метод вращения (Якоби) предпочтителен для симметричных матриц небольшого размера (до 50x50) и при необходимости высокой точности собственных векторов. QR-метод лучше подходит для крупных матриц, несимметричных матриц, и для быстрого нахождения доминирующих собственных значений.

# ### QR через разложение Шура



import numpy as np


def matrix_multiply(A, B):
    """
    Выполняет перемножение двух матриц A и B вручную.
    """
    n, m = A.shape
    m2, p = B.shape
    if m != m2:
        raise ValueError("Количество столбцов A должно совпадать с количеством строк B")

    result = np.zeros((n, p))
    for i in range(n):
        for j in range(p):
            for k in range(m):
                result[i][j] += A[i][k] * B[k][j]
    return result


def qr_decomposition(A):
    """
    Выполняет QR-разложение методом Грама-Шмидта.
    """
    n, m = A.shape
    Q = np.zeros((n, n))
    R = np.zeros((n, m))

    for i in range(m):
        v = A[:, i]
        for j in range(i):
            R[j, i] = sum(Q[:, j][k] * v[k] for k in range(n))  # Скалярное произведение
            v -= R[j, i] * Q[:, j]
        R[i, i] = (sum(v[k] ** 2 for k in range(n))) ** 0.5  # Норма вектора
        Q[:, i] = v / R[i, i]
    return Q, R


def schur_decomposition(A, num_iterations=100, tol=1e-10):
    """
    Выполняет разложение Шура с использованием QR-алгоритма.
    """
    n = A.shape[0]
    T = np.array(A, dtype=float)  # Копия матрицы
    Q_total = np.eye(n)  # Единичная матрица

    for _ in range(num_iterations):
        Q, R = qr_decomposition(T)
        T = matrix_multiply(R, Q)
        Q_total = matrix_multiply(Q_total, Q)
        # Проверка на сходимость
        if all(abs(T[i, j]) < tol for i in range(1, n) for j in range(i)):
            break

    return Q_total, T


def qr_algorithm(A, num_iterations=100, tol=1e-10):
    """
    QR-алгоритм для вычисления собственных значений матрицы.
    """
    Q_total, T = schur_decomposition(A, num_iterations=num_iterations, tol=tol)
    eigenvalues = [T[i, i] for i in range(len(T))]
    return Q_total, T, eigenvalues


# ### QR без Шура



import math

def dot_product(A, B):
    '''Вычисляет скалярное произведение двух векторов'''
    return sum(a * b for a, b in zip(A, B))

def matrix_multiply(A, B):
    '''Выполняет умножение двух матриц'''
    result = [[0] * len(B[0]) for _ in range(len(A))]
    for i in range(len(A)):
        for j in range(len(B[0])):
            result[i][j] = sum(A[i][k] * B[k][j] for k in range(len(B)))
    return result

def qr_decomposition(A):
    '''
    Выполняет разложение QR на основе метода Грамма-Шмидта
    '''
    m = len(A)
    n = len(A[0])
    Q = [[0] * n for _ in range(m)]
    R = [[0] * n for _ in range(n)]

    for j in range(n):
        v = [A[i][j] for i in range(m)]
        for i in range(j):
            R[i][j] = dot_product([Q[k][i] for k in range(m)], v)
            v = [v[k] - R[i][j] * Q[k][i] for k in range(m)]
        R[j][j] = math.sqrt(dot_product(v, v))
        for i in range(m):
            Q[i][j] = v[i] / R[j][j]

    return Q, R

def makesimilar(A):
    Q, R = qr_decomposition(A)
    return matrix_multiply(R, Q)

def eig_qr(A, tol=1e-4, max_iter=1000):
    '''Находит собственные значения матрицы A с помощью QR-алгоритма'''
    B = A
    iters = 0
    leig = B[-1][-1]
    diff = float('inf')

    while diff > tol and iters < max_iter:
        B = makesimilar(B)
        iters += 1
        new_leig = B[-1][-1]
        diff = abs(leig - new_leig)
        leig = new_leig

    eigs = [B[i][i] for i in range(len(B))]
    return eigs, iters


# ### QR без Шура со сдвигом



import math

def dot_product(A, B):
    '''Вычисляет скалярное произведение двух векторов'''
    return sum(a * b for a, b in zip(A, B))

def matrix_multiply(A, B):
    '''Выполняет умножение двух матриц'''
    result = [[0] * len(B[0]) for _ in range(len(A))]
    for i in range(len(A)):
        for j in range(len(B[0])):
            result[i][j] = sum(A[i][k] * B[k][j] for k in range(len(B)))
    return result

def qr_decomposition(A):
    '''Выполняет разложение QR на основе метода Грамма-Шмидта'''
    m = len(A)
    n = len(A[0])
    Q = [[0] * n for _ in range(m)]  # Размер матрицы Q
    R = [[0] * n for _ in range(n)]

    for j in range(n):
        v = [A[i][j] for i in range(m)]
        for i in range(j):
            R[i][j] = dot_product([Q[k][i] for k in range(m)], v)
            v = [v[k] - R[i][j] * Q[k][i] for k in range(m)]
        norm_v = math.sqrt(dot_product(v, v))
        if norm_v == 0:  # Проверяем, если вектор v нулевой
            continue
        R[j][j] = norm_v
        for i in range(m):
            Q[i][j] = v[i] / R[j][j]

    return Q, R

def qr_algorithm_with_shift(A, tol=1e-6, max_iter=1000):
    '''QR со сдвигом'''
    B = A
    n = len(A)
    iters = 0

    while iters < max_iter:
        # Сдвиг (используем последний диагональный элемент как смещение)
        shift = B[-1][-1]

        # Создаем матрицу B - shift * I
        shifted_matrix = [[B[i][j] - (shift if i == j else 0) for j in range(n)] for i in range(n)]

        # QR-разложение смещенной матрицы
        Q, R = qr_decomposition(shifted_matrix)

        # Обратное умножение R * Q + сдвиг
        B = matrix_multiply(R, Q)
        for i in range(n):
            B[i][i] += shift

        # Проверяем сходимость:
        # разница между диагональными элементами на двух итерациях
        off_diagonal_sum = sum(abs(B[i][j]) for i in range(n) for j in range(n) if i != j)
        if off_diagonal_sum < tol:
            break

        iters += 1

    eigenvalues = [B[i][i] for i in range(n)]
    return eigenvalues, iters




# Пример использования
A = np.array([[7, 2, 1, 5],
              [2, 8, 3, 1],
              [1, 3, 6, 2],
              [5, 1, 2, 3]], dtype=float)
# A = np.array([[5, 2, 1], [7, 3, 1], [0, 0, 1]], dtype=float)
# A = np.array([[1, 3, 5], [2, 7, 1], [0, 1, 0]], dtype=float)

Q_total, T, eigenvalues = qr_algorithm(A)

# Вывод результатов
print("Унитарная матрица Q:")
print(Q_total)
print("\nВерхнетреугольная матрица T:")
print(T)
print("\nСобственные значения матрицы:")
print(eigenvalues)


# ### Тестирование



A = [[7, 2, 1, 5],
      [2, 8, 3, 1],
      [1, 3, 6, 2],
      [5, 1, 2, 3]]

eigenvalues, iterations = eig_qr(A)
print(f"Собственные значения: {eigenvalues}, Итерации: {iterations}")




A = [[7, 2, 1, 5],
      [2, 8, 3, 1],
      [1, 3, 6, 2],
      [5, 1, 2, 3]]

eigenvalues, iterations = qr_algorithm_with_shift(A)
print(f"Собственные значения: {eigenvalues}, Итерации: {iterations}")




# Сравните точность QR для поиска собственных чисел матрицы 
# при использовании различных критериев остановки (например, норма ошибки <10-2 или <10-8 ). 

eigs_tol1, iters_tol1 = qr_algorithm(A, tol=1e-2)

# Критерий остановки 2: норма ошибки < 10^-8
eigs_tol2, iters_tol2 = qr_algorithm(A, tol=1e-8)

# Сравнение результатов
print("Собственные значения (точность 10^-2):", eigs_tol1)
print("Количество итераций (точность 10^-2):", iters_tol1)

print("Собственные значения (точность 10^-8):", eigs_tol2)
print("Количество итераций (точность 10^-8):", iters_tol2)

#При более строгом критерии (10^-8) значения будут точнее. При более мягком критерии (10^-2) 
#значения будут приближёнными. Но для более строго также потребуется больше операций.