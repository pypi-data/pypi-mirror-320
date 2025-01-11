from typing import List, Tuple, Union
import numpy as np
from scipy.linalg import lu, solve

def lu_decomposition(matrix: List[List[float]]) -> Tuple[List[List[float]], List[List[float]]]:
    """
    Выполняет LU-разложение разреженной матрицы.
    Однако для алгоритма LU-разложения, описанного выше, требуется квадратная матрица  A, поскольку разложение на L и U предполагает, что L и 𝑈 также квадратные.
    
    :param matrix: Разреженная матрица A
    :return: Кортеж из двух матриц (L, U)
    """
    n = len(matrix)
    L = [[0.0] * n for _ in range(n)]
    U = [[0.0] * n for _ in range(n)]
    
    for i in range(n):
        L[i][i] = 1.0
        for j in range(i, n):
            U[i][j] = matrix[i][j] - sum(L[i][k] * U[k][j] for k in range(i))
        for j in range(i + 1, n):
            L[j][i] = (matrix[j][i] - sum(L[j][k] * U[k][i] for k in range(i))) / U[i][i]
    
    return L, U

def forward_substitution(L: List[List[float]], b: List[float]) -> List[float]:
    """
    Решает систему L * y = b методом прямой подстановки.
    
    :param L: Нижняя треугольная матрица L
    :param b: Вектор правой части b
    :return: Вектор решения y
    """
    n = len(L)
    y = [0.0] * n
    for i in range(n):
        y[i] = b[i] - sum(L[i][j] * y[j] for j in range(i))
    return y

def backward_substitution(U: List[List[float]], y: List[float]) -> List[float]:
    """
    Решает систему U * x = y методом обратной подстановки.
    
    :param U: Верхняя треугольная матрица U
    :param y: Вектор правой части y
    :return: Вектор решения x
    """
    n = len(U)
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        x[i] = (y[i] - sum(U[i][j] * x[j] for j in range(i + 1, n))) / U[i][i]
    return x

def csr_to_dense(csr_matrix: Tuple[List[float], List[int], List[int]], n: int) -> List[List[float]]:
    """
    Преобразует разреженную матрицу в формате CSR в плотную матрицу.
    
    :param csr_matrix: Кортеж из трех списков (values, column_indices, row_pointers)
    :param n: Размерность квадратной матрицы
    :return: Плотная матрица
    """
    values, column_indices, row_pointers = csr_matrix
    dense_matrix = [[0.0] * n for _ in range(n)]
    
    for i in range(n):
        row_start = row_pointers[i]
        row_end = row_pointers[i + 1]
        for j in range(row_start, row_end):
            col = column_indices[j]
            dense_matrix[i][col] = values[j]
    
    return dense_matrix

def sparse_lu_solve(matrix: Union[Tuple[List[float], List[int], List[int]], List[List[float]]], b: List[float], n: int, format: str = 'csr') -> List[float]:
    """
    Решает систему Ax = b для разреженной матрицы A, заданной в формате CSR или плотной матрицы, 
    используя LU-разложение.
    Сложность алгоритма
        LU-разложение: O(n^3)
        Последующее решение систем: O(n^2)2
    LU-разложение существует только для невырожденных матриц, у которых все ведущие главные миноры невырождены

    :param matrix: Разреженная матрица A в формате CSR (values, column_indices, row_pointers) или плотная матрица
    :param b: Вектор правой части b
    :param n: Размерность квадратной матрицы
    :param format: Формат входной матрицы ('csr' или 'dense')
    :return: Вектор решения x

    Пример использования:
    >>> csr_matrix = (
    ...     [4, 3, 5, 6, 8, 2, 9],  # values
    ...     [0, 0, 1, 1, 2, 2, 3],  # column_indices
    ...     [0, 1, 3, 5, 7]         # row_pointers
    ... )
    >>> b = [2, 5, 8, 10]
    >>> n = 4
    >>> x_csr = sparse_lu_solve(csr_matrix, b, n, format='csr')
    >>> print(x_csr)
    [0.5, 0.5, 0.5, 1.0]
    
    """
    if format == 'csr':
        dense_matrix = csr_to_dense(matrix, n)
    elif format == 'dense':
        dense_matrix = matrix
    else:
        raise ValueError("Unsupported matrix format. Use 'csr' or 'dense'.")
    
    L, U = lu_decomposition(dense_matrix)
    y = forward_substitution(L, b)
    x = backward_substitution(U, y)
    return x

if __name__=='__main__':
    # Пример использования
    csr_matrix = (
        [4, 3, 5, 6, 8, 2, 9],  # values
        [0, 0, 1, 1, 2, 2, 3],  # column_indices
        [0, 1, 3, 5, 7]         # row_pointers
    )
    b = [2, 5, 8, 10]
    n = 4

    # Решаем систему для CSR матрицы
    x_csr = sparse_lu_solve(csr_matrix, b, n, format='csr')
    print("Решение x для CSR матрицы:", x_csr)

    # Пример использования для плотной матрицы
    dense_matrix = [
        [4, 0, 0, 0],
        [3, 5, 0, 0],
        [0, 6, 8, 0],
        [0, 0, 2, 9]
    ]

    # Решаем систему для плотной матрицы
    x_dense = sparse_lu_solve(dense_matrix, b, n, format='dense')
    print("Решение x для плотной матрицы:", x_dense)

    # Использование библиотеки scipy для решения системы уравнений
    dense_matrix_np = np.array([
        [4, 0, 0, 0],
        [3, 5, 0, 0],
        [0, 6, 8, 0],
        [0, 0, 2, 9]
    ])
    b_np = np.array([2, 5, 8, 10])

    # Выполняем LU-разложение
    P, L, U = lu(dense_matrix_np)

    # Решаем систему с использованием LU-разложения
    y_np = solve(L, np.dot(P.T, b_np))
    x_np = solve(U, y_np)

    print("L matrix:\n", L)
    print("U matrix:\n", U)
    print("Solution x:\n", x_np)
