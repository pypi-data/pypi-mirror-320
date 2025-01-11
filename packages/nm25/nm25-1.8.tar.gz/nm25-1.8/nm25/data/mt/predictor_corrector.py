# Коши Предиктор корректор
import numpy as np
import matplotlib.pyplot as plt

def f(t, y):
    return 2 * y - t**2

def predictor_corrector(f, y0, t0, t_end, h):
    t_values = np.arange(t0, t_end + h, h)
    y_values = np.zeros_like(t_values)

    y_values[0] = y0

    for i in range(1, len(t_values)):
        t = t_values[i - 1]
        y = y_values[i - 1]

        # Predictor (Euler's method)
        y_pred = y + h * f(t, y)

        # Corrector (Trapezoidal rule)
        t_next = t + h
        y_values[i] = y + (h / 2) * (f(t, y) + f(t_next, y_pred))

    return t_values, y_values

# Initial conditions
t0 = 0
t_end = 3
y0 = 1
h = 0.05

# Solve the Cauchy problem
t_values, y_values = predictor_corrector(f, y0, t0, t_end, h)

# Plot the solution
plt.figure(figsize=(10, 6))
plt.plot(t_values, y_values, label="Approximate solution", color="blue")
plt.title("Solution of the Cauchy Problem using Predictor-Corrector Method")
plt.xlabel("t")
plt.ylabel("y(t)")
plt.grid()
plt.legend()
plt.show()