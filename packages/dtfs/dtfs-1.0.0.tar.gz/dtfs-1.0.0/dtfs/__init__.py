import pyperclip as pc
from IPython.display import display, Image, Markdown
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer


def check(sentence1, sentence2):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([sentence1, sentence2])
    cosine_similarities = cosine_similarity(tfidf_matrix)
    similarity_percentage = cosine_similarities[0, 1] * 100
    return similarity_percentage

def q(n):
    # Проверяем, является ли входной аргумент числом (строка, которую можно привести к int)
    n = str(n)
    if n.isdigit():
        n = int(n)
        # Возвращаем значение (value) словаря по индексу n
        return pc.copy(list(s[n].values())[0])
    else:
        # В противном случае вычисляем схожесть введённой строки (n) 
        # с "ключами" (keys) во всех словарях s
        c = []
        for i, u in enumerate(s):
            # Поскольку в каждом словаре s[i] один ключ, то получим его с помощью next(iter(...))
            key = next(iter(u.keys()))
            # Считаем похожесть между запросом n и этим ключом
            similarity = check(n, key)
            c.append([i, similarity])
        
        # Сортируем список c по убыванию (по значению сходства)
        res = sorted(c, reverse=True, key=lambda x: x[1])[:5]
        return res
 
s = [{
'''# наивное перемножение (покажите алгоритмическую сложность)
# O(n^3) алгоритмическая сложность
# Алгоритмическая сложность данного наивного умножения матриц размера (m×n) на (n×p) равна O(m×n×p). Для случая, когда m=n=p, сложность составляет O(n3). Так как все зависит от n, то алгоритмическая сложность всегда будет такой
# поставить свои матрицы''': '''
# наивное перемножение (покажите алгоритмическую сложность)
# O(n^3) алгоритмическая сложность
# поставить свои матрицы
def matrix_multiply(A, B):

    m = len(A)          # Количество строк в матрице A
    n = len(A[0])       # Количество столбцов в матрице A и строк в матрице B
    p = len(B[0])       # Количество столбцов в матрице B

    # Создаем результирующую матрицу и заполняем нулями
    result = [[0 for _ in range(p)] for _ in range(m)]

    # Наивный алгоритм умножения матриц (тройной цикл)
    for i in range(m):
        for j in range(p):
            for k in range(n):
                result[i][j] += A[i][k] * B[k][j]
    return result

A = [[1, 2, 3],
     [4, 5, 6]]
B = [[7, 8],
     [9, 10],
     [11, 12]]

C = matrix_multiply(A, B)
print("Результат умножения матриц A и B:")
for row in C:
    print(row)'''
},
{
'''# алгоритм Штрассена (перемножение матриц)
# ТОЛЬКО КВАДРАТНЫЕ МАТРИЦЫ
# подставить свои матрицы''': '''
# алгоритм Штрассена (перемножение матриц)
# ТОЛЬКО КВАДРАТНЫЕ МАТРИЦЫ
# подставить свои матрицы
def matrix_multiply_strassen(A, B):
    n = len(A)
    # базовый случай для остановки рекурсии
    # матрица 1х1 те просто элемент 
    if n == 1:
        return [[A[0][0] * B[0][0]]]

    # проверяем, является ли размер матрицы степенью двойки
    # если нет, дополняем матрицы до ближайшей степени двойки
    if n & (n - 1) != 0:
        m = 1 << (n - 1).bit_length()
        A = [[A[i][j] if i < n and j < n else 0 for j in range(m)] for i in range(m)]
        B = [[B[i][j] if i < n and j < n else 0 for j in range(m)] for i in range(m)]
        n = m

    # Разделяем матрицы на подматрицы
    mid = n // 2
    A11 = [[A[i][j] for j in range(mid)] for i in range(mid)]
    A12 = [[A[i][j] for j in range(mid, n)] for i in range(mid)]
    A21 = [[A[i][j] for j in range(mid)] for i in range(mid, n)]
    A22 = [[A[i][j] for j in range(mid, n)] for i in range(mid, n)]

    B11 = [[B[i][j] for j in range(mid)] for i in range(mid)]
    B12 = [[B[i][j] for j in range(mid, n)] for i in range(mid)]
    B21 = [[B[i][j] for j in range(mid)] for i in range(mid, n)]
    B22 = [[B[i][j] for j in range(mid, n)] for i in range(mid, n)]

    # Вычисляем промежуточные матрицы M
    M1 = matrix_multiply_strassen(matrix_add(A11, A22), matrix_add(B11, B22))
    M2 = matrix_multiply_strassen(matrix_add(A21, A22), B11)
    M3 = matrix_multiply_strassen(A11, matrix_subtract(B12, B22))
    M4 = matrix_multiply_strassen(A22, matrix_subtract(B21, B11))
    M5 = matrix_multiply_strassen(matrix_add(A11, A12), B22)
    M6 = matrix_multiply_strassen(matrix_subtract(A21, A11), matrix_add(B11, B12))
    M7 = matrix_multiply_strassen(matrix_subtract(A12, A22), matrix_add(B21, B22))

    # Вычисляем подматрицы результирующей матрицы C
    C11 = matrix_add(matrix_subtract(matrix_add(M1, M4), M5), M7)
    C12 = matrix_add(M3, M5)
    C21 = matrix_add(M2, M4)
    C22 = matrix_add(matrix_subtract(matrix_add(M1, M3), M2), M6)

    # Объединяем подматрицы в одну матрицу
    new_matrix = [[0]*n for _ in range(n)]
    for i in range(mid):
        for j in range(mid):
            new_matrix[i][j] = C11[i][j]
            new_matrix[i][j + mid] = C12[i][j]
            new_matrix[i + mid][j] = C21[i][j]
            new_matrix[i + mid][j + mid] = C22[i][j]

    # Обрезаем матрицу до исходного размера, если она была дополнена
    return [row[:len(B[0])] for row in new_matrix[:len(A)]]

def matrix_add(A, B):
    # A + B
    n = len(A)
    return [[A[i][j] + B[i][j] for j in range(n)] for i in range(n)]

def matrix_subtract(A, B):
    # A - B
    n = len(A)
    return [[A[i][j] - B[i][j] for j in range(n)] for i in range(n)]


def print_matrix(mat):
    for row in mat:
        print(row)

# Пример использования
A = [[1,2],[3,4]] #np.random.randint(0, 11, size=(rows, cols)) в диапозоне от 0 до 10 с размерностью
B = [[5,6],[7,8]]

C = matrix_multiply_strassen(A, B)
print("Результат умножения матриц A и B:")
print_matrix(С)



# если просят график сходимости
# подставить свой диапазон при умножении рандомных матриц
A = np.random.rand(8,8) * 10 # если дан диапазон [0;10]
B = np.random.rand(8,8) * 10 # просто домножаем на 10
C = matrix_multiply_strassen(A, B)
print_matrix(C)
# Функция вычисления ошибки
def relative_error(C_exact, C_strassen):
    return np.linalg.norm(C_strassen - C_exact) / np.linalg.norm(C_exact)

# Сравнение для разных размеров матриц
sizes = [2**i for i in range(7)]  # Размеры квадратных матриц
errors = []

for n in sizes:
    # Генерация случайных матриц
    A = np.random.rand(n, n)
    B = np.random.rand(n, n)
    
    # Точное умножение (NumPy)
    C_exact = np.dot(A, B)
    
    # Умножение алгоритмом Штрассена
    C_strassen = matrix_multiply_strassen(A.tolist(), B.tolist())
    C_strassen = np.array(C_strassen)  # Преобразуем обратно в массив NumPy
    
    # Вычисление относительной ошибки
    error = relative_error(C_exact, C_strassen)
    errors.append(error)

# Построение графика
plt.plot(sizes, errors, marker='o')
plt.xlabel("Размер матрицы (n)")
plt.ylabel("Относительная ошибка")
plt.title("График сходимости")
plt.grid()
plt.show()'''
},
{
'''# ПРЕДПОЧТЕНИЯ ПО МЕТОДАМ:
# метод вращений (якоби)
# Когда предпочтителен:
# 	•	Матрица симметрична.
# 	•	Необходима высокая точность всех собственных значений.
# 	•	Размер матрицы относительно небольшой (n <= 1000) тк алг сложн = O(n^3), 
#         так как метод Якоби становится медленным для больших матриц.

# qr-алгоритм
# Когда предпочтителен:
# 	•	Матрица не обязательно симметрична.
# 	•	Необходимы собственные значения несимметричных матриц.
# 	•	Размер матрицы большой (n > 1000), так как QR-алгоритм 
#         быстрее метода Якоби для крупных матриц. сложность O(n^3) лишь в худшем случае
# 	•	Требуется только часть собственных значений 
#         (например, максимальные/минимальные).


# собственные значения
# qr-алгоритм
# УДАЛИТЬ ВСЕ СВЯЗАННОЕ С ВЕКТОРАМИ''': '''
# ПРЕДПОЧТЕНИЯ ПО МЕТОДАМ:
# метод вращений (якоби)
# Когда предпочтителен:
# 	•	Матрица симметрична.
# 	•	Необходима высокая точность всех собственных значений.
# 	•	Размер матрицы относительно небольшой (n <= 1000) тк алг сложн = O(n^3), 
#         так как метод Якоби становится медленным для больших матриц.

# qr-алгоритм
# Когда предпочтителен:
# 	•	Матрица не обязательно симметрична.
# 	•	Необходимы собственные значения несимметричных матриц.
# 	•	Размер матрицы большой (n > 1000), так как QR-алгоритм 
#         быстрее метода Якоби для крупных матриц. сложность O(n^3) лишь в худшем случае
# 	•	Требуется только часть собственных значений 
#         (например, максимальные/минимальные).


# собственные значения
# qr-алгоритм
# УДАЛИТЬ ВСЕ СВЯЗАННОЕ С ВЕКТОРАМИ
def qr_algorithm(A, epsilon=1e-10, max_iterations=1000):
    # Преобразуем входную матрицу в формат numpy
    A = np.array(A, dtype=float)
    n = A.shape[0]

    # Инициализация матрицы для собственных векторов
    V = np.eye(n)

    for _ in range(max_iterations):
        # Выполняем QR-разложение матрицы A
        Q, R = qr_decomposition(A)

        # Обновляем матрицу A как R @ Q вручную
        A = [[sum(R[i][k] * Q[k][j] for k in range(n)) for j in range(n)] for i in range(n)]
        A = np.array(A)  # Преобразуем результат в формат numpy

        # Обновляем матрицу собственных векторов вручную
        V = [[sum(V[i][k] * Q[k][j] for k in range(n)) for j in range(n)] for i in range(n)]
        V = np.array(V)  # Преобразуем результат в формат numpy

        # Проверка сходимости: если максимальный элемент вне диагонали меньше epsilon, останавливаемся
        off_diagonal = A - create_diagonal_matrix(A)
        if np.all(np.abs(off_diagonal) < epsilon):
            break

    # Собственные значения — диагональные элементы матрицы A
    eigenvalues = [A[i][i] for i in range(n)]
    # Собственные векторы — столбцы матрицы V
    eigenvectors = [V[:, i] for i in range(n)]

    return eigenvalues, eigenvectors

def qr_decomposition(A):
    """Реализует QR-разложение матрицы A с использованием метода Грамма-Шмидта."""
    n = A.shape[0]
    Q = np.zeros_like(A)
    R = np.zeros((n, n))

    for j in range(n):
        # Берем j-й столбец матрицы A
        v = A[:, j]

        # Ортогонализация по предыдущим векторам Q
        for i in range(j):
            R[i, j] = sum(Q[:, i][k] * v[k] for k in range(n))  # Скаляpное произведение вручную
            v = [v[k] - R[i, j] * Q[k, i] for k in range(n)]

        # Нормируем вектор
        R[j, j] = np.sqrt(sum(v_i**2 for v_i in v))  # Норма вектора вручную
        Q[:, j] = [v_i / R[j, j] for v_i in v]  # Нормировка вектора вручную

    return Q, R

def create_diagonal_matrix(A):
    """Создает диагональную матрицу из диагональных элементов матрицы A."""
    n = len(A)
    diagonal_matrix = [[0 if i != j else A[i][i] for j in range(n)] for i in range(n)]
    return np.array(diagonal_matrix)

# Пример использования
A = [[2, 1], [1, 3]]
eigenvalues, eigenvectors = qr_algorithm(A)
print("Собственные значения:", eigenvalues)
# print("Собственные векторы:", eigenvectors)


# СРАВНЕНИЕ
epsilons = [1e-2, 1e-8]
etalon = np.sort(np.linalg.eigvalsh(A)) # эталонное решение
for eps in epsilons:
    eigenvalues, _ = qr_algorithm(A, epsilon=eps)
    eigenvalues = np.sort(eigenvalues)
    print(f'\nepsilon:{eps}')
    for i in range(len(etalon)):
        print(f'relative error:{abs((etalon[i]-eigenvalues[i])/etalon[i])}')'''
},
{
'''# собственные значения
# метод непосредственного развертывания''': '''
# собственные значения
# метод непосредственного развертывания

#преимущества:
# подходит для работы с разреженными матрицами
# быстро сходится при удачном выборе начального приближения
#недостатки:
# находит лишь одно собственное значение (макс по модулю)
# скорость сходимости сильно зависит от начального приближения
# 

def direct_rotation(A, num_iterations=1000, epsilon=1e-10):
    # Инициализация случайного вектора
    n = len(A)
    v = np.random.rand(n)
    v = v / np.linalg.norm(v)  # Нормализация
    
    for _ in range(num_iterations):
        # Итерация метода
        Av = np.dot(A, v)
        v_new = Av / np.linalg.norm(Av)
        
        # Проверка сходимости
        if np.linalg.norm(v_new - v) < epsilon:
            break
        v = v_new
    
    # Собственное значение
    eigenvalue = np.dot(v.T, np.dot(A, v)) / np.dot(v, v)
    return eigenvalue, v

# Пример использования
A = np.array([[3, -2], [-4, 1]])
eigenvalue, eigenvector = direct_rotation(A)
print("Собственное значение (макс. по модулю):", eigenvalue)
print("Собственный вектор:\n", eigenvector)'''
},
{
'''# собственные значения
# Метод итераций (степенной метод)''': '''
# собственные значения
# Метод итераций (степенной метод)

#преимущества:
# быстро сходится, если начальный вектор не ортогонален собственному
# низкая сложность в случае разреженных матриц
#недостатки:
# находит лишь одно значение (максимальное)
# из первого преимущества так же выйдет недостаток - чувствительность к начальному приближению
# без модификации не работает с комплексными числами
def power_iteration_method(A, epsilon=0.1, max_iterations=1000):
    # Размерность матрицы
    n = len(A)

    # Выбираем произвольное начальное приближение собственного вектора (ненулевое)
    X = [1.0] * n  # Вектор с единицами
    lambda_old = 0

    for k in range(max_iterations):
        # Вычисляем новый вектор X^(k+1) = A * X^(k)
        X_new = [sum(A[i][j] * X[j] for j in range(n)) for i in range(n)]

        # Находим максимальную компоненту для нормировки
        max_component = max(abs(x) for x in X_new)
        if max_component == 0:
            raise ValueError("Невозможно нормировать вектор, максимальная компонента равна нулю.")

        # Нормируем вектор
        X_new = [x / max_component for x in X_new]

        # Находим собственное значение с использованием отношения компонент
        lambda_new = max_component  # Собственное значение как максимальная компонента

        # Проверяем условие сходимости |λ^(k+1) - λ^(k)|
        if abs(lambda_new - lambda_old) < epsilon:
            break

        # Обновляем значения для следующей итерации
        X = X_new
        lambda_old = lambda_new

    # Нормируем итоговый собственный вектор на максимальную компоненту
    X = [x / max(X) for x in X]

    return lambda_new, X

# Пример использования
#A = [[5, 1, 2], [1, 4, 1], [2, 1, 3]]
A = [[2, 1], [1, 3]]
eigenvalue, eigenvector = power_iteration_method(A, epsilon=0.001)
print("Собственное значение:", eigenvalue)
print("Собственный вектор:", eigenvector)'''
},
{
'''# собственные значения
# метод вращения (Якоби)''': '''
# собственные значения
# метод вращения (Якоби)

#Преимущества:
# находит все собственные значения
# высокая точность за счет последовательного уменьшения внедиагональных
#                          элементов до заданного epsilon
#Недостатки:
# O(n^2) на каждой итерации (те O(n^3))
# работает только с симметричными матрицами
# из-за сложности вычислений не лучший метод для разреженных матриц

def rotation_method(A, epsilon=1e-10, max_iterations=1000):
    # Размерность матрицы
    n = len(A)
    A = np.array(A, dtype=float)  # Создаем копию матрицы с плавающей точкой
    V = np.eye(n)  # Единичная матрица для хранения собственных векторов

    for k in range(max_iterations):
        # Ищем максимальный по модулю элемент в верхней треугольной части
        max_value = 0
        i_max, j_max = 0, 0
        for i in range(n):
            for j in range(i + 1, n):
                if abs(A[i, j]) > max_value:
                    max_value = abs(A[i, j])
                    i_max, j_max = i, j

        # Проверяем условие остановки
        if max_value < epsilon:
            break

        # Вычисляем угол поворота φ
        if A[i_max, i_max] == A[j_max, j_max]:
            phi = np.pi / 4  # Если диагональные элементы равны, угол φ = π/4
        else:
            phi = 0.5 * np.arctan2(2 * A[i_max, j_max], A[i_max, i_max] - A[j_max, j_max])

        cos_phi = np.cos(phi)
        sin_phi = np.sin(phi)

        # Формируем матрицу вращения H
        H = np.eye(n)
        H[i_max, i_max] = cos_phi
        H[j_max, j_max] = cos_phi
        H[i_max, j_max] = -sin_phi
        H[j_max, i_max] = sin_phi

        # Выполняем преобразование A = H^T * A * H
        A = H.T @ A @ H

        # Обновляем матрицу собственных векторов
        V = V @ H

    # Собственные значения на диагонали матрицы A
    eigenvalues = [A[i, i] for i in range(n)]
    # Собственные векторы — столбцы матрицы V
    eigenvectors = [V[:, i] for i in range(n)]

    return eigenvalues, eigenvectors

# Пример использования
A = [[2, 1], [1, 3]]
eigenvalues, eigenvectors = rotation_method(A)
print("Собственные значения:", eigenvalues)
print("Собственные векторы:", eigenvectors)'''
},
{
'''Используя метод Эйлера решите задачу Коши: y'(x)=y^2-x^2 y(0)=0.5 на интервале [0,4] с шагом h=0.05. Постройте график решения''': '''
# задача Коши
# метод Эйлера
# prompt: Using Euler's method solve the Cauchy problem:
# y'(x)=y^2-x^2
# y(0)=0.5
# on the interval [0,4] with step h=0.05. Draw the graph of the solution
def euler_method(f, y0, x0, xn, h):
    x_values = np.arange(x0, xn + h, h)
    y_values = np.zeros(len(x_values))
    y_values[0] = y0

    for i in range(len(x_values) - 1):
        y_values[i + 1] = y_values[i] + h * f(x_values[i], y_values[i])

    return x_values, y_values


# Определяем функцию правой части дифференциального уравнения
def f(x, y):
    return y**2 - x**2


# Начальные условия и интервал
x0 = 0
xn = 4
h = 0.05
y0 = 0.5

x_values, y_values = euler_method(f, y0, x0, xn, h)

# Строим график решения
plt.plot(x_values, y_values)
plt.xlabel('x')
plt.ylabel('y')
plt.title("Решение задачи Коши методом Эйлера")
plt.grid(True)
plt.show()'''
},
{
'''# Задача Коши метод Эйлера (система) + фазовый портрет''': '''
# Задача Коши метод Эйлера (система) + фазовый портрет
def euler_method(y1_prime, y2_prime, y1_initial, y2_initial, x_start, x_end, h):
    # Создаем массивы для хранения значений x, y1 и y2
    x_values = np.arange(x_start, x_end + h, h)
    y1_values = np.zeros(len(x_values))
    y2_values = np.zeros(len(x_values))

    # Начальные условия
    y1_values[0] = y1_initial
    y2_values[0] = y2_initial

    # Метод Эйлера
    for i in range(1, len(x_values)):
        y1_values[i] = y1_values[i - 1] + h * y1_prime(y1_values[i - 1], y2_values[i - 1])
        y2_values[i] = y2_values[i - 1] + h * y2_prime(y1_values[i - 1], y2_values[i - 1])

    return x_values, y1_values, y2_values

# Определяем функции для производных
def y1_prime(y1, y2):
    return np.arctan(1 / (1 + y1**2 + y2**2))

def y2_prime(y1, y2):
    return np.sin(y1 * y2)

# Параметры задачи
x_start = -1
x_end = 5
h = 0.0001
y1_initial = 1
y2_initial = 1

# Вызываем метод Эйлера
x_values, y1_values, y2_values = euler_method(y1_prime, y2_prime, y1_initial, y2_initial, x_start, x_end, h)

# Построение фазового портрета
plt.plot(y1_values, y2_values)
plt.xlabel("y1")
plt.ylabel("y2")
plt.title("Фазовый портрет")
plt.grid()
plt.show()'''
},
{
'''Решите задачу Коши методом адамса-мултона dy/dx = x^2 + y^2; y(0) = 1 на отрезке с шагом h = 0.02. Постройте график функции.''': '''
# решите задачу кошу методом адамса-мултона 
# dy/dx = x2 + y2; 
# y(0) = 1 на отрезке с шагом h = 0.02. 
# постройте график функции.

def adams_moulton_method(f, x0, y0, h, xn):
    # Создаём массив значений x от x0 до xn с шагом h
    x_values = np.arange(x0, xn + h, h)
    # Создаём массив для значений y, изначально заполняем нулями
    y_values = np.zeros(len(x_values))

    # Устанавливаем начальное условие: y(x0) = y0
    y_values[0] = y0

    # Для первого шага используем метод Эйлера:
    # y_{1} = y_{0} + h * f(x0, y0).
    y_values[1] = y_values[0] + h * f(x_values[0], y_values[0])

    # Применяем одношаговый метод Адамса–Мултона (метод трапеций).
    # Формула метода трапеций (предиктор–корректор):
    #
    # 1) Предиктор (обычно метод Эйлера):
    #    y_{i+1}^p = y_i + h * f(x_i, y_i).
    #
    # 2) Корректор (метод трапеции):
    #    y_{i+1} = y_i + (h / 2) * [f(x_i, y_i) + f(x_{i+1}, y_{i+1}^p)].
    #
    # В коде мы неявно вычисляем y_{i+1}^p и сразу подставляем в формулу корректора.
    for i in range(1, len(x_values) - 1):
        # Предиктор:
        y_pred = y_values[i] + h * f(x_values[i], y_values[i])
        # Корректор (используем y_pred):
        y_values[i+1] = y_values[i] + (h / 2) * (f(x_values[i], y_values[i]) + f(x_values[i+1], y_pred))

    return x_values, y_values

# Определяем функцию f(x, y) для уравнения dy/dx = x^2 + y^2
def f(x, y):
    return x**2 + y**2

# Задаём начальные условия и параметры
x0 = 0 # Начальное значение x
y0 = 1 # Начальное значение y
h = 0.02 # Шаг интегрирования
xn = 1 # Конечное значение x

# Решаем задачу Коши методом Адамса–Мултона
x_values, y_values = adams_moulton_method(f, x0, y0, h, xn)

# Строим график полученного решения
plt.plot(x_values, y_values, label="Численное решение")
plt.xlabel("x")
plt.ylabel("y")
plt.title("Решение задачи Коши методом Адамса–Мултона")
plt.grid(True)
plt.legend()
plt.show()'''
},
{
'''Решите задачу Коши методом Рунге-Кутта 3-го порядка y'(x)=x*y+atan(x) y(0)=1 методом Адамса-Мултона на интервале [0,2] с шагом h=0.01 Постройте график решения''': '''
# задача Коши методом Рунге-Кутта 3 порядка + Адамса-Мултона на интервале
# метод Рунге-Кутта 3 порядка
# y'(x)=x*y+atan(x)
# y(0)=1
# методом Адамса-Мултона на интервале [0,2] с шагом h=0.01 

# Задаём правую часть диф. уравнения
def f(x, y):
    return x*y + np.arctan(x)

# Один шаг метода Рунге–Кутты 3-го порядка
def runge_kutta_3_step(x_n, y_n, h):
    k1 = f(x_n, y_n)
    k2 = f(x_n + h/2, y_n + (h/2)*k1)
    k3 = f(x_n + h,   y_n - h*k1 + 2*h*k2)
    y_next = y_n + (h/6)*(k1 + 4*k2 + k3)
    x_next = x_n + h
    return x_next, y_next

#Параметры задачи
x0 = 0.0 # начальное значение x
y0 = 1.0 # начальное значение y(0)=1
h = 0.01 # шаг
X_end = 2.0 # конец отрезка
N = int((X_end - x0)/h)  # число шагов (для [0,2] при шаге 0.01 -> 200)

# Массивы для хранения x и y
x_vals = np.zeros(N+1) # будет [x0, x1, ..., xN], всего N+1 точек
y_vals = np.zeros(N+1) # будет [y0, y1, ..., yN]

# Инициализация начальных значений
x_vals[0] = x0
y_vals[0] = y0

# Сначала получим несколько точек методом Рунге–Кутты (3 порядка)
# (1) Первый шаг: (x0, y0) -> (x1, y1)
x1, y1 = runge_kutta_3_step(x_vals[0], y_vals[0], h)
x_vals[1], y_vals[1] = x1, y1

# (2) Второй шаг: (x1, y1) -> (x2, y2)
x2, y2 = runge_kutta_3_step(x_vals[1], y_vals[1], h)
x_vals[2], y_vals[2] = x2, y2

# Теперь у нас есть три точки: (x0, y0), (x1, y1), (x2, y2).
# С ними можно начинать многошаговый метод Адамса–Мултона.

# Многошаговый метод Адамса–Мултона (c предиктором)
for n in range(2, N):
    # Текущие x_n, y_n
    x_n   = x_vals[n]
    y_n   = y_vals[n]
    # Также нужны x_{n-1}, y_{n-1} и, конечно, x_{n+1}.
    x_nm1 = x_vals[n-1]
    y_nm1 = y_vals[n-1]
    x_np1 = x_n + h  # Следующая точка по x

    # Предиктор (Адамс–Башфорт 2-шаг)
    f_n   = f(x_n,   y_n)
    f_nm1 = f(x_nm1, y_nm1)

    y_np1_pred = y_n + (h/2)*(3*f_n - f_nm1)  # (n+1)-я точка, предсказание

    # Корректор (Адамс–Мултон 2-шаг)
    f_np1_pred = f(x_np1, y_np1_pred)
    y_np1_corr = y_n + (h/12)*(5*f_np1_pred + 8*f_n - f_nm1)

    # Записываем скорректированное значение
    x_vals[n+1] = x_np1
    y_vals[n+1] = y_np1_corr

# ===== 6. Построение графика =====
plt.figure(figsize=(8,5))
plt.plot(x_vals, y_vals, '-', label='Численное решение')
plt.xlabel('x')
plt.ylabel('y')
plt.title("y'(x)=x*y + arctan(x)")
plt.grid(True)
plt.legend()
plt.show()'''
},
{
'''Решить систему дифференциальных уравнений методом Рунге-Кутты порядка 4 dx/dt=x+y dy/dt=y-x x(0)=1, y(0)=0 на интервале [0,1] с шагом h=0.01. построить фазовый портрет.''': '''
# решить систему дифф ур
# метод Рунге-Кутта 4 порядка
# dx/dt=x+y 
# dy/dt=y-x 
# x(0)=1, 
# y(0)=0 на интервале [0,1] 
# с шагом h=0.01. построить фазовый портрет.

def runge_kutta_4(f1, f2, x0, y0, t0, tf, h):
    # Формируем массив времени t от t0 до tf с шагом h
    t = np.arange(t0, tf + h, h)

    # Инициализируем массивы для x и y
    x = np.zeros(len(t))
    y = np.zeros(len(t))

    # Задаём начальные условия
    x[0] = x0
    y[0] = y0

    # Проходим по всем шагам метода Рунге–Кутты 4-го порядка
    for i in range(len(t) - 1):
        # k1_x, k1_y соответствуют f1, f2 в точке (x[i], y[i])
        # Формула: k1_x = h * f1(x[i], y[i])
        k1_x = h * f1(x[i], y[i])
        k1_y = h * f2(x[i], y[i])

        # k2_x, k2_y соответствуют f1, f2 в точке (x[i] + k1_x/2, y[i] + k1_y/2)
        # Формула: k2_x = h * f1(x[i] + k1_x/2, y[i] + k1_y/2)
        k2_x = h * f1(x[i] + k1_x / 2, y[i] + k1_y / 2)
        k2_y = h * f2(x[i] + k1_x / 2, y[i] + k1_y / 2)

        # k3_x, k3_y аналогичны k2, но подставляем (x[i] + k2_x/2, y[i] + k2_y/2)
        k3_x = h * f1(x[i] + k2_x / 2, y[i] + k2_y / 2)
        k3_y = h * f2(x[i] + k2_x / 2, y[i] + k2_y / 2)

        # k4_x, k4_y вычисляются в точке (x[i] + k3_x, y[i] + k3_y)
        k4_x = h * f1(x[i] + k3_x, y[i] + k3_y)
        k4_y = h * f2(x[i] + k3_x, y[i] + k3_y)

        # Итоговое обновление x[i+1] и y[i+1]:
        #   x[i+1] = x[i] + (k1_x + 2*k2_x + 2*k3_x + k4_x)/6
        #   y[i+1] = y[i] + (k1_y + 2*k2_y + 2*k3_y + k4_y)/6
        x[i+1] = x[i] + (k1_x + 2*k2_x + 2*k3_x + k4_x) / 6
        y[i+1] = y[i] + (k1_y + 2*k2_y + 2*k3_y + k4_y) / 6

    return t, x, y

# Определяем правые части системы:
# dx/dt = x + y
def f1(x, y):
    return x + y

# dy/dt = y - x
def f2(x, y):
    return y - x

# Начальные условия и диапазон интегрирования
x0 = 1 # x(0) = 1
y0 = 0 # y(0) = 0
t0 = 0 # начальный момент времени
tf = 1 # конечный момент времени
h = 0.01 # шаг интегрирования

# Решаем систему методом Рунге–Кутты 4-го порядка
t, x, y = runge_kutta_4(f1, f2, x0, y0, t0, tf, h)

# Строим фазовый портрет (график y в зависимости от x)
plt.plot(x, y)
plt.xlabel("x(t)")
plt.ylabel("y(t)")
plt.title("Фазовый портрет системы dx/dt=x+y, dy/dt=y−x")
plt.grid(True)
plt.show()'''
},
{
'''Для функции
F(k)= k*sin(3k)*atan(2k), |k|<=3
иначе 0
выполните дискретное преобразование Фурье. постройте восстановленный сигнал''': '''
# дискретное преобразование Фурье (система) + построить восстановленный сигнал
# Для функции
# F(k)= k*sin(3k)*atan(2k), |k|<=3
# иначе 0
# выполните дискретное преобразование Фурье. постройте восстановленный сигнал

import numpy as np
import matplotlib.pyplot as plt

def F(k):
    """
    Определяет функцию:
    F(k) = k * sin(3k) * atan(2k), если |k| <= 3,
    и 0 во всех остальных случаях.
    """
    if abs(k) <= 3:
        return k * np.sin(3 * k) * np.arctan(2 * k)
    else:
        return 0

# Задаём сетку значений k на отрезке [-5, 5].
# Количество точек N = 1000 (можно увеличить для лучшей точности).
k_values = np.linspace(-5, 5, 1000)
N = len(k_values)

# Вычисляем F(k) в каждой точке сетки
f_k_values = np.array([F(k) for k in k_values])

# Реализуем дискретное преобразование Фурье (DFT).
#
# По определению (прямое DFT):
#   F_k[m] = sum_{n=0}^{N-1} f[n] * exp(-j * 2π * (m * n / N)),  m = 0..N-1
#
# где f[n] = f_k_values[n].
F_k = np.zeros(N, dtype=complex)  # Массив для хранения значений DFT
for m in range(N):
    for n in range(N):
        F_k[m] += f_k_values[n] * np.exp(-1j * 2 * np.pi * m * n / N)

# Восстанавливаем сигнал (обратное DFT).
#
# По определению (обратное DFT):
#   f[n] = (1/N) * sum_{m=0}^{N-1} F_k[m] * exp(+j * 2π * (m * n / N)),  n = 0..N-1
#
# В результате получаем восстановленное приближение исходного сигнала.
reconstructed_f_k = np.zeros(N, dtype=complex)
for n in range(N):
    for m in range(N):
        reconstructed_f_k[n] += F_k[m] * np.exp(1j * 2 * np.pi * m * n / N)
reconstructed_f_k = reconstructed_f_k / N  # Учитываем нормирующий множитель 1/N

# Построим графики исходной и восстановленной функций
plt.figure(figsize=(12, 6))

# График исходной функции F(k)
plt.subplot(1, 2, 1)
plt.plot(k_values, f_k_values, label='Оригинал')
plt.title('Оригинальная функция F(k)')
plt.xlabel('k')
plt.ylabel('F(k)')
plt.grid(True)
plt.legend()

# График восстановленной функции F(k) (берём действительную часть, т.к. результат — комплексный)
plt.subplot(1, 2, 2)
plt.plot(k_values, reconstructed_f_k.real, label='Восстановление')
plt.title('Восстановленная функция F(k)')
plt.xlabel('k')
plt.ylabel('Re(F(k))')
plt.grid(True)
plt.legend()

plt.tight_layout()
plt.show()'''
},
{
'''Для функциии f(t)=sin(2*pi*t)+cos(6*pi*t) выполните дискретное преобразование Фурье и удалите компоненты с частотой выше 5 Гц. Постройте восстановленный сигнал и сравните его с исходным.''': '''
# Для функциии f(t)=sin(2*pi*t)+cos(6*pi*t) выполните дискретное преобразование Фурье
#  и удалите компоненты с частотой выше 5 Гц.
#  Постройте восстановленный сигнал и сравните его с исходным.
# Частота дискретизации
fs = 500  # 5 Гц

# Функция f(t)
# sin(2 * pi * t) соответствует частоте 1 Гц,
# cos(6 * pi * t) соответствует частоте 3 Гц
def f(t):
    return np.sin(2 * np.pi * t) + np.cos(6 * np.pi * t)

# Формируем временной вектор (t)
# от 0 до 1 с 500 отсчётами (endpoint=False означает, что 1 не включается)
t = np.linspace(0, 1, fs, endpoint=False)

# Исходный сигнал
original_signal = f(t)

# Число отсчётов
N = len(t)

# Выполнение ДПФ
# fourier_coeffs[k] = сумма по n=0..N-1 от x[n] * exp(-j*2*pi*(k*n)/N)
# Здесь k меняется от 0 до N-1
fourier_coeffs = np.zeros(N, dtype=complex)
for k in range(N):
    # Реализуем формулу DFT в лоб (наивная реализация)
    for n in range(N):
        fourier_coeffs[k] += original_signal[n] * np.exp(-1j * 2 * np.pi * k * n / N)

# Определение частот в Гц
# Чтобы корректно учитывать положительные и отрицательные частоты, используем симметричную развёртку:
# Частоты от 0 до fs/2 для k < N/2 и от -fs/2 до 0 для k >= N/2
frequencies = np.zeros(N)
for k in range(N):
    if k <= N // 2:
        frequencies[k] = k * fs / N
    else:
        frequencies[k] = (k - N) * fs / N

# Отсечение частот выше 5 Гц
# Ищем индексы, где |frequency| > 5
indices_to_remove = np.where(np.abs(frequencies) > 5)[0]

# Обнуляем высокочастотные компоненты
filtered_coeffs = np.copy(fourier_coeffs)
filtered_coeffs[indices_to_remove] = 0

# Обратное преобразование (IDFT)
# reconstructed_signal[n] = (1/N) * сумма по k=0..N-1 от X[k] * exp(+j*2*pi*k*n/N)
reconstructed_signal = np.zeros(N, dtype=complex)
for n in range(N):
    for k in range(N):
        reconstructed_signal[n] += filtered_coeffs[k] * np.exp(1j * 2 * np.pi * k * n / N)

reconstructed_signal = reconstructed_signal / N  # Масштабируем результат

# Графики
plt.figure(figsize=(12, 6))

# Исходный сигнал
plt.subplot(2, 1, 1)
plt.plot(t, original_signal, label='Original')
plt.title('Исходный сигнал')
plt.xlabel('Время (с)')
plt.ylabel('Амплитуда')
plt.grid(True)

# Восстановленный сигнал (реальная часть)
plt.subplot(2, 1, 2)
plt.plot(t, reconstructed_signal.real, label='Reconstructed')
plt.title('Восстановленный сигнал (частоты <= 5 Гц)')
plt.xlabel('Время (с)')
plt.ylabel('Амплитуда')
plt.grid(True)

plt.tight_layout()
plt.show()'''
},
{
'''Выполните дискретное преобразование Фурье для функции f(t) = (e**(-t))*cos(6*pi*t), удалите высокочастотные компоненты с частотой более 10 Гц, Восстановите сигнал и оцените потери''': '''
#Выполните дискретное преобразование Фурье для функции 
# f(t) = (e**(-t))*cos(6*pi*t), 
# удалите высокочастотные компоненты с частотой более 10 Гц, 
# Восстановите сигнал и оцените потери

import numpy as np
import matplotlib.pyplot as plt

# Определяем частоту дискретизации
fs = 500 # 5 Гц
# Временной вектор (N=500 отсчётов, 1 секунда)
t = np.linspace(0, 1, 500, endpoint=False)
N = len(t)

# Определяем исходную функцию:
# f(t) = exp(-t) * cos(6πt)
# Здесь exp(-t) - затухающая экспонента, cos(6πt) - косинусная компонента с частотой 3 Гц,
# так как 6π = 2π * 3, значит частота равна 3 Гц.
def f(t):
    return np.exp(-t) * np.cos(6 * np.pi * t)

# Исходный сигнал
original_signal = f(t)

# Ручное вычисление прямого ДПФ
# DFT-формула (Discrete Fourier Transform):
# X[k] = Σ (от n=0 до N-1) x[n] * exp(-j * 2π * k * n / N),
# где k = 0,1,...,N-1
fourier_coeffs = np.zeros(N, dtype=complex)
for k in range(N):
    s = 0j
    for n in range(N):
        # exp(-1j * 2πkn/N)
        s += original_signal[n] * np.exp(-1j * 2 * np.pi * k * n / N)
    fourier_coeffs[k] = s

# Создаём массив частот (в Гц)
# Для индекса k частота в герцах может быть найдена по формуле:
# freq[k] = (k, если k <= N/2) или (k-N, если k > N/2) всё это умножить на fs/N.
#
# При N=500 и fs=500 Гц:
#  - k от 0 до 250 даёт частоты 0..250 Гц
#  - k от 251 до 499 даёт «эффективные» частоты -249..-1 Гц (если смотреть на стандартный вывод FFT)
# Мы вручную учитываем эту «отрицательную» часть:
freqs = np.zeros(N)
for k in range(N):
    if k <= N // 2:
        freqs[k] = k * fs / N
    else:
        freqs[k] = (k - N) * fs / N

# Удаляем высокочастотные компоненты (> 10 Гц)
# Ищем индексы, где частота по модулю больше 10 Гц
indices_to_remove = np.where(np.abs(freqs) > 10)

# Копируем исходные спектральные коэффициенты и «забиваем» нулями те, что > 10 Гц
filtered_coeffs = np.copy(fourier_coeffs)
filtered_coeffs[indices_to_remove] = 0

# Ручное вычисление обратного ДПФ
# IDFT-формула (Inverse Discrete Fourier Transform):
# x[n] = (1/N) * Σ (от k=0 до N-1) X[k] * exp(+j * 2π * k * n / N),
# где n = 0,1,...,N-1
reconstructed_signal = np.zeros(N, dtype=complex)
for n in range(N):
    s = 0j
    for k in range(N):
        s += filtered_coeffs[k] * np.exp(1j * 2 * np.pi * k * n / N)
    # Делим на N (масштабируем результат)
    reconstructed_signal[n] = s / N

# Преобразуем к вещественной части (исходный сигнал вещественный)
reconstructed_signal = reconstructed_signal.real

# Оценка потерь (MSE)
# MSE (Mean Squared Error) = (1/N)*Σ (|orig[n] - recon[n]|^2)
loss = np.mean((original_signal - reconstructed_signal)**2)

# Построение графиков
plt.figure(figsize=(12, 6))

plt.subplot(2, 1, 1)
plt.plot(t, original_signal, label='Оригинальный сигнал')
plt.title('Оригинальный сигнал')
plt.xlabel('Время (с)')
plt.ylabel('Амплитуда')
plt.grid(True)

plt.subplot(2, 1, 2)
plt.plot(t, reconstructed_signal, label='Восстановленный сигнал (<= 10 Гц)')
plt.title('Восстановленный сигнал (с частотами не выше 10 Гц)')
plt.xlabel('Время (с)')
plt.ylabel('Амплитуда')
plt.grid(True)

plt.tight_layout()
plt.show()

print(f"Потери (MSE): {loss}")'''
},
{
'''Для функции f(x)=e^(-x)^2+atan(x) выполните быстрое преобразование Фурье. Постройте график исходного сигнала и спектра частот''': '''
# быстрое преобразование
# Для функции f(x)=e^(-x)^2+atan(x) выполните быстрое преобразование Фурье. 
# Постройте график исходного сигнала и спектра частот

# 1) Определяем функцию и задаём сетку по времени (x)
def f(x):
    return np.exp(-x**2) + np.arctan(x)

# Интервал от -5 до +5
x_min = -5.0
x_max =  5.0
N = 500  # Число точек
x = np.linspace(x_min, x_max, N)

# Вычисляем значения сигнала
signal = f(x)

# 2) Наивное вычисление DFT

# Период выборки и частота выборки (fs)
dx = x[1] - x[0]     # Шаг между соседними точками
fs = 1.0 / dx        # «Частота дискретизации»

# Массив для результатов преобразования (комплексный)
spectrum = np.zeros(N, dtype=complex)

# Наивный двойной цикл: DFT[k] = Σ signal[n] * exp(-i * 2π * k * n / N)
for k in range(N):
    for n in range(N):
        spectrum[k] += signal[n] * np.exp(-1j * 2 * np.pi * k * n / N)

# Сдвиг спектра, чтобы частоты были "вокруг нуля"

# Шагаем по частотам от -N/2 до +N/2-1
# Шаг по частоте: fs/N
freq_step = fs / N
freq = (np.arange(N) - N//2) * freq_step

# "Сдвигаем" сам спектр на -N//2 индексов,
# чтобы нулевая частота оказалась в центре массива
spectrum_shifted = np.roll(spectrum, -N//2)

# Построение графиков

plt.figure(figsize=(12, 6))

# Исходный сигнал
plt.subplot(1, 2, 1)
plt.plot(x, signal, label='f(x)')
plt.title('Исходный сигнал')
plt.xlabel('x (время)')
plt.ylabel('Амплитуда')
plt.grid(True)
plt.legend()

# Спектр (по модулю), от отрицательных частот к положительным
plt.subplot(1, 2, 2)
plt.plot(freq, np.abs(spectrum_shifted), label='|DFT|')
plt.title('Частотный спектр (сдвинутый около 0)')
plt.xlabel('Частота')
plt.ylabel('Модуль спектра')
plt.grid(True)
plt.legend()

plt.tight_layout()
plt.show()'''
},
{
'''разложите функцию f(x)=sin^2(x)+cos(x) с использованием быстрого преобразования Фурье и визуализируйте спектр. Постройте восстановленную функцию''': '''
# разложить быстрым преобразованием Фурье
# визуализируйте спектр и постройте восстановленную функцию

# разложите функцию f(x)=sin^2(x)+cos(x) с использованием быстрого 
# преобразования Фурье и визуализируйте спектр. 
# Постройте восстановленную функцию

# Определяем функцию f(x)
def f(x):
    return np.sin(x)**2 + np.cos(x)

# Задаем диапазон и количество точек
x = np.linspace(0, 2 * np.pi, 500) # 500 точек на отрезке [0, 2π]
N = len(x) # Общее число точек

# Вычисляем значения исходной функции
y = f(x)

# Прямое дискретное преобразование Фурье (DFT) без использования np.fft
# Формула DFT:
#   X[k] = ∑[n=0..N-1] x[n] * exp(-j * 2π * (k * n / N))
# где x[n] - это сигнал, а X[k] - комплексный спектр на частоте k.

spectrum = np.zeros(N, dtype=complex)
for k in range(N):
    for n in range(N):
        spectrum[k] += y[n] * np.exp(-1j * 2 * np.pi * k * n / N)

# Делаем зеркальный график спектра относительно 0

# Шаг между точками по оси x
dx = x[1] - x[0]

# Формируем массив индексов от -N/2 до N/2-1
# (для N четного это будет симметричный набор частот).
k_vals = np.arange(-N//2, N//2)
frequencies_shifted = k_vals / (N * dx)

# Теперь "сдвигаем" спектр так, чтобы отрицательные частоты шли первыми,
# а положительные — последними. Аналог fftshift(spectrum).
spectrum_shifted = np.roll(spectrum, N//2)

# Обратное дискретное преобразование Фурье (IDFT)
# Формула IDFT:
#   x[n] = (1 / N) * ∑[k=0..N-1] X[k] * exp(j * 2π * (k * n / N))
# Здесь мы восстанавливаем сигнал по спектру.

reconstructed_signal = np.zeros(N, dtype=complex)
for n_i in range(N):
    for k in range(N):
        reconstructed_signal[n_i] += spectrum[k] * np.exp(1j * 2 * np.pi * k * n_i / N)
reconstructed_signal = reconstructed_signal / N

# Визуализация результатов

plt.figure(figsize=(12, 6))

# Исходный сигнал
plt.subplot(2, 1, 1)
plt.plot(x, y, label='Исходный сигнал')
plt.title('Исходный сигнал f(x)')
plt.xlabel('x')
plt.ylabel('f(x)')
plt.grid(True)
plt.legend()

# мплитудный спектр, сдвинутый для симметрии
plt.subplot(2, 1, 2)
plt.plot(frequencies_shifted, np.abs(spectrum_shifted), label='Спектр (сдвинутый)')
plt.title('Спектр сигнала (сдвинутый)')
plt.xlabel('Частота')
plt.ylabel('|DFT|')
plt.grid(True)
plt.legend()

# Восстановленный сигнал
plt.figure(figsize=(12, 6))
plt.plot(x, reconstructed_signal.real, label='Восстановленный сигнал')
plt.title('Восстановленный сигнал (IDFT)')
plt.xlabel('x')
plt.ylabel('f(x)')
plt.grid(True)
plt.legend()

plt.tight_layout()
plt.show()'''
},
{
'''Решите задачу Коши методом предиктора-корректора: y'(t)=2y-t^2 y(0)=1 на интервале [0,3] с шагом h=0.05. Постройте график решения''': '''
# Решите задачу Коши методом предиктора-корректора: y'(t)=2y-t^2 y(0)=1 на интервале [0,3] с шагом h=0.05. Постройте график решения
import numpy as np
import matplotlib.pyplot as plt

def f(t, y):
    return 2*y - t**2

# Параметры задачи
t0 = 0.0
tmax = 3.0
h = 0.05

# Шагов будет:
N = int((tmax - t0)/h)

# Сетки по t
t = np.linspace(t0, tmax, N+1)  # массив из N+1 точек

# Массив значений решения
y = np.zeros(N+1)
y[0] = 1.0  # начальное условие

# Метод предиктора-корректора (Эйлер - трапеции)
for n in range(N):
    # Предиктор (явный Эйлер)
    y_pred = y[n] + h * f(t[n], y[n])
    
    # Корректор (трапеции)
    y[n+1] = y[n] + (h/2)*(
        f(t[n], y[n]) + f(t[n+1], y_pred)
    )

# Для сравнения - точное решение
def y_exact(t):
    return 0.5*t**2 + 0.5*t + 0.25 + 0.75*np.exp(2*t)

y_true = y_exact(t)

# Построение графика
plt.figure(figsize=(8,4))
plt.plot(t, y, '-', label='Предиктор-корректор (h=0.05)')
plt.plot(t, y_true, '-', label='Точное решение')
plt.xlabel('t')
plt.ylabel('y(t)')
plt.title("Решение задачи Коши: y' = 2y - t^2,  y(0)=1")
plt.legend()
plt.grid(True)
plt.show()'''
},]
