# # Рунге-Кутта 1-4 порядков



def equation(x, y):
    return x + y - 2    

def RungeKutta_1(x0, y0, x, h):
    n = round((x - x0) / h)
    y = y0

    for i in range(1, n + 1):
        y += h * equation(x0, y)
        x0 = x0 + h
    return y




def equation(x, y):
    return x + y - 2    

def RungeKutta_2(x0, y0, x, h):
    n = round((x - x0) / h)
    y = y0

    for i in range(1, n + 1):
        k1 = h * equation(x0, y)
        k2 = h * equation(x0 + 0.5 * h, y + 0.5 * k1)

        y += (k1 + k2) / 2
        x0 = x0 + h
    return y




def equation(x, y):
    return x + y - 2

def RungeKutta_3(x0, y0, x, h):
    n = round((x - x0) / h)
    y = y0

    for i in range(1, n + 1):
        k1 = h * equation(x0, y)
        k2 = h * equation(x0 + h / 2, y + k1 / 2)
        k3 = h * equation(x0 + h, y - k1 + 2 * k2)

        y += (k1 + 4 * k2 + k3) / 6
        x0 += h
    return y




def equation(x, y):
    return y

def RungeKutta_4(x0, y0, x, h):
    n = round((x - x0) / h)
    y = y0

    for i in range(1, n + 1):
        k1 = h * equation(x0, y)
        k2 = h * equation(x0 + h / 2, y + k1 / 2)
        k3 = h * equation(x0 + h / 2, y + k2 / 2)
        k4 = h * equation(x0 + h, y + k3)

        y += (k1 + 2 * k2 + 2 * k3 + k4) / 6
        x0 += h
    return y




x0 = 0
y0 = 1
x = 2
h = 0.2
print('y(x) =', RungeKutta_4(x0, y0, x, h))