# Метод штрассена для матриц любых размеров

import math
import numpy as np

def pad_matrix(matrix, size):
    """Дополняет матрицу нулями до заданного размера."""
    current_size = len(matrix)
    new_matrix = [[0] * size for _ in range(size)]
    for i in range(current_size):
        for j in range(len(matrix[0])):
            new_matrix[i][j] = matrix[i][j]
    return new_matrix

def unpad_matrix(matrix, original_rows, original_cols):
    """Удаляет дополненные нули, возвращая матрицу к исходным размерам."""
    return [row[:original_cols] for row in matrix[:original_rows]]

def next_power_of_two(n):
    """Находит следующую степень двойки для числа n."""
    return 2 ** math.ceil(math.log2(n))

def strassen_with_padding(A, B):
    """Алгоритм Штрассена с поддержкой матриц, размер которых не является степенью двойки."""
    # Размеры исходных матриц
    original_rows_A, original_cols_A = len(A), len(A[0])
    original_rows_B, original_cols_B = len(B), len(B[0])
    
    # Новый размер матриц, кратный степени двойки
    new_size = max(next_power_of_two(len(A)), next_power_of_two(len(A[0])), 
                next_power_of_two(len(B)), next_power_of_two(len(B[0])))

    # Дополняем матрицы нулями
    A_padded = pad_matrix(A, new_size)
    B_padded = pad_matrix(B, new_size)
    
    # Выполняем алгоритм Штрассена
    C_padded = strassen(A_padded, B_padded)
    
    # Убираем дополнение
    return unpad_matrix(C_padded, original_rows_A, original_cols_B)

def add_matrices(A, B):
    """Сложение двух матриц."""
    n = len(A)
    return [[A[i][j] + B[i][j] for j in range(n)] for i in range(n)]


def subtract_matrices(A, B):
    """Вычитание одной матрицы из другой."""
    n = len(A)
    return [[A[i][j] - B[i][j] for j in range(n)] for i in range(n)]


def split_matrix(A):
    """Разделение матрицы на четыре подматрицы."""
    n = len(A)
    mid = n // 2
    A11 = [row[:mid] for row in A[:mid]]
    A12 = [row[mid:] for row in A[:mid]]
    A21 = [row[:mid] for row in A[mid:]]
    A22 = [row[mid:] for row in A[mid:]]
    return A11, A12, A21, A22


def merge_matrices(C11, C12, C21, C22):
    """Объединение четырех подматриц в одну матрицу."""
    n = len(C11)
    top = [C11[i] + C12[i] for i in range(n)]
    bottom = [C21[i] + C22[i] for i in range(n)]
    return top + bottom

def strassen(A, B):
    """Реализация алгоритма Штрассена для перемножения двух матриц."""
    n = len(A)

    if n == 1:
        return [[A[0][0] * B[0][0]]]

    # Разбиение матриц на подматрицы
    mid = n // 2

    A11 = [row[:mid] for row in A[:mid]]
    A12 = [row[mid:] for row in A[:mid]]
    A21 = [row[:mid] for row in A[mid:]]
    A22 = [row[mid:] for row in A[mid:]]

    B11 = [row[:mid] for row in B[:mid]]
    B12 = [row[mid:] for row in B[:mid]]
    B21 = [row[:mid] for row in B[mid:]]
    B22 = [row[mid:] for row in B[mid:]]

    # Рекурсивные вызовы
    F1 = strassen(add_matrices(A11, A22), add_matrices(B11, B22))
    F2 = strassen(add_matrices(A21, A22), B11)
    F3 = strassen(A11, subtract_matrices(B12, B22))
    F4 = strassen(A22, subtract_matrices(B21, B11))
    F5 = strassen(add_matrices(A11, A12), B22)
    F6 = strassen(subtract_matrices(A21, A11), add_matrices(B11, B12))
    F7 = strassen(subtract_matrices(A12, A22), add_matrices(B21, B22))

    # Объединение подматриц в результирующую матрицу
    C11 = add_matrices(subtract_matrices(add_matrices(F1, F4), F5), F7)
    C12 = add_matrices(F3, F5)
    C21 = add_matrices(F2, F4)
    C22 = add_matrices(subtract_matrices(add_matrices(F1, F3), F2), F6)

    return merge_matrices(C11, C12, C21, C22)

# Тестирование кода
A = np.random.uniform(0, 10, (7, 7))
B = np.random.uniform(0, 10, (7, 7))

result = strassen_with_padding(A, B)
for row in result:
    print(row)