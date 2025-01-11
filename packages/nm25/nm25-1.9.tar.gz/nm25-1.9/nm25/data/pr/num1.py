# # Наивное умножение матрицы на вектор и на матрицу



def matrix_vector_multiplier(A, B):
    if len(A[0]) != len(B):
        print("Can't multiply.")
        return

    matrix = False
    if isinstance(B[0], list):
        matrix = True

    if matrix:
        m, n, p = len(A), len(B), len(B[0])
        C = [[0] * p for _ in range(m)]
        for i in range(m):  # строки A
            for j in range(p):  # столбцы B
                for k in range(n):  # общий размер
                    C[i][j] += A[i][k] * B[k][j]
        return C
    else:
        C = []
        for row in A:
            y_i = sum(row[j] * B[j] for j in range(len(B)))
            C.append(y_i)
        return C




A = [[1, 2, 3],[4, 5, 6],[7, 8, 9]]
B = [1, 0, -1]
print(matrix_vector_multiplier(A, B))
A = [[1, 2, 3],[4, 5, 6]]
B = [[7, 8],[9, 10],[11, 12]]
print(matrix_vector_multiplier(A, B))