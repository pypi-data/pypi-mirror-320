# Метод непосредственного развертывания
from itertools import permutations

def count_inv(mas):
    """
    Количество перестановок
    """
    s = 0
    for i in range(len(mas)):
        for j in range(i, len(mas)):
            if mas[i] > mas[j]:
                s += 1
    return s

def det(mat):
    """
    Определитель матрицы
    """
    d = 0
    for comb in permutations(range(len(mat))):
        v = 1
        for i, j in enumerate(comb):
            v *= mat[i][j]
        d += v * (-1) ** count_inv(comb)
    return d


A = np.array([[6, 2, 1, 4],
              [2, 7, 3, 1],
              [1, 3, 8, 2],
              [4, 1, 2, 2]])

func = lambda x: det(A - np.eye(4)*x)
x = np.arange(-1, 15, 0.1) # определяем в каких числах находятся корни
plt.plot(x, list(map(func, x)))
plt.plot([min(x), max(x)], [0, 0])

#Можно использовать крутые методы типа бисекции и тд, но здесь перебор простой
h = 0.001
for x in np.arange(-1, 15, h): # смотрим на график и сами определяем границы
    if func(x) * func(x+h) < 0 or func(x) == 0:
        print("Собственное значение примерно равно:", x)
