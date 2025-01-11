# # 16. Метод центральной разницы



def central_diff(f, x, h=1e-5):
    return (f(x + h) - f(x - h)) / h / 2




def forward_diff(f, x, h=1e-5):
    # Метод прямой разницы
    return (f(x + h) - f(x)) / h




def backward_diff(f, x, h=1e-5):
    # Метод обратной разницы
    return (f(x) - f(x - h)) / h




def f(x):
    return x**2

x = 2
print(central_diff(f, x))
print(forward_diff(f, x))
print(backward_diff(f, x))