# # Метод итераций



def vector_norm(v):
    """
    Вычисляет евклидову норму вектора вручную.
    """
    return sum(x**2 for x in v) ** 0.5

def matrix_vector_multiply(A, v):
    """
    Умножение матрицы на вектор вручную.
    """
    n = len(A)
    result = [0] * n
    for i in range(n):
        result[i] = sum(A[i][j] * v[j] for j in range(len(v)))
    return result

def dot_product(v1, v2):
    """
    Вычисление скалярного произведения двух векторов вручную.
    """
    return sum(v1[i] * v2[i] for i in range(len(v1)))

def power_iteration_basic(A, tol=1e-6, max_iter=1000):
    """
    Метод степенных итераций для нахождения наибольшего собственного значения и вектора.
    Реализован с использованием только базовых операций.
    """
    n = len(A)
    # Начальный произвольный вектор
    X = [1] * n  # Можно заменить на любой ненулевой вектор
    X = [x / vector_norm(X) for x in X]  # Нормируем начальный вектор

    eigenvalue_old = 0

    for iteration in range(max_iter):
        # Умножение матрицы на вектор
        X_new = matrix_vector_multiply(A, X)
        # Нормировка нового вектора
        X_new_norm = vector_norm(X_new)
        X_new = [x / X_new_norm for x in X_new]
        
        # Оценка собственного значения через Рэйлиев частный
        eigenvalue = dot_product(X_new, matrix_vector_multiply(A, X_new))
        
        # Проверка сходимости
        if abs(eigenvalue - eigenvalue_old) < tol:
            break
        
        # Обновление вектора и значения
        X = X_new
        eigenvalue_old = eigenvalue

    return eigenvalue, X

# Пример использования
A = np.array([[7, 2, 1,5], [2, 8, 3, 1], [1, 3, 6, 2], [5, 1, 2, 3]], dtype=float)

eigenvalue, eigenvector = power_iteration_basic(A, tol=1e-8)

print("Наибольшее собственное значение:", eigenvalue)
print("Соответствующий собственный вектор:", eigenvector)