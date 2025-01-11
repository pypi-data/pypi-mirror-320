import numpy as np
from typing import List

def dft(x: List[complex]) -> List[complex]:
    """
    Вычисляет дискретное преобразование Фурье (ДПФ) входного сигнала вручную.

    :param x: Входной сигнал как список комплексных чисел
    :return: Результат ДПФ - список комплексных чисел той же длины, что и входной сигнал

    Пример
    -------
    >>> x = [1+0j, 2+0j, 3+0j, 4+0j]
    >>> dft(x)
    [(10+0j), (-2.0000000000000004+1.9999999999999996j), (-2-9.797174393178826e-16j), (-1.9999999999999982-2.000000000000001j)]
    """
    N = len(x)
    W = [[np.exp(-2j * np.pi * k * n / N) for k in range(N)] for n in range(N)]  # Матрица DFT
    result = [sum(W[n][k] * x[k] for k in range(N)) for n in range(N)]  # Умножение на вектор
    return result

def idft(X: np.ndarray[np.complex128]) -> np.ndarray[np.complex128]:
    """
    Вычисляет обратное дискретное преобразование Фурье (ОДПФ) входного сигнала.

    Функция реализует ОДПФ, используя матричное умножение для эффективного вычисления.

    Параметры
    ----------
    X : np.ndarray[np.complex128]
        Входной сигнал как массив комплексных чисел

    Возвращает
    ----------
    np.ndarray[np.complex128]
        Результат ОДПФ - массив комплексных чисел той же длины, что и входной сигнал

    Пример
    -------
    >>> X = np.array([10+0j, -2+2j, -2+0j, -2-2j])
    >>> idft(X)
    array([ 1.+0.j,  2.+0.j,  3.+0.j,  4.+0.j])
    """
    N = len(X)
    n = np.arange(N)[:, None]  # Create a column vector of n
    k = np.arange(N)[None, :]  # Create a row vector of k
    W = np.exp(2j * np.pi * k * n / N)  # Calculate the IDFT matrix using broadcasting
    return [sum(W[n][k] * X[k] for k in range(N)) / N for n in range(N)]

def fft(x: np.ndarray[np.complex128]) -> np.ndarray[np.complex128]:
    """
    Быстрое преобразование Фурье (БПФ) с использованием алгоритма Cooley-Tukey.
    
    Параметры:
    ----------
    x : np.ndarray[np.complex128]
        Входной массив комплексных чисел
        
    Возвращает:
    -----------
    np.ndarray[np.complex128]
        Результат БПФ

    !! Пример решения задачи с fft:
    from optinum.signal import fft, ifft

    def custom_fftfreq(N: int, d: float = 1.0) -> np.ndarray:
        '''
        Вычисляет частотную шкалу для FFT.
        
        Параметры:
        ----------
        N : int
            Число точек в преобразовании.
        d : float
            Шаг между отсчетами во временной области (обратная частота выборки).
            
        Возвращает:
        ----------
        np.ndarray
            Массив частот.
        '''
        freqs = np.arange(N)
        return np.where(freqs <= N // 2, freqs / (N * d), (freqs - N) / (N * d))

    # Генерация сигнала с шумом
    SAMPLE_RATE = 44100  # Гц
    DURATION = 5  # секунд

    def generate_sine_wave(freq, sample_rate, duration):
        x = np.linspace(0, duration, sample_rate * duration, endpoint=False)
        y = np.sin(2 * np.pi * freq * x)
        return x, y

    # Генерация тонов
    _, nice_tone = generate_sine_wave(400, SAMPLE_RATE, DURATION)
    _, noise_tone = generate_sine_wave(4000, SAMPLE_RATE, DURATION)
    noise_tone = noise_tone * 0.1  # Уменьшаем амплитуду шума
    mixed_tone = nice_tone + noise_tone

    # Применяем БПФ
    yf = fft(mixed_tone)
    xf = custom_fftfreq(len(yf), 1 / SAMPLE_RATE)

    # Фильтрация шума
    target_freq = 4000
    threshold = 100  # Область вокруг 4000 Гц, которую обнулим
    filtered_yf = yf.copy()
    # Обнуляем частоты болльше 4000 Гц ()
    filtered_yf[4000:] = 0

    # Применяем ОБПФ для восстановления сигнала
    filtered_signal = ifft(filtered_yf).real

    # Визуализация
    plt.figure(figsize=(12, 6))

    # No noise
    plt.subplot(3, 1, 3)
    plt.plot(custom_fftfreq(len(yf), 1 / SAMPLE_RATE), np.abs(fft(nice_tone)), label="Без шума", color="green")
    plt.title("Частотный спектр (до фильтрации)")
    plt.xlabel("Частота (Гц)")
    plt.ylabel("Амплитуда")
    plt.grid()
    plt.legend()

    # Исходный спектр
    plt.subplot(3, 1, 1)
    plt.plot(xf, np.abs(yf), label="До фильтрации")
    plt.title("Частотный спектр (до фильтрации)")
    plt.xlabel("Частота (Гц)")
    plt.ylabel("Амплитуда")
    plt.grid()
    plt.legend()

    # Спектр после фильтрации
    plt.subplot(3, 1, 2)
    plt.plot(xf, np.abs(filtered_yf), label="После фильтрации", color="orange")
    plt.title("Частотный спектр (после фильтрации)")
    plt.xlabel("Частота (Гц)")
    plt.ylabel("Амплитуда")
    plt.grid()
    plt.legend()

    plt.tight_layout()
    plt.show()

    # Временные сигналы
    plt.figure(figsize=(12, 6))
    plt.plot(mixed_tone[:1000], label="Исходный сигнал с шумом")
    plt.plot(filtered_signal[:1000], label="Фильтрованный сигнал", color='orange')
    plt.title("Временной сигнал")
    plt.xlabel("Отсчёты")
    plt.ylabel("Амплитуда")
    plt.legend()
    plt.grid()
    plt.show()
    """
    original_N = len(x)
    N = len(x)
    
    # Дополняем входной массив нулями до ближайшей степени двойки
    if N & (N-1) != 0:
        next_power_2 = 1 << (N - 1).bit_length()
        x = np.pad(x, (0, next_power_2 - N), mode='constant')
        N = next_power_2
    
    # Базовый случай рекурсии
    if N == 1:
        return x
    
    # Разделяем на четные и нечетные индексы
    even = fft(x[::2])
    odd = fft(x[1::2])
    
    # Вычисляем комплексные экспоненты
    factor = np.exp(-2j * np.pi * np.arange(N) / N)
    
    # Объединяем результаты по формуле X_k = E_k + e^(-2πik/N)O_k
    result = np.concatenate([
        even + factor[:N//2] * odd,      # Для k от 0 до N/2-1
        even + factor[N//2:] * odd       # Для k от N/2 до N-1
    ])
    
    # Возвращаем только нужное количество элементов
    return result[:original_N]

def ifft(X: np.ndarray[np.complex128]) -> np.ndarray[np.complex128]:
    """
    Обратное быстрое преобразование Фурье (ОБПФ) с использованием алгоритма Cooley-Tukey.
    
    Параметры:
    ----------
    X : np.ndarray[np.complex128]
        Входной массив комплексных чисел
        
    Возвращает:
    -----------
    np.ndarray[np.complex128]
        Результат ОБПФ
    """
    # Применяем БПФ к комплексно-сопряженным элементам
    result = np.conj(fft(np.conj(X))) / len(X)
    return result