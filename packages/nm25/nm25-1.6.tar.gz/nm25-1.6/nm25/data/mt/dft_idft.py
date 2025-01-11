# дпф и идпф
import math
import numpy as np
import matplotlib.pyplot as plt

def dft(x, direct=1):
    # Стандартный метод фурье
    N = len(x)
    X = []  # Массив для хранения результатов
    for k in range(N):
        X.append(
            sum(x[n] * math.e ** (-2j * direct * math.pi * k * n / N) for n in range(N))
        )
    return X

def idft(spectrum):
    le = len(spectrum)
    return [i / le for i in dft(spectrum, direct=-1)]