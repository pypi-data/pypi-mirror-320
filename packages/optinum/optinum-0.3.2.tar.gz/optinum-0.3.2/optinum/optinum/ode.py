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


def solve_ode_adams_bashforth(f: Callable[[float, float], float], y0: float, x0: float, x_end: float, h: float) -> tuple[np.ndarray, np.ndarray]:
  """
  Решает обыкновенное дифференциальное уравнение методом Адамса-Башфорта 4-го порядка.

  Args:
    f: Функция правой части дифференциального уравнения dy/dx = f(x, y)
    y0: Начальное значение y в точке x0
    x0: Начальная точка
    x_end: Конечная точка
    h: Шаг интегрирования

  Returns:
    Кортеж из двух массивов NumPy: x (значения x) и y (соответствующие значения y)

    Пример использования:
    >>> def f(x: float, y: float) -> float:
    Пример функции правой части дифференциального уравнения.
    >>> return x**2 * y

    >>> h = 0.1
    >>> x0 = 0
    >>> x_end = 1
    >>> y0 = 1
    >>> x, y = solve_ode_adams_bashforth(f, y0, x0, x_end, h)
    >>> for i in range(len(y)):
    >>> print(f"x = {round(x[i],2)}, y = {round(y[i],6)}")
    x = 0.0, y = 1.0
    x = 0.1, y = 1.000333
    x = 0.2, y = 1.00267
    x = 0.3, y = 1.009041
    x = 0.4, y = 1.021535
    x = 0.5, y = 1.042474
    x = 0.6, y = 1.074515
    x = 0.7, y = 1.120886
    x = 0.8, y = 1.185707
    x = 0.9, y = 1.274453
    x = 1.0, y = 1.39464
    
  """
  n = int((x_end - x0) / h)+1
  x = np.linspace(x0, x_end, n)
  y = np.zeros(n)

  # Используем метод Рунге-Кутта 4-го порядка для получения первых 4 значений
  y[0] = y0

  for i in range(3):
    k1 = h * f(x[i], y[i])
    k2 = h * f(x[i] + h/2, y[i] + k1/2)
    k3 = h * f(x[i] + h/2, y[i] + k2/2)
    k4 = h * f(x[i] + h, y[i] + k3)
    y[i+1] = y[i] + (k1 + 2*k2 + 2*k3 + k4) / 6

  # предлагаю заменить на реализованный и оставить только вычисления (но в остальных оставила реализацию метода внутри)
  # _, y[0:4] = runge_kutta_4(f, x0, y0, round(x0+3*h, 1), h)
  # Используем метод Адамса-Башфорта для остальных значений
  for i in range(3, n-1):
    y[i+1] = y[i] + h/24 * (55 * f(x[i], y[i]) - 59 * f(x[i-1], y[i-1]) + 37 * f(x[i-2], y[i-2]) - 9 * f(x[i-3], y[i-3]))
  return x, y

import numpy as np
from typing import Callable



def solve_ode_system_adams_bashforth(f: Callable[[float, float, float], float], y0: float, v0: float, x0: float, x_end: float, h: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
     Решает обыкновенное дифференциальное уравнение второго порядка(или систему, так как мы в этом случае к ней переходим) методом Адамса-Башфорта 4-го порядка.
     Либо понижаем порядок засчет новой переменной(тогда выводить в ответ ее не нужно), либо у нас y1 и y2, выводим три массива в ответ

    Args:
        f: Функция правой части дифференциального уравнения y'' = f(x, y, y')
        y0: Начальное значение y в точке x0
        v0: Начальное значение y' в точке x0
        x0: Начальная точка
        x_end: Конечная точка
        h: Шаг интегрирования

    Returns:
        Кортеж из трех массивов NumPy: x (значения x), y (значения y), v (значения y') - значения v по идее не нужны, только y решение.(или y2 - выводим)
    
    Пример использования для уравнения y'' - 2y' + y - 1 = 0
    y'' = f(x, y, y')
    y' = v
    v' = f(x, y, v)
    y'' -2 y' + y - 1 = 0
    с начальными условиями y(0) = 1 и y'(0) = 2

    >>> def f_example(x: float, y: float, v: float) -> float:
    ...    return 2 * v - y + 1

    >>> h = 0.1
    >>> x0 = 0
    >>> x_end = 1
    >>> y0 = 1
    >>> v0 = 2
    >>> x, y, v = solve_ode_system_adams_bashforth(f_example, y0, v0, x0, x_end, h)
    >>> for i in range(len(x)):
    ...    print(f"x = {round(x[i], 2)}, y = {round(y[i], 6)}, y' = {round(v[i], 6)}")
    Вывод:
    x = 1.0, y = 6.435893, y' = 10.872342
    """
    n = int((x_end - x0) / h) + 1
    x = np.linspace(x0, x_end, n)
    y = np.zeros(n)
    v = np.zeros(n)

    # Используем метод Рунге-Кутты 4-го порядка для первых 4 точек
    y[0] = y0
    v[0] = v0

    for i in range(3):
        k1_y = h * v[i]
        k1_v = h * f(x[i], y[i], v[i])
        k2_y = h * (v[i] + k1_v / 2)
        k2_v = h * f(x[i] + h / 2, y[i] + k1_y / 2, v[i] + k1_v / 2)
        k3_y = h * (v[i] + k2_v / 2)
        k3_v = h * f(x[i] + h / 2, y[i] + k2_y / 2, v[i] + k2_v / 2)
        k4_y = h * (v[i] + k3_v)
        k4_v = h * f(x[i] + h, y[i] + k3_y, v[i] + k3_v)

        y[i + 1] = y[i] + (k1_y + 2 * k2_y + 2 * k3_y + k4_y) / 6
        v[i + 1] = v[i] + (k1_v + 2 * k2_v + 2 * k3_v + k4_v) / 6

    # Метод Адамса-Башфорта
    for i in range(3, n - 1):
        y[i + 1] = y[i] + h / 24 * (55 * v[i] - 59 * v[i - 1] + 37 * v[i - 2] - 9 * v[i - 3])
        v[i + 1] = v[i] + h / 24 * (55 * f(x[i], y[i], v[i]) - 59 * f(x[i - 1], y[i - 1], v[i - 1]) +
                                   37 * f(x[i - 2], y[i - 2], v[i - 2]) - 9 * f(x[i - 3], y[i - 3], v[i - 3]))

    return x, y, v

import numpy as np
import matplotlib.pyplot as plt
from typing import Callable

def solve_ode_adams_moulton(f: Callable[[float, float], float], y0: float, x0: float, x_end: float, h: float) -> tuple[np.ndarray, np.ndarray]:
    """
    Решает обыкновенное дифференциальное уравнение методом Адамса-Моултона 4-го порядка.

    Args:
        f: Функция правой части дифференциального уравнения dy/dx = f(x, y).
        y0: Начальное значение y в точке x0.
        x0: Начальная точка.
        x_end: Конечная точка.
        h: Шаг интегрирования.

    Returns:
        Кортеж из двух массивов NumPy: x_values (значения x) и y_values (соответствующие значения y).

    Пример использования:

    def f(x: float, y: float) -> float:
        Пример функции правой части дифференциального уравнения.
        return x**2 * y

    # Параметры
    y0 = 1
    x0 = 0.0
    x_end = 1.0
    h = 0.1

    # Вызов метода
    x_values, y_values = solve_ode_adams_moulton(f, y0, x0, x_end, h)
    for i in range(len(y_values)):
        print(f"x = {round(x_values[i],2)}, y = {round(y_values[i],6)}")
    """
    n_steps = int((x_end - x0) / h)
    x_values = np.zeros(n_steps + 1)
    y_values = np.zeros(n_steps + 1)
    x_values[0] = x0
    y_values[0] = y0

    # Вычислим первые три значения с помощью метода Эйлера
    for i in range(3):
        y_values[i + 1] = y_values[i] + h * f(x_values[i], y_values[i])
        x_values[i + 1] = x_values[i] + h

    # Основной цикл метода Адамса-Моултона четвертого порядка
    for i in range(3, n_steps):
        x_values[i + 1] = x_values[i] + h
        y_next = y_values[i]  # Начальное приближение для y_next

        for _ in range(10):  # Количество итераций
            y_next_new = (y_values[i] + (h / 24) * (9 * f(x_values[i + 1], y_next) +
                                                19* f(x_values[i], y_values[i]) -
                                                5 * f(x_values[i - 1], y_values[i - 1]) +
                                                 f(x_values[i - 2], y_values[i - 2])))
            if abs(y_next_new - y_next) < 1e-6:
                break
            y_next = y_next_new
        y_values[i + 1] = y_next
    return x_values, y_values

# пример со вторым порядком чтоб сравнить значения
import numpy as np
from typing import Callable
import matplotlib.pyplot as plt

def solve_ode_system_adams_moulton(f: Callable[[float, np.ndarray], np.ndarray], y0: np.ndarray, x0: float, x_end: float, h: float) -> tuple[np.ndarray, np.ndarray]:
    """
    Решает систему обыкновенных дифференциальных уравнений методом Адамса-Моултона 4-го порядка.

    Args:
        f: Функция правой части системы дифференциальных уравнений dy/dx = f(x, y).
        y0: Начальное значение y в точке x0 (вектор).
        x0: Начальная точка.
        x_end: Конечная точка.
        h: Шаг интегрирования.

    Returns:
        Кортеж из массивов NumPy: x_values (значения x) и y_values (матрица значений y).

    Пример использования для системы y1' = y2, y2' = -y1
    (y' = v v' = -y)
    def system_f(x: float, y: np.ndarray) -> np.ndarray:
        Правая часть системы дифференциальных уравнений.
        #return np.array([y[1], -y[0]])
        #2 * v - y + 1
        return np.array([y[1], 2*y[1]-y[0]+1])

    # Начальные условия
    y0 = np.array([1, 2])
    x0 = 0
    x_end = 1
    h = 0.1
    # Решение задачи
    x_values, y_values,  = adams_moulton_sys(system_f, y0, x0, x_end, h)
    for i in range(len(y_values)):
        print(f"x = {round(x_values[i], 1)}, y1 = {y_values[i][0]}, v = {y_values[i][1]}")
    """
    n_steps = int((x_end - x0) / h)
    x_values = np.zeros(n_steps + 1)
    y_values = np.zeros((n_steps + 1, len(y0)))
    x_values[0] = x0
    y_values[0] = y0

    # Вычислим первые три значения с помощью метода Рунге-Кутты 4-го порядка
    for i in range(3):
        k1 = h * f(x_values[i], y_values[i])
        k2 = h * f(x_values[i] + h / 2, y_values[i] + k1 / 2)
        k3 = h * f(x_values[i] + h / 2, y_values[i] + k2 / 2)
        k4 = h * f(x_values[i] + h, y_values[i] + k3)
        y_values[i + 1] = y_values[i] + (k1 + 2 * k2 + 2 * k3 + k4) / 6
        x_values[i + 1] = x_values[i] + h

    # Основной цикл метода Адамса-Моултона четвертого порядка
    for i in range(3, n_steps):
        x_values[i + 1] = x_values[i] + h
        y_next = y_values[i].copy()  # Начальное приближение для y_next

        for _ in range(10):  # Количество итераций
            y_next_new = (y_values[i] +
                           (h / 24) * (9 * f(x_values[i + 1], y_next) +
                                      19 * f(x_values[i], y_values[i]) -
                                       5 * f(x_values[i - 1], y_values[i - 1]) +
                                       f(x_values[i - 2], y_values[i - 2])))
            if np.max(np.abs(y_next_new - y_next)) < 1e-6:
                break
            y_next = y_next_new
        y_values[i + 1] = y_next

    return x_values, y_values

def solve_ode_milne_method(f: Callable[[float, float], float], y0: float, x0: float, x_end: float, h: float) -> tuple[np.ndarray, np.ndarray]:
    """
    Решает обыкновенное дифференциальное уравнение методом Милна 4-го порядка.

    Args:
        f: Функция правой части дифференциального уравнения dy/dx = f(x, y).
        y0: Начальное значение y в точке x0.
        x0: Начальная точка.
        x_end: Конечная точка.
        h: Шаг интегрирования.

    Returns:
        Кортеж из двух массивов NumPy: x_values (значения x) и y_values (соответствующие значения y).

    Пример использования:
    y' = f(x, y) = -2y + 2

    # Пример использования
    def f(x: float, y: float) -> float:
        '''
        Пример функции правой части дифференциального уравнения.
        '''
        return x**2 * y

    # Параметры
    y0 = 1
    x0 = 0.0
    x_end = 1.0
    h = 0.1
    # Решение задачи
    x_values, y_values = milne_method(f, y0, x0, x_end, h)
    for i in range(len(y_values)):
        print(f"x = {round(x_values[i],2)}, y = {round(y_values[i],6)}")
    """
    n_steps = int((x_end - x0) / h)
    x_values = np.zeros(n_steps + 1)
    y_values = np.zeros(n_steps + 1)
    x_values[0] = x0
    y_values[0] = y0

    # Используем метод Рунге-Кутты 4-го порядка для получения первых 4 значений
    def runge_kutta4(x, y):
        k1 = h * f(x, y)
        k2 = h * f(x + h/2, y + k1/2)
        k3 = h * f(x + h/2, y + k2/2)
        k4 = h * f(x + h, y + k3)
        return y + (k1 + 2*k2 + 2*k3 + k4) / 6

    for i in range(3):
        y_values[i + 1] = runge_kutta4(x_values[i], y_values[i])
        x_values[i + 1] = x_values[i] + h

    # Основной цикл метода Милна
    for i in range(3, n_steps):
        x_values[i + 1] = x_values[i] + h
        # Предварительное значение (предсказание)
        y_predict = y_values[i-3] + (4*h/3) * (2*f(x_values[i], y_values[i]) - f(x_values[i-1], y_values[i-1]) + 2*f(x_values[i-2], y_values[i-2]))
        # Коррекция
        y_values[i+1] = y_values[i-1] + (h/3) * (f(x_values[i+1], y_predict) + 4*f(x_values[i], y_values[i]) + f(x_values[i-1], y_values[i-1]))
    return x_values, y_values

def solve_ode_system_milne_method(f: Callable[[float, np.ndarray], np.ndarray], y0: np.ndarray, x0: float, x_end: float, h: float) -> tuple[np.ndarray, np.ndarray]:
    """
    Решает обыкновенное дифференциальное уравнение методом Милна 4-го порядка.

    Args:
        f: Функция правой части дифференциального уравнения dy/dx = f(x, y).
        y0: Начальное значение y в точке x0.
        x0: Начальная точка.
        x_end: Конечная точка.
        h: Шаг интегрирования.

    Returns:
        Кортеж из двух массивов NumPy: x_values (значения x) и y_values (соответствующие значения y).

    Пример использования:

    def system_f(x: float, y: np.ndarray) -> np.ndarray:
    '''
    Правая часть системы дифференциальных уравнений.
    '''
    return np.array([y[1], -y[0]])


    # Начальные условия
    y0 = np.array([1, 0])
    x0 = 0.0
    x_end = 1.0
    h = 0.1
    # Решение задачи
    x_values, y_values = solve_ode_systemm_milne_method(system_f, y0, x0, x_end, h)
    for i in range(len(y_values)):
        print(f"x = {round(x_values[i],2)}, y1 = {round(y_values[i][0],6)}, y2 = {round(y_values[i][1], 6)}")
    """
    n_steps = int((x_end - x0) / h)
    x_values = np.zeros(n_steps + 1)
    y_values = np.zeros((n_steps + 1, len(y0)))
    x_values[0] = x0
    y_values[0] = y0

    # Используем метод Рунге-Кутты 4-го порядка для получения первых 4 значений
    def runge_kutta4(x, y):
        k1 = h * f(x, y)
        k2 = h * f(x + h/2, y + k1/2)
        k3 = h * f(x + h/2, y + k2/2)
        k4 = h * f(x + h, y + k3)
        return y + (k1 + 2*k2 + 2*k3 + k4) / 6

    for i in range(3):
        y_values[i + 1] = runge_kutta4(x_values[i], y_values[i])
        x_values[i + 1] = x_values[i] + h

    # Основной цикл метода Милна
    for i in range(3, n_steps):
        x_values[i + 1] = x_values[i] + h
        # Предварительное значение (предсказание)
        y_predict = y_values[i-3] + (4*h/3) * (2*f(x_values[i], y_values[i]) - f(x_values[i-1], y_values[i-1]) + 2*f(x_values[i-2], y_values[i-2]))
        # Коррекция
        y_values[i+1] = y_values[i-1] + (h/3) * (f(x_values[i+1], y_predict) + 4*f(x_values[i], y_values[i]) + f(x_values[i-1], y_values[i-1]))
    return x_values, y_values