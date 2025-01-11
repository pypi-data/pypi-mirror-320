# Адам Мультон
import matplotlib.pyplot as plt
import numpy as np

def f(x, y):
    return x**2 + y**2

def adams_moulton(x0, y0, h, x_end):
    n = int((x_end - x0) / h) + 1
    x = np.linspace(x0, x_end, n)
    y = np.zeros(n)
    
    y[0] = y0

    for i in range(1, n):
        x_prev, y_prev = x[i - 1], y[i - 1]
        # Predictor (Euler method):
        y_predictor = y_prev + h * f(x_prev, y_prev)
        # Corrector (implicit Adams-Moulton method):
        y[i] = y_prev + h / 2 * (f(x_prev, y_prev) + f(x[i], y_predictor))

    return x, y

# Initial conditions
x0, y0 = 0, 1
h = 0.02
x_end = 1

# Solve the equation
x, y = adams_moulton(x0, y0, h, x_end)

# Plot the results
plt.figure(figsize=(8, 6))
plt.plot(x, y, label="Adams-Moulton", color="blue")
plt.title("Solution of dy/dx = x^2 + y^2 using Adams-Moulton")
plt.xlabel("x")
plt.ylabel("y")
plt.grid()
plt.legend()
plt.show()
