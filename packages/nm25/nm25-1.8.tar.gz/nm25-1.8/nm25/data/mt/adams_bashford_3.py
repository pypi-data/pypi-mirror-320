# метод Адамса-Бэшфорта 3-го порядка
def adams_bashforth_3(f, y0, t0, t_end, h):
    """
    Явный метод Адамса-Бэшфорта 3-го порядка (AB3)
    
    :param f: правая часть дифференциального уравнения dy/dt = f(t, y)
    :param y0: начальное условие
    :param t0: начальное время
    :param t_end: конечное время
    :param h: шаг
    :return: список значений времени и решения
    """
    t_values = [t0]
    y_values = [y0]
    
    # Для первых 2 точек используем метод Рунге-Кутты 4-го порядка
    def runge_kutta_4(f, t, y, h):
        k1 = f(t, y)
        k2 = f(t + h / 2, y + h * k1 / 2)
        k3 = f(t + h / 2, y + h * k2 / 2)
        k4 = f(t + h, y + h * k3)
        return y + h * (k1 + 2 * k2 + 2 * k3 + k4) / 6
    
    for _ in range(2):
        t_next = t_values[-1] + h
        y_next = runge_kutta_4(f, t_values[-1], y_values[-1], h)
        t_values.append(t_next)
        y_values.append(y_next)
    
    # Основной цикл метода AB3
    while t_values[-1] < t_end:
        t_next = t_values[-1] + h
        y_next = y_values[-1] + h / 12 * (
            23 * f(t_values[-1], y_values[-1])
            - 16 * f(t_values[-2], y_values[-2])
            + 5 * f(t_values[-3], y_values[-3])
        )
        t_values.append(t_next)
        y_values.append(y_next)
    
    return t_values, y_values

def f(t, y):
    return t + y - 2

# Параметры
y0 = 1
t0 = 0
t_end = 2
h = 0.2

# Применение методов
t_ab, y_ab = adams_bashforth_3(f, y0, t0, t_end, h)
print("Метод Адамса-Бэшфорта:")
for t, y in zip(t_ab, y_ab):
    print(f"t = {t:.2f}, y = {y:.4f}")