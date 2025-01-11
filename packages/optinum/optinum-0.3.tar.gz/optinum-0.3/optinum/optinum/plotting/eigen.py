import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple

def plot_gershgorin_circles(A: np.ndarray) -> None:
    """
    Вычисляет и отображает круги Гершгорина для матрицы.
    
    Параметры
    ----------
    A : np.ndarray
        Входная матрица для анализа
        
    Возвращает
    ----------
    None
        Отображает график кругов Гершгорина и собственных значений
        
    Пример
    -------
    >>> A = np.array([[10, -1, 0, 1],
    ...               [0.2, 8, 0.2, 0.2],
    ...               [1, 1, 2, 1],
    ...               [-1, -1, -1, -11]])
    >>> plot_gershgorin_circles(A)
    """
    # Вычисление координат кругов Гершгорина
    centers: List[Tuple[float, float]] = []
    for i in range(len(A)):
        center = A[i, i]  # центр круга - элемент на диагонали
        radius = np.sum(np.abs(A[i])) - np.abs(center)  # радиус - сумма модулей вне диагонали
        centers.append((center, radius))
    
    # Создание графика
    plt.figure(figsize=(10, 10))
    
    # Отрисовка кругов и центров
    for center, radius in centers:
        plt.plot(center, 0, 'ro')  # центр круга
        circle = plt.Circle((center, 0), radius, fill=False, color='blue')
        plt.gca().add_patch(circle)
    
    # Отрисовка собственных значений
    eigenvals = np.linalg.eigvals(A)
    plt.plot(eigenvals.real, eigenvals.imag, 'gx', label='Eigenvalues')
    
    # Настройка графика
    plt.grid(True)
    plt.axis('equal')
    plt.xlabel('Re(λ)')
    plt.ylabel('Im(λ)')
    plt.title('Круги Гершгорина и собственные значения')
    plt.legend()
    
    plt.show()
if __name__ == "__main__":
    A = np.array([[10, -1, 0, 1],
                  [0.2, 8, 0.2, 0.2],
                  [1, 1, 2, 1],
                  [-1, -1, -1, -11]])
    plot_gershgorin_circles(A)