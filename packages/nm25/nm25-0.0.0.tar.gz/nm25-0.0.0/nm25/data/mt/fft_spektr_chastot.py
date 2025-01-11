# БПФ И СПЕКТР ЧАСТОТ
import numpy as np
import math
import matplotlib.pyplot as plt

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

def F(k):
    return np.exp(-k**2) + np.arctan(k)
    
def calculate_frequencies(N, sample_rate):
    frequencies = []
    for k in range(N):
        if k <= N//2:
            freq = k * sample_rate / N
        else:
            freq = (k - N) * sample_rate / N
        frequencies.append(freq)
    return frequencies

# Создаем дискретные значения функции
N = 128  # Количество точек
k_values = np.linspace(-10, 10, N)
signal = np.array([F(k) for k in k_values])

# Выполняем БПФ
spectrum = fft(signal)

# Выполняем обратное БПФ
reconstructed_signal = ifft(spectrum)

# Рассчитываем частоты
frequencies = calculate_frequencies(N, N / 20) #20 - длина отрезка иксов
# Рассчитываем амплитуды спектра
amplitudes = np.abs(spectrum)

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

# Спектр частот
plt.subplot(1, 2, 2)
plt.plot(frequencies, amplitudes, label="Спектр частот", color="orange")
plt.title("Спектр частот")
plt.xlabel("Частота")
plt.ylabel("Амплитуда")
plt.grid()
plt.legend()

plt.tight_layout()
plt.show()