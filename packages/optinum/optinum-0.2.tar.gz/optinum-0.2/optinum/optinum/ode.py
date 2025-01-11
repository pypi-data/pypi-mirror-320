from typing import Callable
import numpy as np

def central_diff(y0: float, y1: float, x1: float, h: float, f) -> float:
    """
    Вычисляет следующее значение функции y через дифференциальное уравнение f.

    Параметры
    ----------
    y0 : float
        Первое значение функции y
    y1 : float
        Второе значение функции y
    x1 : float
        Второе значение x
    h : float
        Шаг
    f : function
        Дифференциальное уравнение (с x и y)

    Возвращает
    ----------
    float
        Следующее значение функции y (при х1 + h)

    Пример
    -------
    >>> import math
    >>> def f(y, x):
    ...     return y / (math.cos(x) ** 2)
    >>> n = 10
    >>> h = 0.1
    >>> x = [i * h for i in range(10)]
    >>> y = [0] * n
    >>> y[0] = 2.7183
    >>> y[1] = 2.9901
    >>> for i in range(2, n):
    ...     y[i] = central_diff(y[i-2], y[i-1], x[i-1], h, f)
    >>> print(y)
    """
    return y0 + 2 * h * f(y1, x1)

def solve_ode_central_diff(n: float, h: float, y0: float, y1: float, x0: float, f: Callable) -> float:
    """
    Возвращает решение задачи с одним дифференциальным уравнением через метод центральной разности.

    Параметры
    ----------
    n : int
        Количество значений, которые нужно получить в итоге
    h : float
        Шаг
    y0 : float
        Начальное значение функции y
    y1 : float
        Второе значение функции y
    x0 : float
        Начальное значение x
    f : function
        Дифференциальное уравнение

    Возвращает
    ----------
    list
        Список из n значений функции y (включая два начальных)

    Пример
    -------
    >>> n = 10
    >>> h = 0.1
    >>> y0 = 2.7183
    >>> y1 = 2.9901
    >>> x0 = 0
    >>> solve_ode_central_diff(n, h, y0, y1, x0, f)
    """
    x = [x0 + i * h for i in range(10)]
    y = [0] * n
    y[0] = y0
    y[1] = y1

    for i in range(2, n):
        y[i] = central_diff(y[i-2], y[i-1], x[i-1], h, f)

    return y

def solve_ode_system_central_diff(n: float, h: float, y0: float, y1: float,
                                  z0: float, z1: float, x0: float, f: Callable, g: Callable) -> float:
    """
    Возвращает решение задачи с системой дифференциальных уравнений через метод центральной разности.

    Параметры
    ----------
    n : int
        Количество значений, которые нужно получить в итоге
    h : float
        Шаг
    y0 : float
        Начальное значение функции y
    y1 : float
        Второе значение функции y
    z0 : float
        Начальное значение функции z
    z1 : float
        Второе значение функции z
    x0 : float
        Начальное значение x
    f : function
        Первое дифференциальное уравнение
    g : function
        Второе дифференциальное уравнение

    Возвращает
    ----------
    tuple
        Список из n значений функции y и z (включая два начальных)

    Пример
    -------
    >>> def f(y, x):
    ...     return y / (math.cos(x) ** 2)
    >>> def g(y, x):
    ...     return y / (math.sin(x) ** 3)
    >>> n = 10
    >>> h = 0.1
    >>> y0 = 2.7183
    >>> y1 = 2.9901
    >>> z0 = 1.4142
    >>> z1 = 1.7321
    >>> x0 = 0
    >>> solve_ode_system_central_diff(n, h, y0, y1, z0, z1, x0, f, g)
    """
    x = [x0 + i * h for i in range(10)]
    y = [0] * n
    z = [0] * n
    y[0] = y0
    y[1] = y1
    z[0] = z0
    z[1] = z1

    for i in range(2, n):
        y[i] = central_diff(y[i-2], y[i-1], x[i-1], h, f)
        z[i] = central_diff(z[i-2], z[i-1], x[i-1], h, g)

    return y, z

def solve_ode_euler(f: Callable, x0: float, y0: float, x_end: float, h: float) -> tuple:
    """
    Метод Эйлера для решения ОДУ.

    Параметры
    ----------
    f : Callable
        Правая часть ОДУ (dy/dx = f(x, y))
    x0 : float
        Начальная точка
    y0 : float
        Начальное значение y
    x_end : float
        Конец интервала
    h : float
        Шаг интегрирования

    Возвращает
    ----------
    tuple
        (x_values, y_values) - списки значений x и y

    Пример
    -------
    >>> def f(x, y):
    ...     return -2 * x + y # правая часть ОДУ
    >>> x0, y0 = 0, 1
    >>> x_end = 1
    >>> h = 0.1
    >>> x_vals, y_vals = solve_ode_euler(f, x0, y0, x_end, h)
    """
    x_values = [x0]
    y_values = [y0]

    x, y = x0, y0
    while x < x_end:
        y = y + h * f(x, y)
        x = x + h
        if x < x_end:
            x_values.append(x)
            y_values.append(y)

    return x_values, y_values

def solve_ode_predictor_corrector(f: Callable, x0: float, y0: float, x_end: float, h: float) -> tuple:
    """
    Метод предиктора-корректора для решения ОДУ.

    Параметры
    ----------
    f : Callable
        Правая часть ОДУ (dy/dx = f(x, y))
    x0 : float
        Начальная точка
    y0 : float
        Начальное значение y
    x_end : float
        Конец интервала
    h : float
        Шаг интегрирования

    Возвращает
    ----------
    tuple
        (x_values, y_values) - списки значений x и y

    Пример
    -------
    >>> def f(x, y):
    ...     return x + y
    >>> x0, y0 = 0, 1
    >>> x_end = 1
    >>> h = 0.1
    >>> x_vals, y_vals = solve_ode_predictor_corrector(f, x0, y0, x_end, h)
    """
    x_values = [x0]
    y_values = [y0]

    x, y = x0, y0
    while x < x_end:
        y_pred = y + h * f(x, y)
        x_next = x + h
        y_corr = y + h / 2 * (f(x, y) + f(x_next, y_pred))
        
        x, y = x_next, y_corr
        x_values.append(x)
        y_values.append(y)

    return x_values, y_values

def solve_ode_runge_kutta(f: Callable, x0: float, y0: float, x_end: float, h: float, order: int = 4) -> tuple:
    """
    Универсальный метод Рунге-Кутты для решения ОДУ.

    Параметры
    ----------
    f : Callable
        Правая часть ОДУ (dy/dx = f(x, y))
    x0 : float
        Начальная точка
    y0 : float
        Начальное значение y
    x_end : float
        Конец интервала
    h : float
        Шаг интегрирования
    order : int, optional
        Порядок метода Рунге-Кутты (1, 2, 3 или 4), по умолчанию 4

    Возвращает
    ----------
    tuple
        (x_values, y_values) - массивы numpy со значениями x и y

    Пример
    -------
    >>> def f(x, y):
    ...     return -2 * x + y
    >>> x0, y0 = 0, 1
    >>> x_end = 1
    >>> h = 0.1
    >>> x_vals, y_vals = solve_ode_runge_kutta(f, x0, y0, x_end, h, order=4)
    """
    if order not in [1, 2, 3, 4]:
        raise ValueError("Порядок метода должен быть 1, 2, 3 или 4.")

    x_values = [x0]
    y_values = [y0]
    x, y = x0, y0

    while x < x_end:
        if order == 1:
            k1 = f(x, y)
            y = y + h * k1
        elif order == 2:
            k1 = f(x, y)
            k2 = f(x + h / 2, y + h / 2 * k1)
            y = y + h * k2
        elif order == 3:
            k1 = f(x, y)
            k2 = f(x + h / 2, y + h / 2 * k1)
            k3 = f(x + h, y - h * k1 + 2 * h * k2)
            y = y + h / 6 * (k1 + 4 * k2 + k3)
        else:  # order == 4
            k1 = f(x, y)
            k2 = f(x + h / 2, y + h / 2 * k1)
            k3 = f(x + h / 2, y + h / 2 * k2)
            k4 = f(x + h, y + h * k3)
            y = y + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)

        x = x + h
        x_values.append(x)
        y_values.append(y)

    return np.array(x_values), np.array(y_values)

def solve_ode_system_euler(f_system: list, x0: float, y0: list, x_end: float, h: float) -> tuple:
    """
    Метод Эйлера для решения систем обыкновенных дифференциальных уравнений (ОДУ).

    Параметры
    ----------
    f_system : list
        Список функций правых частей системы ОДУ [f1, f2, ..., fn]
    x0 : float
        Начальная точка
    y0 : list
        Начальные значения y в виде списка [y1_0, y2_0, ..., yn_0]
    x_end : float
        Конечная точка x
    h : float
        Шаг интегрирования

    Возвращает
    ----------
    tuple
        (x_values, y_values) - массивы numpy со значениями x и y

    Пример
    -------
    >>> def f1(x, y): return y[1]
    >>> def f2(x, y): return -0.5 * y[1] - y[0]
    >>> f_system = [f1, f2]
    >>> x0, y0 = 0, [2, -1]
    >>> x_end, h = 10, 0.1
    >>> x_vals, y_vals = solve_ode_system_euler(f_system, x0, y0, x_end, h)
    """
    n = len(f_system)
    x_values = [x0]
    y_values = [y0]
    x = x0
    y = np.array(y0)

    while x < x_end:
        y_new = np.zeros(n)
        for i in range(n):
            y_new[i] = y[i] + h * f_system[i](x, y)
        y = y_new
        x = x + h
        if x < x_end:
            x_values.append(x)
            y_values.append(y.tolist())

    return np.array(x_values), np.array(y_values)