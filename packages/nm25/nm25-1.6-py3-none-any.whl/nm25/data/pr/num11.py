# ## Неявный QR алгоритм (со сдвигами).
# Поиск собственных векторов



import numpy as np




def matmul(A, B):
    if len(A[0]) != len(B):
        print("Can't multiply.")
        return

    matrix = False
    if isinstance(B[0], list):
        matrix = True

    if matrix:
        m, n, p = len(A), len(B), len(B[0])
        C = [[0] * p for _ in range(m)]
        for i in range(m):  # строки A
            for j in range(p):  # столбцы B
                for k in range(n):  # общий размер
                    C[i][j] += A[i][k] * B[k][j]
        return C
    else:
        C = []
        for row in A:
            y_i = sum(row[j] * B[j] for j in range(len(B)))
            C.append(y_i)
        return C




def vector_prod(vec1, vec2):
    return sum(i * j for i, j in zip(vec1, vec2))


def gram_schmidt(A):
    m, n = A.shape
    Q = np.zeros((m, n))
    R = np.zeros((n, n))

    for j in range(n):
        v = A[:, j]

        # Ортогонализация текущего вектора
        for i in range(j):
            R[i, j] = vector_prod(Q[:, i], A[:, j])
            v = v - R[i, j] * Q[:, i]
        # Нормализация вектора
        R[j, j] = sum(i**2 for i in v) ** 0.5
        Q[:, j] = [i / R[j, j] for i in v]

    return Q, R


def QR_method_with_shift(A, accuracy=0.001):
    Q_list = []

    def get_up_max(A):
        """
        Получить наибольшее значение из верхнего правого треугольника Матрицы
        """
        values = []
        for i in range(A.shape[0]):
            for j in range(i + 1, A.shape[1]):
                values.append(A[i, j])
        return max(values)

    def get_shift(A):
        """
        Выбор сдвига (обычно нижний правый элемент матрицы)
        """
        n = A.shape[0]
        return A[n - 1, n - 1]

    eye = np.eye(A.shape[0])
    while get_up_max(A) > accuracy:
        # Шаг со сдвигом
        shift = get_shift(A)
        # Вычитаем сдвиг из диагонали
        A_shifted = A - shift * eye

        # Выполняем QR-разложение
        Q, R = gram_schmidt(A_shifted)
        Q_list.append(Q)

        # Обновляем матрицу с добавлением сдвига обратно
        A = matmul(R, Q) + shift * eye

    # Восстановим матрицу Q из произведений всех Q
    Q_final = eye.copy()
    for i in Q_list:
        Q_final = matmul(Q_final, i)

    return list(zip(*Q_final))


# Пример использования
A = np.array(
    [
        [1, 2, 3],
        [2, 3, 4],
        [3, 4, 4],
    ]
)
vecs = QR_method_with_shift(A)
print("Собственные векторы:")
print(*vecs, sep="\n")




"""QR-алгоритм через qr-разложение"""
import math
import numpy as np

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