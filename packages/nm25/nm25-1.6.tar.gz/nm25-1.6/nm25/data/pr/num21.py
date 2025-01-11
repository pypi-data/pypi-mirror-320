import numpy as np
import matplotlib.pyplot as plt

def f(x, y):
    """Правая часть уравнения dy/dx = f(x, y)."""
    return x + y - 2

def runge_kutta_4(f, x0, y0, h):
    """Метод Рунге-Кутты 4-го порядка для получения начальных значений."""
    k1 = h * f(x0, y0)
    k2 = h * f(x0 + h / 2, y0 + k1 / 2)
    k3 = h * f(x0 + h / 2, y0 + k2 / 2)
    k4 = h * f(x0 + h, y0 + k3)
    return y0 + (k1 + 2 * k2 + 2 * k3 + k4) / 6

def milne_method(f, x0, y0, a, b, h, epsilon):
    """Решение задачи методом Милна."""
    n = int((b - a) / h) + 1  # Число точек сетки
    x = [x0 + i * h for i in range(n)]
    y = np.zeros(n)

    # Начальные условия
    y[0] = y0
    for i in range(1, 4):  # Первые 3 точки методом Рунге-Кутты
        y[i] = runge_kutta_4(f, x[i-1], y[i-1], h)

    for m in range(4, n):
        # Первая формула Милна для y_m^[1]
        y_pred = y[m-4] + (4 * h / 3) * (2 * f(x[m-1], y[m-1]) - f(x[m-2], y[m-2]) + 2 * f(x[m-3], y[m-3]))
        f_pred = f(x[m], y_pred)

        # Вторая формула Милна для y_m^[2]
        y_corr = y[m-2] + (h / 3) * (f(x[m-2], y[m-2]) + 4 * f(x[m-1], y[m-1]) + f_pred)

        # Погрешность
        error = abs(y_corr - y_pred) / 29

        # Проверка точности
        if error <= epsilon:
            y[m] = y_corr
        else:
            raise ValueError(f"Точность не достигнута на шаге {m}. Уменьшите шаг h.")

    return x, y

# Параметры задачи
x0, y0 = 0, 1  # Начальные условия
a, b = 0, 2    # Интервал интегрирования
h = 0.2        # Шаг сетки
epsilon = 1e-5 # Точность

# Решение методом Милна
x, y = milne_method(f, x0, y0, a, b, h, epsilon)

# Вывод результатов
for xi, yi in zip(x, y):
    print(f"x = {xi:.2f}, y = {yi:.5f}")


plt.plot(x, y, label='Метод Милна', marker='o')
plt.xlabel('t')
plt.ylabel('y')
plt.title('Решение ODU методом Милна')
plt.legend()
plt.grid()
plt.show()