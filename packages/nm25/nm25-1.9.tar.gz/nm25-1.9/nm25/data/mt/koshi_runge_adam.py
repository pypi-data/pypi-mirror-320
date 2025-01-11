# Коши методом рунге методом адама
import matplotlib.pyplot as plt
import numpy as np

#коши методом рунге кутта методом адама
def RungeKutta_3_system(X0, t0, t_end, h):
    n = int((t_end - t0) / h)

    X = np.zeros([n + 1, len(X0)])
    t = np.zeros(n + 1)
    X[0] = X0
    t[0] = t0

    for i in range(n):
        k1 = np.zeros(len(X0))
        k2 = np.zeros(len(X0))
        k3 = np.zeros(len(X0))
        for j in range(len(X0)):
            k1[j] = h * functions[j](t[i], X[i])
        for j in range(len(X0)):
            k2[j] = h * functions[j](t[i] + h/2, X[i] + k1/2)
        for j in range(len(X0)):
            k3[j] = h * functions[j](t[i] + h, X[i] - k1 + 2*k2)
        for j in range(len(X0)):
            X[i + 1] = X[i] + (k1 + 4*k2 + k3) / 6
        t[i + 1] = t[i] + h

    return t, X

def f(x, y):
    return x*y*np.arctan(x)

functions = [f]

def adams_moulton(x0, y0, h, x_end):
    n = int((x_end - x0) / h) + 1
    x = np.linspace(x0, x_end, n)
    y = np.zeros(n)
    
    y[0] = y0

    for i in range(1, n):
        x_prev, y_prev = x[i - 1], y[i - 1]
        # Predictor (RungeKutta method):
        # В методе РунгеКутта за t0 мы берем ту переменную, которую мы перебираем на промежутке (то, от чего зависит наша функция)
        y_predictor = y_prev + h * RungeKutta_3_system([y0], x0, x_end, h)[0][0]
        # Corrector (implicit Adams-Moulton method):
        y[i] = y_prev + h / 2 * (f(x_prev, y_prev) + f(x[i], y_predictor))
    return x, y

# Initial conditions
x0, y0 = 0, 1
h = 0.01
x_end = 2

# Solve the equation
x, y = adams_moulton(x0, y0, h, x_end)

# Plot the results
plt.figure(figsize=(8, 6))
plt.plot(x, y, label="Adams-Moulton", color="blue")
plt.title("Solution using Adams-Moulton with RungeKutta")
plt.xlabel("x")
plt.ylabel("y")
plt.grid()
plt.legend()
plt.show()