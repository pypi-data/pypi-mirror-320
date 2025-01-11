# # Быстрый matvec с циркулянтом
# 
# Если требуется умножить циркулянт на вектор, то вычисления происходят быстрее с помощью
# последующего метода
# 
# $C = F^*_n (F_n(c)\cdot F_n(x))$



# %load fft_vanila
import math


def get_divides(n):
    divides = []
    i = 2
    while n > 1:
        if n % i == 0:
            n /= i
            divides.append(i)
        else:
            i += 1

    return [1] + divides


def dft(x, direct=1):
    # Стандартный метод фурье
    N = len(x)
    X = []  # Массив для хранения результатов
    for k in range(N):
        X.append(
            sum(x[n] * math.e ** (-2j * direct * math.pi * k * n / N) for n in range(N))
        )
    return X


def fft(x, direct=1, divides=[]):
    """
    Обобщенный метод Кули-Туки
    """
    if not divides:
        divides = get_divides(len(x))
    N = len(x)
    p = divides.pop()
    # Используем стандартный FFT для малых частей
    if p == 1:
        return dft(x, direct=direct)

    # Разделяем на p частей
    parts = [x[i::p] for i in range(p)]

    # Рекурсивно применяем ДПФ к каждой части
    fft_parts = [fft(part, direct, divides) for part in parts]

    # Скомбинированные результаты
    result = []
    for k in range(N):
        val = 0
        for i in range(p):
            val += fft_parts[i][k % (N // p)] * math.e ** (
                -2j * direct * math.pi * i * k / N
            )
        result.append(val)

    return result


def ifft(spectrum):
    le = len(spectrum)
    return [i / le for i in fft(spectrum, direct=-1)]




def circulant_matvec(c, x):
    """
    Функция умножения циркулянта на вектор.

    c - первый столбец циркулянта
    x - вектор
    """
    return ifft([a * b for a, b in zip(fft(c), fft(x))])




import numpy as np
import scipy as sp

n = 5000
c = np.random.random(n)
C = sp.linalg.circulant(c)  # делает из набора чисел (5000,) циркулянт 5000x5000

x = np.random.randn(n)

# Погрешность вычеслений
max(circulant_matvec(C[:, 0], x) - C @ x)