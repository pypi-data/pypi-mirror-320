# Задание в котором используется дпф и идпф
import numpy as np
import math
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
#дпф и идпф
def idft(spectrum):
    le = len(spectrum)
    return [i / le for i in dft(spectrum, direct=-1)]

def F(k):
    if abs(k) <= 3:
        return k * np.sin(3 * k) * np.arctan(2 * k)
    else:
        return 0

# Создаем дискретные значения функции
N = 128  # Количество точек
k_values = np.linspace(-10, 10, N)
signal = np.array([F(k) for k in k_values])

# Выполняем ДПФ
spectrum = dft(signal)

# Выполняем обратное ДПФ
reconstructed_signal = idft(spectrum)

# Построение графиков
plt.figure(figsize=(12, 6))

# Исходный сигнал
plt.subplot(1, 2, 1)
plt.plot(k_values, signal, label="Исходный сигнал")
plt.title("Исходный сигнал")
plt.xlabel("k")
plt.ylabel("F(k)")
plt.grid()
plt.legend()

# Восстановленный сигнал
plt.subplot(1, 2, 2)
plt.plot(k_values, reconstructed_signal, label="Восстановленный сигнал", linestyle="--")
plt.title("Восстановленный сигнал")
plt.xlabel("k")
plt.ylabel("F(k)")
plt.grid()
plt.legend()

plt.tight_layout()
plt.show()

