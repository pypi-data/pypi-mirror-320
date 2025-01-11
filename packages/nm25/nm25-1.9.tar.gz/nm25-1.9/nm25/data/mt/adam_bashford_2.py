# метод Адамса-Бэшфорта
def adams_bashforth(f, y0, t0, t_end, h):
    """
    Явный метод Адамса-Бэшфорта (AB2)
    
    :param f: правая часть дифференциального уравнения dy/dt = f(t, y)
    :param y0: начальное условие
    :param t0: начальное время
    :param t_end: конечное время
    :param h: шаг
    :return: список значений времени и решения
    """
    t_values = [t0]
    y_values = [y0]
    
    # Начальный шаг с использованием метода Эйлера
    t1 = t0 + h
    y1 = y0 + h * f(t0, y0)
    t_values.append(t1)
    y_values.append(y1)
    
    # Основной цикл
    while round(t_values[-1], 4) < t_end:
        t_prev, t_curr = t_values[-2], t_values[-1]
        y_prev, y_curr = y_values[-2], y_values[-1]
        
        # Формула AB2
        t_next = t_curr + h
        y_next = y_curr + h * (1.5 * f(t_curr, y_curr) - 0.5 * f(t_prev, y_prev))
        
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
t_ab, y_ab = adams_bashforth(f, y0, t0, t_end, h)
print("Метод Адамса-Бэшфорта:")
for t, y in zip(t_ab, y_ab):
    print(f"t = {t:.2f}, y = {y:.4f}")