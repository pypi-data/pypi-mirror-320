# вычисление массива частот
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
    
# Пример
N = 256  # количество точек
T = 1.0  # общее время (длина интервала для linspace)
sample_rate = N / T  # частота дискретизации
t = np.linspace(0, T, N)

# Вычисляем частоты для каждой компоненты спектра
freqs = calculate_frequencies(N, sample_rate)