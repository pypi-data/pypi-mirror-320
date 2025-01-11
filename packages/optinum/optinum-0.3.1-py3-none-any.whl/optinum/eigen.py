import numpy as np
import matplotlib.pyplot as plt

def power_method(A: np.ndarray, num_iterations: int = 1000, tol: float = 1e-6) -> tuple:
    """
    Степенной метод для нахождения наибольшего по модулю собственного значения и соответствующего собственного вектора.

    Этот метод применяет итерационный процесс для нахождения наибольшего по модулю собственного значения матрицы A.
    На каждом шаге матрица умножается на вектор, и результат нормализуется. Метод прекращается, когда изменение
    собственного значения на текущем шаге становится меньше заданного порога.

    Параметры:
    -----------
    A : np.ndarray
        Квадратная матрица (размер n x n), для которой нужно найти собственное значение и собственный вектор.

    num_iterations : int, по умолчанию 1000
        Максимальное количество итераций для выполнения степенного метода.

    tol : float, по умолчанию 1e-6
        Порог сходимости. Метод завершится, если изменение собственного значения на текущем шаге
        будет меньше этого значения.

    Возвращает:
    --------
    tuple
        - собственное значение (float)
        - собственный вектор (np.ndarray), соответствующий наибольшему собственному значению

    Пример:
    --------
    >>> A = np.array([[4, 1],
                      [2, 3]])
    >>> lambda_max, eigenvector = power_method(A)
    >>> print(lambda_max)
    5.0
    >>> print(eigenvector)
    [0.57735027 0.57735027]

    В этом примере:
    - Матрица A = [[4, 1], [2, 3]]
    - Функция находит наибольшее по модулю собственное значение (5) и соответствующий собственный вектор.
    """

    # Инициализация начального вектора (случайный вектор)
    A = np.array(A)
    n = A.shape[0]
    x = np.random.rand(n)

    # Нормируем начальный вектор
    x = x / np.linalg.norm(x)

    # Инициализация переменной для хранения предыдущего собственного значения
    prev_lambda = 0

    for i in range(num_iterations):
        # Умножаем матрицу A на текущий вектор x
        x_next = np.dot(A, x)

        # Нормируем новый вектор
        x_next = x_next / np.linalg.norm(x_next)

        # Вычисляем приближенное собственное значение (скалярное произведение)
        lambda_ = np.dot(x_next.T, np.dot(A, x_next))

        # Проверяем сходимость (если изменение собственного значения меньше порога, выходим)
        if np.abs(lambda_ - prev_lambda) < tol:
            break

        # Обновляем значения для следующей итерации
        x = x_next
        prev_lambda = lambda_

    return lambda_, x_next

def qr_decompose(A: np.ndarray) -> tuple[list, list]:
    """
    Выполняет QR-разложение матрицы используя процесс Грама-Шмидта.

    Параметры
    ----------
    A : np.ndarray
        Матрица для разложения

    Возвращает
    ----------
    tuple[np.ndarray, np.ndarray]
        Q : ортогональная матрица
        R : верхнетреугольная матрица

    Пример
    -------
    >>> A = np.array([[1, -1], [1, 1]])
    >>> Q, R = qr_decompose(A)
    """
    n = len(A) 
    Q = [[0.0] * n for _ in range(n)] 
    R = [[0.0] * n for _ in range(n)] 
 
    for j in range(n): 
        v = [A[i][j] for i in range(n)] 
        for i in range(j): 
            R[i][j] = sum(Q[k][i] * A[k][j] for k in range(n)) 
            v = [v[k] - R[i][j] * Q[k][i] for k in range(n)] 
        R[j][j] = sum(v[k] ** 2 for k in range(n)) ** 0.5 
        for k in range(n): 
            Q[k][j] = v[k] / R[j][j] 
 
    return Q, R 
 
def qr_algorithm(A: np.ndarray, tol: float = 1e-10, max_iterations: int = 1000) -> tuple[list, list]:
    """
    Вычисляет собственные значения и собственные векторы матрицы используя QR-алгоритм.

    Параметры
    ----------
    A : np.ndarray
        Квадратная матрица
    tol : float
        Допуск для сходимости
    max_iterations : int
        Максимальное количество итераций

    Возвращает
    ----------
    tuple[np.ndarray, np.ndarray]
        eigenvalues : массив собственных значений
        eigenvectors : матрица собственных векторов

    Пример
    -------
    >>> A = np.array([[4, 1], [2, 3]])
    >>> eigenvals, eigenvecs = qr_algorithm(A)
    """
    n = len(A) 
    Q_total = [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)] 
 
    for _ in range(max_iterations): 
        Q, R = qr_decompose(A) 
        A = [[sum(R[i][k] * Q[k][j] for k in range(n)) for j in range(n)] for i in range(n)] 
        Q_total = [[sum(Q_total[i][k] * Q[k][j] for k in range(n)) for j in range(n)] for i in range(n)] 
 
        # Check convergence by looking at off-diagonal elements 
        off_diagonal = sum(abs(A[i][j]) for i in range(n) for j in range(n) if i != j) 
        if off_diagonal < tol: 
            break 
 
    eigenvalues = [A[i][i] for i in range(n)] 
    eigenvectors = Q_total 
    return eigenvalues, eigenvectors

def compute_spectrum(A: np.ndarray) -> list:
    """
    Вычисляет спектр (набор собственных значений) матрицы.

    Параметры
    ----------
    A : np.ndarray
        Квадратная матрица

    Возвращает
    ----------
    np.ndarray
        Массив собственных значений

    Пример
    -------
    >>> A = np.array([[4, 1], [2, 3]])
    >>> spectrum = compute_spectrum(A)
    """
    eigenvalues, _ = qr_algorithm(A) 
    return eigenvalues 
 
def compute_pseudospectrum(A: np.ndarray, epsilon: float = 1e-3, 
                         grid_points: int = 100) -> tuple[list, list, list]:
    """
    Вычисляет псевдоспектр матрицы.

    Параметры
    ----------
    A : np.ndarray
        Квадратная матрица
    epsilon : float
        Уровень возмущения для псевдоспектра
    grid_points : int
        Количество точек сетки для визуализации

    Возвращает
    ----------
    tuple[np.ndarray, np.ndarray, np.ndarray]
        X : сетка действительных частей
        Y : сетка мнимых частей
        pseudospectrum : сетка значений псевдоспектра

    Пример
    -------
    >>> A = np.array([[4, 1], [2, 3]])
    >>> X, Y, ps = compute_pseudospectrum(A)
    """
    n = len(A) 
    x = [i / grid_points * 4 - 2 for i in range(grid_points)] 
    y = [i / grid_points * 4 - 2 for i in range(grid_points)] 
    X, Y = [[0.0] * grid_points for _ in range(grid_points)], [[0.0] * grid_points for _ in range(grid_points)] 
    pseudospectrum = [[0.0] * grid_points for _ in range(grid_points)] 
 
    for i in range(grid_points): 
        for j in range(grid_points): 
            z = x[i] + 1j * y[j] 
            try: 
                inv_norm = 1.0 / sum(abs(A[k][l] - (z if k == l else 0.0)) for k in range(n) for l in range(n)) 
            except ZeroDivisionError: 
                inv_norm = float('inf') 
            pseudospectrum[i][j] = inv_norm 
            X[i][j], Y[i][j] = x[i], y[j] 
 
    return X, Y, pseudospectrum 
 
def find_min_max_eigenvalues(A: np.ndarray): 
    """ 
    Найти минимальное и максимальное собственные значения матрицы. 
 
    Параметры: 
    A (list of list): Квадратная матрица. 
 
    Возвращает: 
    min_eigenvalue (float): Минимальное собственное значение. 
    max_eigenvalue (float): Максимальное собственное значение. 
    """ 
    eigenvalues = compute_spectrum(A) 
    return min(eigenvalues), max(eigenvalues)

def plot_pseudospectrum(A: np.ndarray) -> None:
    """
    Визуализирует псевдоспектр матрицы.

    Параметры
    ----------
    A : np.ndarray
        Квадратная матрица

    Пример
    -------
    >>> A = np.array([[4, 1], [2, 3]])
    >>> plot_pseudospectrum(A)
    """
    # Спектр 
    spectrum = compute_spectrum(A) 
    print("Spectrum:", spectrum) 
 
    # Псевдоспектр 
    X, Y, pseudospectrum = compute_pseudospectrum(A) 
    plt.contourf(X, Y, [[abs(value) for value in row] for row in pseudospectrum], levels=50, cmap="viridis") 
    plt.colorbar(label="Pseudospectrum Magnitude") 
    plt.title("Pseudospectrum") 
    plt.xlabel("Re") 
    plt.ylabel("Im") 
    plt.show()

def schur_decomposition(A, tol=1e-10, max_iter=1000):
    """
    Функция для разложения Шура матрицы A.

    Параметры:
    A : np.ndarray
        Квадратная матрица для разложения.
    tol : float
        Допустимая ошибка для остановки итераций.
    max_iter : int
        Максимальное количество итераций.

    Возвращает:
    U : np.array()
        Унитарная матрица.
    T : np.array()
        Верхняя треугольная матрица.
    U*: np.array()
      эрмитово-сопряженная матрица

    Пример использования:

    >>> A = np.array([[1, -1, 1],
                [2, 3, 9],
                [3, 5, 5]], dtype = float)

    >>> U, T, U_conjugate = schur_decomposition(A)
    >>> A_reconstructed = U @ T @ U_conjugate
    >>> print(A_reconstructed)

    [[ 1.05975064 -1.02519765  1.03695278]
    [ 2.04868027  2.82188809  9.12925175]
    [ 3.05507456  4.90388791  5.07457154]]
    """
    def zero(m, n):
      z = [[0 for _ in range(n)] for _ in range(m)] # нулевая матрица
      return z

    def transpose(m): # функция транспонирования матрицы
      return list(map(list, zip(*m)))

    def vector_norm(v): # нормализация
      return sum(x ** 2 for x in v) ** 0.5

    def multiply_v(a, b): # скалярное произведение векторов
      return sum([a[i] * b[i] for i in range(len(a))])

    def multiply(a, b):
        rows_a, cols_a = len(a), len(a[0])
        rows_b, cols_b = len(b), len(b[0])

        result = np.zeros((rows_a, cols_b))

        for i in range(rows_a):
            for j in range(cols_b):
                for k in range(cols_a):
                    result[i, j] += a[i, k] * b[k, j]

        return result

    def qr_razloj(A):

        m = len(A)
        n = len(A[0])
        Q = zero(m, n)


      # векторы-столбцы заданной матрицы A
        a = []
        for i in range(len(A[0])):
            a.append(transpose(A)[i])


      # чтобы в дальнейшем найти векторы-столбцы матрицы Q, найдём промежуточные векторы u
        u = [a[0]]
        for i in range(n-1):
            v_ = a[i+1]
            u_new = a[i+1]
            for j in range(i+1):
                scale = multiply_v(u[j], v_) / multiply_v(u[j], u[j])
                for r in range(len(u_new)):
                    u_new[r] -= scale * u[j][r]
            u.append(u_new)

      # найдём векторы-столбцы матрицы Q
        e = []
        for i in range(n):
            e_ = u[i]
            norm = vector_norm(e_)
            for j in range(len(e_)):
                e_[j] /= norm
            e.append(e_)

      # Из полученных векторов составляем по столбцам матрицу Q
        Q = transpose(e)

      # Найдем матрицу R=Q^{-1}*A=Q^{T}*A
        R = [[0]*m for _ in range(n)]
        for i in range(n):
            for j in range(i, m):
                A_j = [A[k][j] for k in range(n)]
                Q_i = [Q[k][i] for k in range(n)]
                R[i][j] = multiply_v(A_j, Q_i)

      # округляем значения матриц до адекватного числа знаков
        for i in range(n):
            for j in range(n):
                Q[i][j] = round(Q[i][j], 2)
                R[i][j] = round(R[i][j], 2)

        return Q, R

    n = len(A)
    Q = np.eye(n)  # Начальная унитарная матрица
    A_k = A.copy()  # Копия исходной матрицы

    for _ in range(max_iter):
        # QR-разложение
        Q_k, R_k = qr_razloj(A_k)
        Q_k = np.array(Q_k)
        R_k = np.array(R_k)

        # Обновление A_k
        A_k = multiply(R_k, Q_k)

        # Обновление Q
        Q = multiply(Q, Q_k)

        # # Проверка на сходимость (разница между текущей и предыдущей матрицами)
        # if np.linalg.norm(np.triu(A_k, 1)) < tol:
        #     break

    # Вычисление сопряженной матрицы U*
    U_conjugate = transpose(Q)

    return Q, A_k, U_conjugate