# QR алгоритм для собственных значений
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

def eig_qr(A, tol=1e-8, max_iter=1000):
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

A = np.array([[7, 2, 1, 5],
              [2, 8, 3, 1],
              [1, 3, 6, 2],
              [5, 1, 2, 3]], dtype=float)
eig_qr(A)