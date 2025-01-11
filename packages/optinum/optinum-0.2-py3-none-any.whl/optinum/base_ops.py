from typing import List

def add(matrix_a: List[List], matrix_b: List[List]) -> List[List]:
    """
    Складывает две матрицы одинакового размера.
    
    :param matrix_a: Первая матрица
    :param matrix_b: Вторая матрица
    :return: Результирующая матрица, представляющая собой сумму matrix_a и matrix_b
    """
    return [[matrix_a[i][j] + matrix_b[i][j] for j in range(len(matrix_a[0]))] for i in range(len(matrix_a))]

def subtract(matrix_a: List[List], matrix_b: List[List]) -> List[List]:
    """
    Вычитает одну матрицу из другой матрицы одинакового размера.
    
    :param matrix_a: Первая матрица
    :param matrix_b: Вторая матрица
    :return: Результирующая матрица, представляющая собой разность matrix_a и matrix_b
    """
    return [[matrix_a[i][j] - matrix_b[i][j] for j in range(len(matrix_a[0]))] for i in range(len(matrix_a))]

def multiply(matrix_a: List[List], matrix_b: List[List]) -> List[List]:
    """
    Перемножает две матрицы.
    
    :param matrix_a: Первая матрица
    :param matrix_b: Вторая матрица
    :return: Результирующая матрица, представляющая собой произведение matrix_a и matrix_b
    """
    return [[sum(matrix_a[i][k] * matrix_b[k][j] for k in range(len(matrix_a[0]))) for j in range(len(matrix_b[0]))] for i in range(len(matrix_a))]

def strassen_multiply(a: List[List], b: List[List]) -> List[List]:
    """
    Перемножает две матрицы с использованием алгоритма Штрассена.
    
    :param a: Первая матрица
    :param b: Вторая матрица
    :return: Результирующая матрица, представляющая собой произведение a и b
    """
    def split(matrix: List[List]) -> tuple:
        """
        Разбивает матрицу на четыре подматрицы.
        
        :param matrix: Исходная матрица
        :return: Четыре подматрицы
        """
        mid = len(matrix) // 2
        a11 = [row[:mid] for row in matrix[:mid]]
        a12 = [row[mid:] for row in matrix[:mid]]
        a21 = [row[:mid] for row in matrix[mid:]]
        a22 = [row[mid:] for row in matrix[mid:]]
        return a11, a12, a21, a22

    def merge(c11: List[List], c12: List[List], c21: List[List], c22: List[List]) -> List[List]:
        """
        Объединяет четыре подматрицы в одну матрицу.
        
        :param c11: Первая подматрица
        :param c12: Вторая подматрица
        :param c21: Третья подматрица
        :param c22: Четвертая подматрица
        :return: Объединенная матрица
        """
        top = [c11[i] + c12[i] for i in range(len(c11))]
        bottom = [c21[i] + c22[i] for i in range(len(c21))]
        return top + bottom

    if len(a) == 1 or len(a[0]) == 1:
        return [[a[0][0] * b[0][0]]]
    
    # Убедимся, что матрицы имеют размер степени двойки
    n = max(len(a), len(a[0]), len(b), len(b[0]))
    m = 1
    while m < n:
        m *= 2
    
    def pad_matrix(matrix: List[List], size: int) -> List[List]:
        """
        Дополняет матрицу нулями до указанного размера.
        
        :param matrix: Исходная матрица
        :param size: Требуемый размер
        :return: Дополненная матрица
        """
        padded = [[0] * size for _ in range(size)]
        for i in range(len(matrix)):
            for j in range(len(matrix[0])):
                padded[i][j] = matrix[i][j]
        return padded
    
    a = pad_matrix(a, m)
    b = pad_matrix(b, m)
    
    # Разбиение матриц на блоки
    a11, a12, a21, a22 = split(a)
    b11, b12, b21, b22 = split(b)
    
    # Вычисление промежуточных значений
    f1 = strassen_multiply(add(a11, a22), add(b11, b22))
    f2 = strassen_multiply(add(a21, a22), b11)
    f3 = strassen_multiply(a11, subtract(b12, b22))
    f4 = strassen_multiply(a22, subtract(b21, b11))
    f5 = strassen_multiply(add(a11, a12), b22)
    f6 = strassen_multiply(subtract(a21, a11), add(b11, b12))
    f7 = strassen_multiply(subtract(a12, a22), add(b21, b22))
    
    # Вычисление блоков результирующей матрицы
    c11 = add(subtract(add(f1, f4), f5), f7)
    c12 = add(f3, f5)
    c21 = add(f2, f4)
    c22 = add(subtract(add(f1, f3), f2), f6)
    
    # Сборка результирующей матрицы
    result = merge(c11, c12, c21, c22)
    
    # Убираем дополнение
    return [row[:len(b[0])] for row in result[:len(a)]]