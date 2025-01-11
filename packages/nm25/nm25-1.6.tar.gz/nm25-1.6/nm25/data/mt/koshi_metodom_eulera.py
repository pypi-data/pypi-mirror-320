# Коши методом Эйлера
import matplotlib.pyplot as plt
import numpy as np

#Задача Коши методом Эйлера
def euler(f, x0, y0, x, h):
    n = round((x - x0) / h)
    x = x0
    y = y0
    x_list = [x]
    y_list = [y]
    for i in range(n):
        y += h * function(x, y)
        x += h
        y_list.append(y)
        x_list.append(x)
    return x_list, y_list, y

def function(x, y):
    return y**2 - x**2

x0 = 0
y0 = 0.5
x = 4
h = 0.05

x_list, y_list, y = euler(function, x0, y0, x, h)
print(y)
plt.plot(x_list, y_list)