import matplotlib.pyplot as plt
import numpy as np
from typing import Callable, Optional

def plot_ode_solution(x_vals: np.ndarray, y_vals: np.ndarray, 
                     exact_solution: Optional[Callable] = None,
                     method_name: str = "Numerical solution",
                     x0: Optional[float] = None,
                     x_end: Optional[float] = None) -> None:
    """
    Построение графика решения ОДУ с возможностью сравнения с точным решением.

    Параметры
    ----------
    x_vals : np.ndarray
        Массив значений x
    y_vals : np.ndarray
        Массив значений y (численное решение)
    exact_solution : Callable, optional
        Функция точного решения (если известно)
    method_name : str, optional
        Название метода решения для легенды
    x0 : float, optional
        Начальное значение x для точного решения
    x_end : float, optional
        Конечное значение x для точного решения

    Пример
    -------
    >>> import numpy as np
    >>> def exact_solution(x):
    ...     return -x - 1 + 2 * np.exp(x)
    >>> x_vals = np.array([0, 0.1, 0.2, 0.3])
    >>> y_vals = np.array([1.0, 1.2, 1.5, 1.9])
    >>> plot_ode_solution(x_vals, y_vals, 
    ...                   exact_solution=exact_solution,
    ...                   method_name="Метод Эйлера",
    ...                   x0=0, x_end=0.3)
    """
    plt.figure(figsize=(10, 6))
    plt.plot(x_vals, y_vals, 'o-', label=method_name)

    if exact_solution is not None:
        if x0 is None:
            x0 = x_vals[0]
        if x_end is None:
            x_end = x_vals[-1]
            
        x_exact = np.linspace(x0, x_end, 100)
        y_exact = exact_solution(x_exact)
        plt.plot(x_exact, y_exact, label="Точное решение")

    plt.xlabel("x")
    plt.ylabel("y")
    plt.title("Сравнение численного и точного решения")
    plt.legend()
    plt.grid()
    plt.show()

def plot_ode_methods_comparison(methods_results: dict, 
                              exact_solution: Optional[Callable] = None,
                              x0: Optional[float] = None,
                              x_end: Optional[float] = None) -> None:
    """
    Сравнение нескольких методов решения ОДУ на одном графике.

    Параметры
    ----------
    methods_results : dict
        Словарь с результатами разных методов в формате
        {'название метода': (x_vals, y_vals)}
    exact_solution : Callable, optional
        Функция точного решения (если известно)
    x0 : float, optional
        Начальное значение x для точного решения
    x_end : float, optional
        Конечное значение x для точного решения

    Пример
    -------
    >>> import numpy as np
    >>> def exact_solution(x):
    ...     return -x - 1 + 2 * np.exp(x)
    >>> # Предположим, у нас есть результаты разных методов
    >>> x1 = np.array([0, 0.1, 0.2])
    >>> y1 = np.array([1.0, 1.2, 1.5])
    >>> x2 = np.array([0, 0.1, 0.2])
    >>> y2 = np.array([1.0, 1.21, 1.52])
    >>> methods_results = {
    ...     "Метод Эйлера": (x1, y1),
    ...     "Метод Рунге-Кутты": (x2, y2)
    ... }
    >>> plot_ode_methods_comparison(methods_results, 
    ...                            exact_solution=exact_solution,
    ...                            x0=0, x_end=0.2)
    """
    plt.figure(figsize=(12, 8))
    
    for method_name, (x_vals, y_vals) in methods_results.items():
        plt.plot(x_vals, y_vals, 'o-', label=method_name)

    if exact_solution is not None:
        if x0 is None:
            x0 = min(x[0] for x, _ in methods_results.values())
        if x_end is None:
            x_end = max(x[-1] for x, _ in methods_results.values())
            
        x_exact = np.linspace(x0, x_end, 100)
        y_exact = exact_solution(x_exact)
        plt.plot(x_exact, y_exact, 'k-', label="Точное решение")

    plt.xlabel("x")
    plt.ylabel("y")
    plt.title("Сравнение методов решения ОДУ")
    plt.legend()
    plt.grid()
    plt.show()
