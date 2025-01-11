# ## Спектр и псевдоспектр.
# 
# Псевдоспектр матрицы A обобщает понятие спектра и определяется как множество комплексных чисел z, которые почти являются собственными значениями, в смысле:
# 
# $z \in A_\epsilon(A) \Longleftrightarrow ||(A - zI)^{-1}|| \geq \frac{1}{\epsilon}$
# 
# Геометрически, псевдоспектр — это области в комплексной плоскости, вблизи которых матрица становится почти вырожденной.



import numpy as np
import matplotlib.pyplot as plt




# %load linalg
from itertools import permutations
import numpy as np


def norm(mat):
    """
    Норма матрицы
    """
    s = 0
    for row in mat:
        for i in row:
            s += i.real**2 + i.imag**2
    return s**0.5


def count_inv(mas):
    """
    Количество перестановок
    """
    s = 0
    for i in range(len(mas)):
        for j in range(i, len(mas)):
            if mas[i] > mas[j]:
                s += 1
    return s


def det(mat):
    """
    Определитель матрицы
    """
    d = 0
    for comb in permutations(range(len(mat))):
        v = 1
        for i, j in enumerate(comb):
            v *= mat[i][j]
        d += v * (-1) ** count_inv(comb)
    return d


def conj(mat, i, j):
    """
    Алгебраическое дополнение
    """
    new_mat = []
    for n_row, row in enumerate(mat):
        if n_row == i:
            continue
        new_mat.append([])
        for n_col, col in enumerate(row):
            if n_col != j:
                new_mat[-1].append(col)
    return det(new_mat)


def conjM(mat):
    """
    Сопряженная матрица
    """
    new_mat = []
    for row_n, row in enumerate(mat):
        new_mat.append([])
        for col_n, _ in enumerate(row):
            new_mat[-1].append(conj(mat, row_n, col_n))
    return new_mat


def inv(mat):
    """
    Обратная матрица
    """
    return 1 / det(mat) * np.array(conjM(mat))




def pseudospectrum(matrix, grid_points=100, xlim=(-5, 5), ylim=(-5, 5)):
    """
    Рисует псевдоспектр матрицы.

    :param matrix: Матрица, для которой вычисляется псевдоспектр.
    :param grid_points: Количество точек сетки вдоль одной оси.
    :param xlim: Пределы по оси X для сетки.
    :param ylim: Пределы по оси Y для сетки.
    """
    x = np.linspace(*xlim, grid_points)
    y = np.linspace(*ylim, grid_points)
    xx, yy = np.meshgrid(x, y)
    zz = xx + 1j * yy

    resolvent_norm = np.zeros_like(zz, dtype=float)

    for i in range(grid_points):
        for j in range(grid_points):
            z = zz[i, j]
            try:
                # Вычисляем норму обратной матрицы
                _inv = inv(matrix - z * np.eye(matrix.shape[0]))
                resolvent_norm[i, j] = 1 / norm(_inv)

            except:
                # Если обратной матрицы нет, ставим бесконечность
                resolvent_norm[i, j] = np.inf

    # Рисуем псевдоспектральные уровни
    plt.figure(figsize=(8, 6))
    plt.contour(xx, yy, np.log10(resolvent_norm), levels=20, cmap="viridis")
    plt.colorbar()

    # Вычисление собственных значений и их отображение
    # eigenvalues = eigvals(matrix)
    # plt.scatter(eigenvalues.real, eigenvalues.imag, color="red", label="Eigenvalues")
    plt.xlabel("Real part")
    plt.ylabel("Imaginary part")
    plt.title("Pseudospectrum")
    plt.show()


# Пример использования
A = np.array([[1, 2], [3, 4]])
pseudospectrum(A)  # , xlim=(-10, 10), ylim=(-10, 10))