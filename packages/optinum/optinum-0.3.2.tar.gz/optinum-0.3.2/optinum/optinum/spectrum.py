import matplotlib.pyplot as plt

def qr_decompose(A): 
    """ 
    Perform QR decomposition using Gram-Schmidt process. 
 
    Parameters: 
    A (list of list): Matrix to decompose. 
 
    Returns: 
    Q (list of list): Orthogonal matrix. 
    R (list of list): Upper triangular matrix. 
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
 
def qr_algorithm(A, tol=1e-10, max_iterations=1000): 
    """ 
    Computes the eigenvalues and eigenvectors of a matrix using the QR algorithm. 
 
    Parameters: 
    A (list of list): Square matrix. 
    tol (float): Tolerance for convergence. 
    max_iterations (int): Maximum number of iterations. 
 
    Returns: 
    eigenvalues (list): List of eigenvalues. 
    eigenvectors (list of list): Matrix of eigenvectors. 
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

def compute_spectrum(A): 
    """ 
    Вычислить спектр (набор собственных значений) матрицы. 
 
    Параметры: 
    A (list of list): Квадратная матрица. 
 
    Возвращает: 
    spectrum (list): Список собственных значений. 
    """ 
    eigenvalues, _ = qr_algorithm(A) 
    return eigenvalues 
 
def compute_pseudospectrum(A, epsilon=1e-3, grid_points=100): 
    """ 
    Вычислить псевдоспектр матрицы. 
 
    Параметры: 
    A (list of list): Квадратная матрица. 
    epsilon (float): Уровень возмущения для псевдоспектра. 
    grid_points (int): Количество точек сетки для визуализации. 
 
    Возвращает: 
    X (list): Сетка действительных частей. 
    Y (list): Сетка мнимых частей. 
    pseudospectrum (list of list): Сетка псевдоспектра. 
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
 
def find_min_max_eigenvalues(A): 
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


def plot_pseudospectrum(A):
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