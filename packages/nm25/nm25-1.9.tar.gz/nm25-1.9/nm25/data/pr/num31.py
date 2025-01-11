# # Метод вращения



import numpy as np
import matplotlib.pyplot as plt
# для начала реализуем наивный алгоритм умножения матриц, а также функцию для транспонирования

def naive_matrix_multiply(A, B):
    result = np.zeros((A.shape[0], B.shape[1]))
    
    for i in range(A.shape[0]):
        for j in range(B.shape[1]):
            for k in range(A.shape[1]):
                result[i, j] += A[i, k] * B[k, j]
                
    return result

def transpose_matrix(A):
    result = np.zeros_like(A)
    
    for i in range(A.shape[0]):
        for j in range(A.shape[1]):
            result[j, i] = A[i, j]
            
    return result


def rotate_method(A, epsilon=0.001): # теперь реализуем сам алгоритм
    A = np.array(A).copy()
    n = A.shape[0]
    V = np.eye(n)  # для накопления собственных векторов

    while True: # поиск максимального недиагонального элемента в верхней треугольной матрице
        max_val = 0
        p, q = -1, -1
        for i in range(n):
            for j in range(i + 1, n):
                if abs(A[i, j]) > max_val:
                    max_val = abs(A[i, j])
                    p, q = i, j
        
        # проверка на достижение точности (завершение алгоритма)
        if max_val < epsilon:
            break

        if A[p, p] == A[q, q]: # вычисление угла поворота
            phi = np.pi / 4
        else:
            phi = 0.5 * np.arctan(2 * A[p, q] / (A[p, p] - A[q, q]))

        H = np.eye(n)   # создание матрицы вращения H
        H[p, p] = np.cos(phi)
        H[q, q] = np.cos(phi)
        H[p, q] = -np.sin(phi)
        H[q, p] = np.sin(phi)

        # Обновление A и V на основе написанных ранее алгоритмов
        A = naive_matrix_multiply(naive_matrix_multiply(transpose_matrix(H), A), H)
        V = naive_matrix_multiply(V, H)

    eigenvalues = np.array([A[i, i] for i in range(n)]) # собственные значения на диагонали матрицы A
    eigenvectors = V # собственные векторы в столбцах матрицы V
    
    return eigenvalues, eigenvectors


A = np.array([[1.6, 0.7, 1.4, 0.4], [0.7, 1.6, 1.4, 0.5], [0.8, 0.3, 1, 2.2], [0.6, 0.3, 1.6, 3.3]])

# применим функцию и получим ответ

print('Ответ (собственные значения):')
print(rotate_method(A)[0])

print('Ответ (собственные векторы):')
print(rotate_method(A)[1])

# отображение собственных значений на комплексной плоскости

plt.figure(figsize=(6, 6))
plt.scatter(rotate_method(A)[0].real, rotate_method(A)[0].imag, color='r')
plt.xlabel('Re')
plt.ylabel('Im')
plt.grid(True)
plt.show()