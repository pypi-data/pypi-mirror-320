# ДПФ И удалить компоненты выше 5гц
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

def idft(spectrum):
    le = len(spectrum)
    return [i / le for i in dft(spectrum, direct=-1)]
    
def f(t):
    return np.sin(2*math.pi*t) + np.cos(6 * math.pi * t)

def calculate_frequencies(N, sample_rate):
    """
    Вычисляет массив частот для ДПФ
    N - количество точек
    sample_rate - частота дискретизации (отсчетов в секунду)
    """
    frequencies = []
    for k in range(N):
        if k <= N//2:
            freq = k * sample_rate / N
        else:
            freq = (k - N) * sample_rate / N
        frequencies.append(freq)
    return frequencies

# Создаем временной ряд
N = 256  # количество точек
T = 1.0  # общее время
sample_rate = N / T  # частота дискретизации
t = np.linspace(0, T, N)
signal = [f(ti) for ti in t]

# Выполняем ДПФ
spectrum = dft(signal)

# Вычисляем частоты для каждой компоненты спектра
freqs = calculate_frequencies(N, sample_rate)

# Создаем фильтр низких частот (5 Гц)
filter_mask = [abs(f) <= 5 for f in freqs]
filtered_spectrum = [s if m else 0 for s, m in zip(spectrum, filter_mask)]

# Выполняем обратное преобразование
filtered_signal = idft(filtered_spectrum)

# Визуализация
plt.figure(figsize=(15, 10))

# Исходный сигнал
plt.subplot(2, 1, 1)
plt.plot(t, signal)
plt.title('Исходный сигнал')
plt.grid(True)

# Фильтрованный сигнал
plt.subplot(2, 1, 2)
plt.plot(t, filtered_signal)
plt.title('Фильтрованный сигнал')
plt.grid(True)

plt.tight_layout()
plt.show()