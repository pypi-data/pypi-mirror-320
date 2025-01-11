# # Метод эйлера



def Euler(n = 10, h = 0.2, x = 0, y = 1):
    # Явный метод эйлера
    x_list = [x]
    y_list = [y]
    for i in range(n):
        y += h * function(x, y)
        x += h
        y_list.append(y)
        x_list.append(x)
    return y

def function(x, y):
    return y + x - 2
print(Euler())




def newton_raphson(f, y, tol=1e-6):
    y_new = float('inf')
    while abs(y_new - y) > tol:
        f_val = f(y)
        df_dy = (f(y + 1e-8) - f_val) / 1e-8
        if abs(df_dy) < 1e-12:  # предотвращение деления на ноль
            raise ValueError("Производная близка к нулю, метод Ньютона может не сойтись.")
        y_new = y - f_val / df_dy
        y = y_new
    return y_new


def implicit_euler(f, x0, y0, x, h):
    # Неявный метод Эйлера
    y_next = y0
    x_next = x0
    n = round((x - x0) / h)
    for i in range(1, n + 1):
        y_prev = y_next
        x_next += h

        def implicit_func(y_next):
            return y_next - y_prev - h * f(x_next, y_next)
        y_next = newton_raphson(implicit_func, y_prev)
    return y_next




x0 = 0
y0 = 1
x = 2
h = 0.2

def f(x, y):
    return x + y - 2

implicit_euler(f, x0, y0, x, h)