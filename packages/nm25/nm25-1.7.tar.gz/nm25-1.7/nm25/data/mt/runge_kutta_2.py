# Метод Рунге-Кутта 2-го порядка 
import numpy as np
import matplotlib.pyplot as plt

# Уравнения системы
def equation_x(t, X):
    x, y = X
    return x + y

def equation_y(t, X):
    x, y = X
    return y - x

# Если не система, то functions = [equation]
functions = [equation_x, equation_y]

# Метод Рунге-Кутта 2-го порядка для системы
def RungeKutta_2_system(X0, t0, t_end, h):
    n = int((t_end - t0) / h)
    X = np.zeros([n + 1, len(X0)])
    t = np.zeros(n + 1)
    X[0] = X0
    t[0] = t0

    for i in range(n):
        k1 = np.zeros(len(X0))
        k2 = np.zeros(len(X0))
        for j in range(len(X0)):
            k1[j] = h * functions[j](t[i], X[i])
        for j in range(len(X0)):
            k2[j] = h * functions[j](t[i] + 0.5*h, X[i] + k1/2)
        for j in range(len(X0)):
            X[i + 1] = X[i] + (k1 + k2) / 2
        t[i + 1] = t[i] + h

    return t, X
    
# ВАЖНО
# в алгоритме за t берется та переменная, по которой изменяются остальные,
# то есть если уравнение такого вида dx/dy = x + y,
# то за t мы будем брать переменную y

# Другими словами
# В методе РунгеКутта за t0 мы берем ту переменную,
# которую мы перебираем на промежутке (то, от чего зависит наша функция)

# Пример
# Параметры
x0 = 1
y0 = 0
t0 = 0
t_end = 1
h = 0.01
X0 = [x0, y0]
# Решение
t, X = RungeKutta_2_system(X0, t0, t_end, h)
x, y = X[:, 0], X[:, 1]

# Фазовый портрет
plt.plot(x, y)
plt.title('Фазовый портрет')
plt.xlabel('x')
plt.ylabel('y')
plt.grid(True)
plt.show()