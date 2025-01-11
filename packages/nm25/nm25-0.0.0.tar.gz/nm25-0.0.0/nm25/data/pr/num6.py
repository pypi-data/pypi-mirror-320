# # Степенной метод



import random

def outer_product(v1, v2):
    """Вычисляет внешнее произведение двух векторов."""
    n = len(v1)
    return [[v1[i] * v2[j] for j in range(n)] for i in range(n)]

def subtract_matrices(A, B):
    """Вычитает одну матрицу из другой."""
    n = len(A)
    return [[A[i][j] - B[i][j] for j in range(n)] for i in range(n)]

def matrix_vector_multiply(A, v):
    """Перемножение матрицы и вектора."""
    return [sum(A[i][j] * v[j] for j in range(len(v))) for i in range(len(A))]

def vector_norm(v):
    """Евклидова норма вектора."""
    return sum(x**2 for x in v) ** 0.5

def dot_product(v1, v2):
    """Скалярное произведение двух векторов."""
    return sum(x * y for x, y in zip(v1, v2))

def power_method(A, num_iterations=1000, tolerance=1e-10):
    """
    Реализация степенного метода для нахождения наибольшего собственного значения и собственного вектора.
    :param A: Квадратная матрица (список списков).
    :param num_iterations: Максимальное количество итераций.
    :param tolerance: Допустимая погрешность для сходимости.
    :return: Наибольшее собственное значение и собственный вектор.
    """
    # Генерация случайного начального вектора
    b_k = [random.random() for _ in range(len(A[0]))]
    
    for _ in range(num_iterations):
        # Умножение матрицы на вектор
        b_k1 = matrix_vector_multiply(A, b_k)
        
        # Нормализация вектора
        b_k1_norm = vector_norm(b_k1)
        b_k1 = [x / b_k1_norm for x in b_k1]
        
        # Проверка сходимости
        if vector_norm([b_k1[i] - b_k[i] for i in range(len(b_k))]) < tolerance:
            break
        
        b_k = b_k1
    
    # Вычисление собственного значения
    eigenvalue = dot_product(b_k, matrix_vector_multiply(A, b_k)) / dot_product(b_k, b_k)
    return eigenvalue, b_k

def find_all_eigenvalues(A, num_iterations=1000, tolerance=1e-10):
    """
    Находит все собственные значения матрицы, используя степенной метод и дефляцию.
    
    :param A: Квадратная матрица (список списков).
    :param num_iterations: Максимальное количество итераций для степенного метода.
    :param tolerance: Допустимая погрешность для сходимости.
    :return: Список всех собственных значений.
    """
    n = len(A)
    A_copy = [row[:] for row in A]  # Создаем копию матрицы
    eigenvalues = []
    eigenvectors = []
    
    for _ in range(n):
        # Находим наибольшее собственное значение и собственный вектор
        eigenvalue, eigenvector = power_method(A_copy, num_iterations, tolerance)
        eigenvalues.append(eigenvalue)
        eigenvectors.append(eigenvector)
        
        # Вычисляем матрицу дефляции
        eigenvector_norm = vector_norm(eigenvector)
        eigenvector = [x / eigenvector_norm for x in eigenvector]  # Нормализация
        outer = outer_product(eigenvector, eigenvector)
        A_copy = subtract_matrices(A_copy, [[eigenvalue * outer[i][j] for j in range(n)] for i in range(n)])
    
    return eigenvalues, eigenvectors




# Пример использования
A = [[4, 2],
     [2, 3]]

eigenvalues, eigenvectors = find_all_eigenvalues(A)
for i in range(len(A)):
    print("Собственные значения:", eigenvalues[i])
    print('Собственные вектора:', eigenvectors[i])
    print()