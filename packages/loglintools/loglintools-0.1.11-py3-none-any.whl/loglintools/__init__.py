def hlp():
    print(''' q1() -  код, q1_th() - теория
    q1 - Наивное умножение матрицы на вектор и умножение матриц
    q2 - Иерархия памяти, план кеша и LRU, промахи в обращении к кешу
    q3 - Алгоритм Штрассена
    q4 - Собственные векторы, собственные значения (важность, Google PageRank)
    q5 - Разложение Шура и QR-алгоритм
    q6 - Степенной метод
    q7 - Круги Гершгорина
    q8 - Разложение Шура, теорема Шура
    q9 - Нормальные матрицы, эрмитовы матрицы, унитарно диагонализуемые матрицы, верхне-гессенбергова форма матриц
    q10 - Спектр и псевдоспектр
    q11 - Неявный QR алгоритм (со сдвигами)
    q12 - Алгоритм на основе стратегии "разделяй и властвуй"
    q13 - Разреженные матрицы, форматы хранения разреженных матриц, прямые методы для решения больших разреженных систем
    q14 - Обыкновенные дифференциальные уравнения, задача Коши
    q15 - Локальная, глобальная ошибки
    q16 - Метод центральной разности
    q17 - Метод Эйлера
    q18 - Метод предиктора-корректора
    q19 - Метод Рунге-Кутты 1-4 порядков
    q20 - Методы Адамса-Мултона, методы Адамса-Бэшфорта
    q21 - Метод Милна
    q22 - Согласованность, устойчивость, сходимость, условия устойчивости
    q23 - Моделирование волны с использованием математических инструментов (амплитуда, период, длина волны, частота, Герц, дискретизация, частота дискретизации, фаза, угловая частота)
    q24_ex - пример решения дискретный фурье
    q24_ex2 - пример решения дискретный фурье с фильтрацией
    q24 - Дискретное преобразование Фурье, обратное дискретное преобразование Фурье их ограничения, симметрии в дискретном преобразовании Фурье
    q25 - Быстрое преобразование Фурье, его принципы, фильтрация сигнала с использованием быстрого преобразования Фурье
    q26 - Операции свёртки, связь с быстрым преобразованием Фурье, операции дискретной свёртки
    q27 - Дискретная свёртка и Тёплицевы матрицы (Ганкелевы матрицы)
    q28 - Циркулянтные матрицы. Матрицы Фурье.
    q29 - Быстрый матвек с циркулянтом
    q30 - метод вращений
    q31 - метод непосредственного развертывания''')


    
def q6():
    print('''
    def vec_norm(a):
    return (sum(i**2 for i in a))**0.5

def mat_vec_mult(matrix, vector): #перемножение матрицы на вектор
    num_rows = len(matrix)
    num_cols = len(matrix[0])
    result = [0] * num_rows
    for i in range(num_rows):
        for j in range(num_cols):
            result[i] += matrix[i][j] * vector[j]
    return result

def vec_dot(a, b): #произведение двух векторов
    return sum(ai * bi for ai, bi in zip(a, b))

def transpose_vector(vector): #Транспонирование вектора -> в одномерный список
    return [vector[i] for i in range(len(vector))]

def vec_mat_mult(vec, matrix): #перемножение вектора матрицу
    num_cols = len(matrix[0])
    result = [0] * num_cols

    for j in range(num_cols):
        for i in range(len(vec)):
            result[j] += vec[i] * matrix[i][j]
    return result


# Матрица A
A = [[6, 2, 1, 4],
     [2, 7, 3, 1],
     [1, 3, 8, 2],
     [4, 1, 2, 2]]

# Вектор x
x = [1, 1, 1, 1]

# Параметры алгоритма
tol = 1e-10
max_iter = 10000
lam_prev = 0

for i in range(max_iter):
    # Умножаем матрицу на вектор и нормируем результат
    x = mat_vec_mult(A, x)
    norm = vec_norm(x)
    x = [xi / norm for xi in x]

    # Считаем приближенное собственное значение
    xt = transpose_vector(x)
    lam = vec_dot(vec_mat_mult(xt, A), x) / vec_dot(xt, x)

    # Проверяем условие остановки
    if abs(lam - lam_prev) < tol:
        break
    lam_prev = lam

print(f'Наибольшее собственное значение: {lam}')
print(f'Собственный вектор:')
print(transpose_vector(x))

print('-----------------------')
eigenvalues, eigenvectors = np.linalg.eig(A)
print(f'Настоящие собственные значения:')
print(eigenvalues)
print(f'Настоящие собственные векторы:')
print(eigenvectors)''')
def q8():
    print('''
    # только с базовыми

def triu(matrix, k): # np.triu
    rows, cols = matrix.shape
    result = np.zeros_like(matrix)
    for i in range(rows):
        for j in range(cols):
            if j >= i + k:
                result[i, j] = matrix[i, j]
    return result

def matmul(A, B):
  n = A.shape[0]
  k = A.shape[1]
  m = B.shape[1]
  c = np.zeros((n, m))
  for i in range(n):
    for j in range(m):
      for s in range(k):
        c[i, j] += A[i, s] * B[s, j]
  return c

def vec_dot(a, b):
  return sum(ai * bi for ai, bi in zip(a, b))


def qr_decomposition(A):
  n, m = A.shape
  Q = np.zeros((m, n))
  R = np.zeros((n,n))
  for j in range(n):
    v = A[:, j]
    for i in range(j):
      R[i, j] = vec_dot(Q[:, i], A[:, j])
      v = v - R[i, j] * Q[:, i]
    R[j, j] = (sum(i**2 for i in v))**0.5
    Q[:, j] = [i/R[j,j] for i in v]
  return Q, R


def shur_dec(A, eps = 0.001):
  n = A.shape[0]
  U = np.eye(A.shape[0])
  while triu(A, 1).max() >= eps:
    Q, R = qr_decomposition(A)
    A = matmul(R, Q)
    U = matmul(U, Q)
  T = A
  return U, T

A = np.array([[1, 5, 3,6],
       [2, 7, 4,7],
       [1, 8, 9,8],
      [1,2,3,4]])
U, T = shur_dec(A)

print("Матрица U (унитарная):")
print(U)

print("Матрица T (верхнетреугольная):")
print(T)

# Проверка
print("Проверка разложения Шура (A ≈ U @ T @ U^*):")
print(np.allclose(A, U @ T @ U.T.conj()))''')
def q31():
    print('''
    import numpy as np
A = np.array([[7, 2, 1, 5], [2, 8, 3, 1], [1, 3, 6, 2], [5, 1, 2, 3]])

cf = np.poly(A)
ev_roots = np.roots(cf)

print(cf)
print(ev_roots)
print(np.linalg.eigvals(A))''')
def q31_th():
    print('''
    Метод непосредственного развёртывания предполагает решение характеристического уравнения для нахождения собственных значений.

$$\det\left(A - \lambda I \right) = 0$$

Данный метод хорошо подходит для нахождения собственных значений матриц не очень большого порядка (примерно $n \le 10$).

Естественно, сам метод предполгаеат нахождение корней полинома $n$, что представляет из себя отдельную довольно тяжёлую задачу как с точки зрения точности полученных решений, так и с точки зрения сложности вычислений. В случае матриц высших порядков как правило применяют иные методы, выбор метода в таком случае уже зависит от характера задачи (нахождение полного спектра матрицы или только наибольшего собственного значения, например).''')
def q30_th():
    print('''
    Метод вращений предназначен для поиска собственных значений и собственных векторов симметричных матриц. Основная идея заключается в последовательном обнулении внедиагональных элементов матрицы путём применения матриц вращения.

Метод используется для решения полной проблемы собственных значений симметрической матрицы и основан на преобразовании подобия исходной матрицы $A \in \mathbb{R}^{n \times n}$ с помощью ортогональной матрицы $H$.

Две матрицы $A$ и $A^{(i)}$ называются подобными ($A \sim A^{(i)}$ или $A^{(i)} \sim A$), если:

$$ A^{(i)} = H^{-1} A H \quad \text{или} \quad A = H A^{(i)} H^{-1},$$

где $H$ — невырожденная матрица.

В методе вращений в качестве $H$ берется ортогональная матрица, такая, что:

$$ H H^\top = H^\top H = E, \quad \text{т. е.} \quad H^\top = H^{-1}.$$



**Плюсы:**
1. Метод особенно эффективен для симметричных матриц, гарантируя высокую точность вычисленных собственных значений.
2. Алгоритм относительно прост в программировании и не требует сложных операций.
3. Метод хорошо работает с небольшими и средними симметричными матрицами.

**Минусы**
1. Для больших матриц метод требует много итераций, что делает его менее эффективным по сравнению с другими алгоритмами.
2. Для несоответствующих матриц этот метод не работает.
3. Для очень больших матриц вычислительные и временные затраты могут стать значительными.

---

**Сравнение метода вращений и QR-алгоритма**

| **Критерий**          | **Метод вращений (Якоби)**         | **QR-алгоритм**                     |
|------------------------|------------------------------------|-------------------------------------|
| **Применимость**      | Только для симметричных матриц    | Для всех квадратных матриц         |
| **Сходимость**        | Медленная                         | Быстрая для большинства матриц     |
| **Сложность**         | \( O(n^3) \) за итерацию           | \( O(n^3) \) за итерацию            |
| **Точность**          | Высокая для симметричных матриц   | Хорошая, но может страдать для плохо обусловленных матриц |
| **Масштабируемость**  | Плохо подходит для больших матриц | Более эффективно работает с большими матрицами |
| **Численная устойчивость** | Стабильный для симметричных матриц | Устойчив для большинства случаев   |''')
def q30():
    print('''
    def diag(matrix): # np.diag
    rows, cols = matrix.shape
    return np.array([matrix[i, i] for i in range(rows)])

def matmul(matrix_1, matrix_2):
    n = matrix_1.shape[0]
    k = matrix_1.shape[1]
    m = matrix_2.shape[1]

    result = np.zeros((n, m))

    for i in range(n):
        for j in range(m):
            for s in range(k):
                result[i][j] += matrix_1[i][s]*matrix_2[s][j]
    return result

def jacobi_method(A, eps=1e-8, max_iter=100):
    n = A.shape[0]
    vecs = np.eye(n)

    for i in range(max_iter):
        # находим наибольшее по модулю значение в верхней наддиагональной части матрицы
        max_val = 0
        for i in range(n):
            for j in range(i + 1, n):
                if abs(A[i, j]) > abs(max_val):
                    max_val = A[i, j]
                    p, q = i, j

        # проверка условия окончания процесса
        if abs(max_val) < eps:
            break

        # находим угол phi
        if A[p, p] == A[q, q]:
            phi = np.pi / 4
        else:
            phi = 0.5 * np.arctan(2 * A[p, q] / (A[p, p] - A[q, q]))

        # составляем матрицу вращения
        H = np.eye(n)
        H[p, p] = np.cos(phi)
        H[q, q] = np.cos(phi)
        H[p, q] = -np.sin(phi)
        H[q, p] = np.sin(phi)

        # matmul - наивное умножение матриц, из вопроса 1
        A = matmul(matmul(H.T, A), H)
        vecs = matmul(vecs, H)

    vals = diag(A)
    return vals, vecs

A = np.array([
    [1, 2, 3],
    [2, 6, 4],
    [3, 4, 5]
])

true_eigvals, true_eigvec = np.linalg.eig(A)
print("numpy:")
print("values:")
display(true_eigvals)
print("vectors:")
for v in true_eigvec:
    display(v)

print("jacobi:")
eigvals, eigvec = jacobi_method(A)
print("values:")
display(eigvals)
print("vectors:")
for v in eigvec:
    display(v)''')
def q29():
    print('''
    import time
import numpy as np
import scipy as sp
import scipy.linalg

n = 5000

c = np.random.randn(n)
C = sp.linalg.circulant(c)
x = np.random.randn(n)

def circulant_matvec(c, x):
    return np.fft.ifft(np.fft.fft(c) * np.fft.fft(x))

y_full = C.dot(x)
full_time = %timeit -q -o C.dot(x)

print(f'Время полного матвека = {full_time.average}')

y_fft = circulant_matvec(c, x)
fft_time = %timeit -q -o circulant_matvec(c, x)

print(f'Время FFT= {fft_time.average}')

print(f'Относительная ошибка = {np.linalg.norm(y_full - y_fft) / np.linalg.norm(y_full)}')''')
def q27():
    print('''
    #пример теплицевой матрицы
import numpy as np
from scipy.linalg import toeplitz

row_0 = [1,2,3,4,5]
column_0 = [1,6,7,8,9]

a = toeplitz(row_0, column_0)
a''')
def q25():
    print('''
    import matplotlib.pyplot as plt
import numpy as np
from numpy.fft import fft, ifft

def concatenate(arrays): # np.concatenate вроде использовать нельзя
    result = []
    for arr in arrays:
        result.extend(arr)

    return np.array(result)

def FFT(x):
    N = len(x)

    if N == 1:
        return x
    else:
        X_even = FFT(x[::2])
        X_odd = FFT(x[1::2])
        factor = np.exp(-2j*np.pi*np.arange(N)/N)

        X = np.concatenate([X_even + factor[:int(N/2)] * X_odd,
                            X_even + factor[int(N/2):] * X_odd])

        return X

sr = 128 # Частота дискретизации. Здесь - степень 2
ts = 1/sr

t = np.arange(0, 1, ts)

freq = 1
x = 3 * np.sin(2*np.pi*freq*t)

freq = 4
x += 1 * np.sin(2*np.pi*freq*t)

freq = 7
x += 0.5 * np.sin(2*np.pi*freq*t)

plt.figure(figsize = (8, 4))
plt.plot(t, x, 'b')
plt.xlabel('Время')
plt.ylabel('Амплитуда')
plt.show()

X = FFT(x)

N = len(x)
n = np.arange(N)
T = N/sr
freq = n/T

plt.figure(figsize = (8, 4))
plt.subplot(121)
plt.stem(freq, abs(X), 'b', markerfmt = " ", basefmt = "-b")
plt.xlabel('Частота (Гц)')
plt.ylabel('Амплитуда DFT')

n_oneside = N//2
f_oneside = freq[:n_oneside]

X_oneside = X[:n_oneside]/n_oneside

plt.subplot(122)
plt.stem(f_oneside, abs(X_oneside), 'b', markerfmt = " ", basefmt = "-b")
plt.ylabel('Амплитуда')

plt.show()

def IFFT(X):
    N = len(X)
    if N <= 1:
        return X
    even = IFFT(X[::2])
    odd = IFFT(X[1::2])
    factor = np.exp(2j * np.pi * np.arange(N) / N)
    return np.concatenate([even + factor[:N // 2] * odd, even - factor[:N // 2] * odd]) /2

x = IFFT(X)
plt.figure(figsize = (8, 4))
plt.plot(t, x, 'b')
plt.xlabel('Время')
plt.ylabel('Амплитуда')
plt.show()''')
def q24_ex2():
    print('''
    #дискретный Фурье с фильтрацией
#пример
def f(t):
    return np.sin(2*np.pi*t)+np.cos(6*np.pi*t)

t = np.linspace(-1,1,100)
plt.plot(t, [f(elem) for elem in t])
plt.xlabel('время')
plt.ylabel('амплитуда')
plt.show()

#дискретное преобразование Фурье
def DFT(x):
    N = len(x)
    n = np.arange(N)
    k = n.reshape((N, 1))
    e = np.exp(-2j * np.pi * k * n / N)
    X = np.dot(e, x)
    return X

res = DFT(np.array([f(elem) for elem in t]))
N = len(t)
n = np.arange(N)
sr = 1/((t[-1]-t[0])/(len(t)-1))#частота дискретизации = 1 / ((конечное значение - начальное) / (кол-во точек - 1))
T = N/sr
freq = n/T


plt.figure(figsize = (8, 4))
plt.stem(freq, res, 'b', markerfmt = " ")
plt.xlabel('Частота (Гц)')
plt.ylabel('Амплитуда DFT')
plt.show()


#убираем частоты выше 5гц
# (В задании сказано удалить частоты, выше 5Гц, то есть по идее надо удалять по оси частот, т.е. по x, а не по величине амплитуды, надеемся что это ему и нужно)
res[5:] = 0
# res[res >= 5] = 0

plt.figure(figsize = (8, 4))
plt.stem(freq, res, 'b', markerfmt = " ")
plt.xlabel('Частота (Гц)')
plt.ylabel('Амплитуда DFT')
plt.show()


#обратное преобразование Фурье
def IDFT(X):
    N = len(X)
    n = np.arange(N)
    k = n.reshape((N, 1))
    e = np.exp((2j * np.pi * n * k)/N)
    x = 1/N * (np.dot(e, X))
    return x

res_idft = IDFT(res)
plt.figure(figsize = (8, 4))
plt.plot(t, res_idft , 'b')
plt.plot(t,[f(elem) for elem in t])
plt.xlabel('Время')
plt.ylabel('Амплитуда')
plt.show()''')
    
def q24_ex():
    print('''
    #пример
def f(k):
  if abs(k)<=3:
    return k*np.sin(3*k)*np.arctan(2*k)
  else:
    return 0

K = np.linspace(-3.5,3.5,100)
plt.plot(K, [f(elem) for elem in K])
plt.xlabel('время')
plt.ylabel('амплитуда')
plt.show()

#дискретное преобразование Фурье
def DFT(x):
    N = len(x)
    n = np.arange(N)
    k = n.reshape((N, 1))
    e = np.exp(-2j * np.pi * k * n / N)
    X = np.dot(e, x)
    return X

res = DFT(np.array([f(elem) for elem in K]))
N = len(K)
n = np.arange(N)
sr = 1/((K[-1]-K[0])/(len(K)-1)) #частота дискретизации = 1 / ((конечное значение - начальное) / (кол-во точек - 1))
T = N/sr
freq = n/T

plt.figure(figsize = (8, 4))
plt.stem(freq, abs(res), 'b', markerfmt = " ")
plt.xlabel('Частота (Гц)')
plt.ylabel('Амплитуда DFT')
plt.show()

#обратное преобразование Фурье
def IDFT(X):
    N = len(X)
    n = np.arange(N)
    k = n.reshape((N, 1))
    e = np.exp((2j * np.pi * n * k)/N)
    x = 1/N * (np.dot(e, X))
    return x

k = IDFT(res)
plt.figure(figsize = (8, 4))
plt.plot(K, k, 'b')
plt.xlabel('Время')
plt.ylabel('Амплитуда')
plt.show()''')
def q24():
    print('''
    import matplotlib.pyplot as plt
import numpy as np
from numpy.fft import fft, ifft

sr = 100 # Частота дискретизации
ts = 1/sr

t = np.arange(0, 1, ts)

freq = 1
x = 3 * np.sin(2*np.pi*freq*t)

freq = 4
x += 1 * np.sin(2*np.pi*freq*t)

freq = 7
x += 0.5 * np.sin(2*np.pi*freq*t)

plt.figure(figsize = (8, 4))
plt.plot(t, x, 'b')
plt.xlabel('Время')
plt.ylabel('Амплитуда')
plt.show()

def DFT(x):
    N = len(x)
    n = np.arange(N)
    k = n.reshape((N, 1))
    e = np.exp(-2j * np.pi * k * n / N)
    X = np.dot(e, x)
    return X

X = DFT(x)
N = len(x)
n = np.arange(N)
T = N/sr
freq = n/T

plt.figure(figsize = (8, 4))
plt.stem(freq, abs(X), 'b', markerfmt = " ", basefmt = "-b")
plt.xlabel('Частота (Гц)')
plt.ylabel('Амплитуда DFT')
plt.show()

n_oneside = N//2
f_oneside = freq[:n_oneside]

X_oneside = X[:n_oneside]/n_oneside

fig = plt.figure(figsize = (12, 4))

plt.subplot(121)
plt.stem(f_oneside, abs(X_oneside), 'b', markerfmt = " ", basefmt = "-b")
plt.xlabel('Частота')
plt.ylabel('Амплитуда')

plt.subplot(122)
plt.stem(f_oneside, abs(X_oneside), 'b', markerfmt = " ", basefmt = "-b")
plt.xlim(0, 10)
plt.xlabel('Частота')
plt.ylabel('Амплитуда')

plt.show()

def IDFT(X):
    N = len(X)
    n = np.arange(N)
    k = n.reshape((N, 1))
    e = np.exp((2j * np.pi * n * k)/N)
    x = 1/N * (np.dot(e, X))
    return x

x = IDFT(X)
plt.figure(figsize = (8, 4))
plt.plot(t, x, 'b')
plt.xlabel('Время')
plt.ylabel('Амплитуда')
plt.show()''')
def q23():
    print('''
    sr = 100 # частота дискретизации
ts = 1/sr # шаг
t = np.arange(0, 1, ts)

freq = 5
y = np.sin(2*np.pi*freq*t)

fig = plt.figure(figsize = (8, 4))

plt.subplot(211)
plt.plot(t, y, 'b')
plt.ylabel('Амплитуда')


freq = 10
y = np.sin(2*np.pi*freq*t)

plt.subplot(212)
plt.plot(t, y, 'b')
plt.ylabel('Амплитуда')

plt.xlabel('Время')
plt.show()''')
def q21():
    print(''' 
    def func(x, y=1):
    return x*y + np.arctan(x)

def Milne(func, x, y0, h = 0.01):
    x0, x1 = x
    yl = [y0]
    xl = np.arange(x0, y0, h).tolist()

    # узнаем y для 4 точек через метод Рунге-Кутты
    for i in range(3):
        k1 = h * dydx(xl[i], yl[i])
        k2 = h * dydx(xl[i] + h/2, yl[i] + 1/2* k1)
        k3 = h * dydx(xl[i] +h/2, yl[i]+ 1/2 * k2)
        k4 = h * dydx(xl[i] + h, yl[i] + k3)

        yn = yl[i] + 1/6 * (k1 + 2*k2+ 2*k3 + k4)

        yl.append(yn)

    # Метод Милна
    for i in range(2, len(xl)-1):
        y_pred = yl[i-3] + (4*h/3) * (2*func(xl[i-2], yl[i-2]) - func(xl[i-1], yl[i-1]) + 2*func(xl[i], yl[i]))
        yn = yl[i-1] + (h/3) * (func(xl[i-1], yl[i-1]) + 4*func(xl[i], yl[i]) + f(xl[i+1], y_pred))
        yl.append(yn)
    xl.append(x1)

    return np.array(xl), np.array(yl)

x, y = Milne(func, (0, 2), 1)
plt.plot(x, y)''')
def q20():
    print('''  
    def dydx(x, y):
    return x**2 - np.sin(2*x)

def AdamsBashforth(x0, y0, endx=2, h=0.2):
    yl = [y0]
    xl = np.arange(x0, y0, h).tolist()

    # узнаем y для Трех точек через метод Рунге-Кутты
    for i in range(2):
        k1 = h * dydx(xl[i], yl[i])
        k2 = h * dydx(xl[i] + h/2, yl[i] + 1/2* k1)
        k3 = h * dydx(xl[i] +h/2, yl[i]+ 1/2 * k2)
        k4 = h * dydx(xl[i] + h, yl[i] + k3)

        yn = yl[i] + 1/6 * (k1 + 2*k2+ 2*k3 + k4)

        yl.append(yn)

    # Метод Адамса-Бэшфорта
    for i in range(2, len(xl)):
        yn = yl[i] + h/12 * (23*dydx(xl[i], yl[i]) - 16 * dydx(xl[i-1],yl[i-1]) + 5* dydx(xl[i-2], yl[i-2]))
        yl.append(yn)
    xl.append(endx)

    return np.array(xl), np.array(yl)
########################################################
def dydx(x, y=0):
    return x**2 - np.sin(2*x)

def AdamsMoulton(x0, y0, endx=2, h=0.02):
    yl = [y0]
    xl = np.arange(x0, y0, h).tolist()

    # узнаем y для Трех точек через метод Рунге-Кутты
    for i in range(2):
        k1 = h * dydx(xl[i], yl[i])
        k2 = h * dydx(xl[i] + h/2, yl[i] + 1/2* k1)
        k3 = h * dydx(xl[i] +h/2, yl[i]+ 1/2 * k2)
        k4 = h * dydx(xl[i] + h, yl[i] + k3)

        yn = yl[i] + 1/6 * (k1 + 2*k2+ 2*k3 + k4)

        yl.append(yn)

    # Метод Адамса-Мултона
    for i in range(2, len(xl)-1):
        yn = yl[i] + h/12 * (5*dydx(xl[i+1]) + 8*dydx(xl[i])- dydx(xl[i-1]))
        yl.append(yn)
    xl.append(endx)

    return np.array(xl), np.array(yl)''')
def q19():
    print('''
    def dydx(x, y):
  return x**2 - np.sin(2*x)

def rungeKutta(x0, y0, endx=2, h=0.2):
    yl = [y0]
    xl = np.arange(x0, endx, h).tolist()

    for i in range(len(xl)):

        k1 = h * dydx(xl[i], yl[i])
        k2 = h * dydx(xl[i] + h, yl[i] + k1)

        yn = yl[i] + k1/2 + k2/2

        yl.append(yn)
    xl.append(endx)
    return np.array(xl), np.array(yl)

def method_rk3(f, x_end, y0, N):
    h = x_end / N
    x = np.linspace(0, x_end, N+1)

    y = np.zeros((N+1, len(y0)))
    k1 = np.zeros_like(y0)
    k2 = np.zeros_like(y0)
    k3 = np.zeros_like(y0)
    y[0, :] = y0

    for n in range(N):
        k1 = h * f(x[n], y[n, :])
        k2 = h * f(x[n] + h/2, y[n, :] + k1/2)
        k3 = h * f(x[n] + h, y[n, :] - k1 + 2*k2)

        y[n + 1, :] = y[n, :] + (k1 + 4 * k2 + k3) / 6

    return x, y

#рунге-кутта 4-го порядка
def method_rk4(f, x_end, y0, N):
    h = x_end / N
    x = np.linspace(0, x_end, N+1)

    y = np.zeros((N+1, len(y0)))
    k1 = np.zeros_like(y0)
    k2 = np.zeros_like(y0)
    k3 = np.zeros_like(y0)
    k4 = np.zeros_like(y0)
    y[0, :] = y0

    for n in range(N):
        k1 = h * f(x[n], y[n, :])
        k2 = h * f(x[n] + h/2, y[n, :] + k1/2)
        k3 = h * f(x[n] + h/2, y[n, :] + k2/2)
        k4 = h * f(x[n] + h, y[n, :] + k3)

        y[n + 1, :] = y[n, :] + (k1 + 2 * (k2 + k3) + k4) / 6

    return x, y

def fsimple(x, y):
    return -np.sin(x)

x_1, y_1 = method_rk4(fsimple, 0.5, [1.0], 1)
x_5, y_5 = method_rk4(fsimple, 0.5, [1.0], 5)
x_50, y_50 = method_rk4(fsimple, 0.5, [1.0], 50)

print(f'Решение при х=0.5  и h=1 - {y_1[-1, 0]}')
print(f'Решение при х=0.5  и h=0.1 - {y_5[-1, 0]}')
print(f'Решение при х=0.5  и h=0.01 - {y_50[-1, 0]}')
print(f'Точное значение - {np.cos(0.5)}')


#рунге-кутта для решения системы диф.уравнений
import math

# Функция, содержащая правые части дифференциальных уравнений
def equations(x, y):
    return [y[1], math.exp(-x * y[0])]

def rk(func, x0, xf, y0, h):
    count = int((xf - x0) / h) + 1
    y = [y0[:]]  # создание массива y с начальными условиями
    x = x0

    for i in range(1, count):
        k1 = func(x, y[i - 1])
        k2 = func(x + h / 2, list(map(lambda arr1, arr2: arr1 + arr2 * h / 2, y[i - 1], k1)))
        k3 = func(x + h / 2, list(map(lambda arr1, arr2: arr1 + arr2 * h / 2, y[i - 1], k2)))
        k4 = func(x + h, list(map(lambda arr1, arr2: arr1 + arr2 * h, y[i - 1], k3)))

        y.append([])

        for j in range(len(y0)):
            y[i].append(y[i - 1][j] + h / 6 * (k1[j] + 2 * k2[j] + 2 * k3[j] + k4[j]))

        x += h

    return y
print(rk(equations, 0, 1, [0,0], 0.1))''')
def q18():
    print('''
    #задача Коши методом предиктора(явный метод эйлера)-корректора(модифицированный метод Эйлера (метод трапеций))
import numpy as np
import matplotlib.pyplot as plt

def predictor_corrector_euler(f, t_start, y0, t_end, h):
    t = np.arange(t_start, t_end + h, h)#массив значений времени
    y = np.zeros((len(t), len(y0)))  # Обработка y0 как вектора
    y[0] = y0  # Устанавливаем начальное условие

    for i in range(len(t) - 1):
        y_pred = y[i] + h * f(t[i], y[i])# Предиктор
        y[i + 1] = y[i] + (h / 2) * (f(t[i], y[i]) + f(t[i + 1], y_pred))# Корректор
    return t, y

# y' = 2y-t^2, y(0) = 1
f = lambda t, y: 2*y - t**2
t_start = 0
y0 = np.array([1])
t_end = 3
h = 0.005
t, y = predictor_corrector_euler(f, t_start, y0, t_end, h)

# Построение графика
plt.plot(t, y, label='Численное решение')
plt.xlabel('t')
plt.ylabel('y(t)')
plt.legend()
plt.title('Метод предиктора-корректора')
plt.grid(True)
plt.show()''')
def q17():
    print('''
    def euler(f, x_end, y0, N):
  h = x_end / N
  x = np.linspace(0.0, x_end, N+1)

  y = np.zeros((N+1, len(y0)))
  y[0,:] = y0
  for n in range(N):
      y[n+1, :] = y[n, :] + h*f(x[n], y[n,:])
  return x,y

def simple(x,y):
  return -np.sin(x)

x_5, y_5 = euler(simple, 0.5, [1.0], 5)
x_50, y_50 = euler(simple, 0.5, [1.0], 50)

print(f'Решение при х=0.5  и h = 0.1 -> {y_5[-1][0]}')
print(f'Решение при х=0.05  и h = 0.1 -> {y_50[-1][0]}')
print(f'Точное решение - {np.cos(0.5)}')



#решение системы дифференциальных уравнений методом Эйлера
import math

def equations(x, y): # Функция, содержащая правые части дифференциальных уравнений
    return [y[1], math.exp(-x * y[0])]

def eiler(func, x0, xf, y0, h):
    count = int((xf - x0) / h) + 1
    y = [y0[:]]  # создание массива y с начальными условиями
    x = x0
    for i in range(1, count):
        right_parts = func(x, y[i - 1])
        y.append([])  # добавление пустой строки

        for j in range(len(y0)):
            y[i].append(y[i - 1][j] + h * right_parts[j])

        x += h
    return y

print(eiler(equations, 0, 1, [0,0], 0.1))
''')
def q16():
    print('''
    def central_difference(f, x, h):
    return (f(x + h) - f(x - h)) / (2 * h)

# Пример функции
def f(x):
    return np.cos(np.pi*x)**3  # Пример функции: f(x) = cos(πx)^3

x = np.pi/2  # Точка, в которой будем вычислять производную
h = 0.01  # Шаг

# Вычисляем производную с помощью метода прямой разности
approx_derivative = central_difference(f, x, h)

# Для проверки вычислим производную с помощью библиотеки
x_sym = sp.symbols('x')
f_sym = sp.cos(sp.pi*x_sym)**3
exact_derivative = sp.diff(f_sym, x_sym).subs(x_sym, x)

print("Приближенное значение производной:", approx_derivative)
print("Точное значение производной:", exact_derivative.evalf())#evalf()-нужен, чтобы посчитать численное значение, иначе ответ будет вот таким:-3*pi*sin(1.5707963267949*pi)*cos(1.5707963267949*pi)**2''')
def q15():
    print('''
    import numpy as np
import sympy as sp
import matplotlib.pyplot as plt

def euler_method(f, t0, y0, h, t_end):
    t = np.arange(t0, t_end + h, h)
    y = np.zeros_like(t)
    y[0] = y0

    for i in range(1, len(t)):
        y[i] = y[i - 1] + h * f(t[i - 1], y[i - 1])

    return t, y # t - массив временных точек, y - массив зн-й решения


def f(t, y): # Пример задачи: dy/dt = y * sin(t)
    return y * np.sin(t)

# Параметры задачи
t0 = 0 # начальное время
y0 = 1 #  начальное условие
t_end = 5 # конечное время
h = 0.5  # шаг интегрирования

t_euler, y_euler = euler_method(f, t0, y0, h, t_end) # Численное решение методом Эйлера

#------- находим общее решение оду
t = sp.Symbol('t')   # Время
y = sp.Function('y') # Функция y(t)

func = sp.Eq(y(t).diff(t), y(t) * sp.sin(t))

solution = sp.dsolve(func, y(t))
print("Общее решение:", solution)
#--------------------------------
y_true = np.exp(-np.cos(t_euler)) # Общее решение

local_errors = np.abs(y_true - y_euler) # Локальная ошибка
global_error = local_errors[-1]

print('Локальные ошибки на каждом шаге:')
for t_i, error_i in zip(t_euler, local_errors):
    print(f't = {t_i:.2f}, локальная ошибка = {error_i:.5f}')

print(f'\nГлобальная ошибка: {global_error:.5f}')

# Построение графиков
plt.figure(figsize=(12, 6))

# Решение
plt.subplot(1, 2, 1)
plt.plot(t_euler, y_true, label="Точное решение", color="black", linewidth=2)
plt.plot(t_euler, y_euler, 'o--', label="Метод Эйлера", color="blue")
plt.xlabel("t")
plt.ylabel("y(t)")
plt.title("Решение ОДУ методом Эйлера")
plt.legend()
plt.grid(True)

# Локальная ошибка
plt.subplot(1, 2, 2)
plt.plot(t_euler, local_errors, 'o-', label="Локальная ошибка", color="red")
plt.axhline(global_error, color="green", linestyle="--", label="Глобальная ошибка")
plt.xlabel("t")
plt.ylabel("Ошибка")
plt.title("Локальные и глобальная ошибки метода Эйлера")
plt.legend()
plt.grid(True)

plt.show()''')
    
    
def q14():
    print('''
    import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

def solve_odu(f, t_span, y0, method='RK45'): # f - ф-я, t_span - кортеж (t0, tf), y0 - нач усл-е
    sol = solve_ivp(f, t_span, y0, method = method)
    return sol

def example_ode(t, y): # Пример: dy/dt = y * sin(t)
  return y * np.sin(t)

t_span = (0, 10)
y0 = np.array([1])

sol = solve_odu(example_ode, t_span, y0)

print(sol)

plt.plot(sol.t, sol.y[0, :])
plt.xlabel('t')
plt.ylabel('y(t)')
plt.title('решение оду dy/dt = y * np.sin(t)')
plt.grid(True)
plt.show()''')
    
def q13():
    print('''
    import scipy.sparse as sp
import numpy as np

# Пример разреженной матрицы
data = np.array([1, 2, 3, 4])
row_indices = np.array([0, 1, 2, 3])
col_indices = np.array([1, 2, 3, 4])

coo_matrix = sp.coo_matrix((data, (row_indices, col_indices)), shape=(5, 5))
print("COO формат:", coo_matrix)

csr_matrix = coo_matrix.tocsr()
print("CSR формат:", csr_matrix)

csc_matrix = coo_matrix.tocsc()
print("CSC формат:", csc_matrix)''')
def q12():
    print('''
    #код нерабочий, но вдруг поможет
import numpy as np

def div_conq_alg(A):
    n = A.shape[0]
    if n == 1:
        return np.array([A[0, 0]])

    A11 = A[:n//2, :n//2]    # Разделение матрицы на подматрицы
    A12 = A[:n//2, n//2:]
    A21 = A[n//2:, :n//2]
    A22 = A[n//2:, n//2:]

    eigvals_A11 = div_conq_alg(A11) # рекурсивно вычисляем собственные значения подматриц
    eigvals_A22 = div_conq_alg(A22)

    eigvals = np.concatenate((eigvals_A11, eigvals_A22)) # Комбинирование результатов

    return eigvals

A = np.array([[2, 1, 0],
              [1, 1, 5],
              [0, 3, 1]], dtype=float)  # Пример матрицы

eigenvalues_dac = div_conq_alg(A)
print("Собственные значения:", eigenvalues_dac)

true_eigvals, true_eigvec = np.linalg.eig(A)
true_eigvals''')
    
    
def q11():
    print('''
    def vec_dot(a, b):
  return sum(ai*bi for ai, bi in zip(a, b))

def matmul(A, B):
  n = A.shape[0]
  k = A.shape[1]
  m = B.shape[1]
  c = np.zeros((n, m))
  for i in range(n):
    for j in range(m):
      for s in range(k):
        c[i, j] += A[i, s] * B[s, j]
  return c

def norm2(v):
    s = 0
    for i in range(len(v)):
        s+= v[i]**2
    return s**(1/2)

def qr_decomposition(A):
    u = []
    e = []
    v = A.T[0]
    u.append(list(v))
    e.append(list(v/norm2(v)))
    for i in range(1, len(A)):
        v = A.T[i]
        u_ = v - sum([(vec_dot(u[z], v) / vec_dot(u[z], u[z])) * np.array(u[z]) for z in range(len(u))])
        u.append(list(u_))
        e.append(list(u_ / norm2(u_)))

    return np.array(e).T, np.array(e) @ A

def tril(A): # np.tril
    maxelem = -float('inf')
    for i in range(1, A.shape[0]):
        for j in range(0, i):
            maxelem = max(maxelem, A[i, j])

    return abs(maxelem)

def diag(matrix): # np.diag
    rows, cols = matrix.shape
    return np.array([matrix[i, i] for i in range(rows)])

def qr_alg_shifts(A, eps = 0.001):
  Q_final = np.eye(A.shape[0])
  Q_list = []
  while tril(A) > eps:
      Q, R = qr_decomposition(A - A[-1, -1] * np.eye(A.shape[0]))
      Q_list.append(Q)
      A = matmul(R, Q) + A[-1, -1] * np.eye(A.shape[0])
      Q_final = matmul(Q_final, Q)
  return A, diag(A), [Q_final[:, i] for i in range(Q_final.shape[1])]

A = np.array([[1, 3, 5, 7],
             [2, 4, 6, 8],
              [5, 5, 7, 9],
              [4,6,8,0]])
A_, eigval, eigvec = qr_alg_shifts(A)

eigval, np.linalg.eigvals(A)''')
    
def q10():
    print('''
    
A = np.array([[1, 1], [0, 1]]) # Пример матрицы

# Вычисление спектра
w, v = np.linalg.eig(A)
print("Спектр матрицы A:", w)


def pseudo_spectrum(A, epsilon): # Функция для вычисления псевдоспектра
    w, v = np.linalg.eig(A)
    pseudo_spectrum_vals = []
    for val in w:
      pseudo_spectrum_vals.append(val + epsilon) # примерное вычисление, требует уточнения в зависимости от задачи
    return np.array(pseudo_spectrum_vals)

# Вычисление псевдоспектра
epsilon = 0.01
pseudo_w = pseudo_spectrum(A, epsilon)
print(f"Псевдоспектр матрицы A (epsilon = {epsilon}):", pseudo_w)

# Визуализация (пример)
plt.figure(figsize=(8, 6))
plt.scatter(np.real(w), np.imag(w), label="Спектр", marker='o', s=100, color='blue')
plt.scatter(np.real(pseudo_w), np.imag(pseudo_w), label=f"Псевдоспектр (epsilon = {epsilon})", marker='x', s=100, color='red')
plt.xlabel("Действительная часть")
plt.ylabel("Мнимая часть")
plt.title("Спектр и псевдоспектр матрицы")
plt.legend()
plt.grid(True)''')
def q9():
    print('''
    from collections import OrderedDict
import scipy.linalg
# Пример нормальной матрицы
A = np.array([[4, 1], [1, 4]])
# Проверка нормальности
is_normal = np.allclose(A.T.conj() @ A, A @ A.T.conj())
print("Матрица нормальна:", is_normal)


# Пример эрмитовой матрицы
B = np.array([[3, 2+1j], [2-1j, 1]])
# Проверка эрмитовости
is_hermitian = np.allclose(B, B.T.conj())
print("Матрица эрмитова:", is_hermitian)


# Проверка унитарной диагонализуемости
def is_unitarily_diagonalizable(A, tol=1e-10):
    A_star = A.conj().T  # Эрмитово-сопряжённая матрица A
    norm_diff = np.linalg.norm(A @ A_star - A_star @ A)  # Норма разности A A* и A* A
    return norm_diff < tol
# Пример использования
A = np.array([[1, 0], [0, 1]], dtype=complex)
print(is_unitarily_diagonalizable(A))  # Вывод: True или False


# Пример приведения к верхне-гессенберговой форме
D = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
# Use scipy.linalg.hessenberg instead of np.linalg.hessenberg
H = scipy.linalg.hessenberg(D) # scipy.linalg contains the hessenberg function
print("Верхне-гессенбергова форма:")
H''')
def q7():
    print('''
    n = 3
fig, ax = plt.subplots(1, 1)
a = np.array([[5, 1, 1], [1, 0, 0.5], [2, 0, 10]])
a = a + 2 * np.random.randn(n, n)
xg = np.diag(a).real
yg = np.diag(a).imag
rg = np.zeros(n)
ev = np.linalg.eigvals(a)
for i in range(n):
    rg[i] = np.sum(np.abs(a[i, :])) - np.abs(a[i, i])
    crc = plt.Circle((xg[i], yg[i]), radius=rg[i], fill=False)
    ax.add_patch(crc)
plt.scatter(ev.real, ev.imag, color='r', label="Eigenvalues")
plt.axis('equal')
plt.legend()
ax.set_title('Eigenvalues and Gershgorin circles')
fig.tight_layout()''')
def q5():
    print('''
    def vec_dot(a, b):
  return sum(ai*bi for ai, bi in zip(a, b))

def matmul(A, B):
  n = A.shape[0]
  k = A.shape[1]
  m = B.shape[1]
  c = np.zeros((n, m))
  for i in range(n):
    for j in range(m):
      for s in range(k):
        c[i, j] += A[i, s] * B[s, j]
  return c

def norm2(v):
    s = 0
    for i in range(len(v)):
        s+= v[i]**2
    return s**(1/2)

def qr_decomposition(A):
    u = []
    e = []
    v = A.T[0]
    u.append(list(v))
    e.append(list(v/norm2(v)))
    for i in range(1, len(A)):
        v = A.T[i]
        u_ = v - sum([(vec_dot(u[z], v) / vec_dot(u[z], u[z])) * np.array(u[z]) for z in range(len(u))])
        u.append(list(u_))
        e.append(list(u_ / norm2(u_)))

    return np.array(e).T, np.array(e) @ A

def tril(A): # max elem in trie matrix
    maxelem = -float('inf')
    for i in range(1, A.shape[0]):
        for j in range(0, i):
            maxelem = max(maxelem, A[i, j])

    return abs(maxelem)

def diag(matrix): # np.diag
    rows, cols = matrix.shape
    return np.array([matrix[i, i] for i in range(rows)])

def QR_method(A, eps = 0.001):
  Q_final = np.eye(A.shape[0])
  Q_list = []
  while tril(A) > eps:
    Q, R = qr_decomposition(A)
    Q_list.append(Q)
    A = matmul(R, Q)
    Q_final = matmul(Q_final, Q)
  return A, np.diag(A), [Q_final[:, i] for i in range(Q_final.shape[1])]

A = np.array([[1, 3, 5, 7], [2, 4, 6, 8], [4, 5, 7, 9], [4, 6, 8, 0]])

Q, R = qr_decomposition(A)
A_, nums, vecs = QR_method(A)
print(f'Результат QR-разложения:\n{Q.round(5)}\n\n{R.round(5)}')
print('Результат QR - алгоритма')
print(A_)
print("Собственные значения:") #диагональные элементы матрицы A
print(nums)
print("Собственные векторы:") #произведение всех Q, полученных в результате алгоритма
list(map(display, vecs));
''')
    
def q3():
    print('''
    def strassen_multiply(A, B):
    n = A.shape[0]

    # Базовый случай: умножение 1x1 матриц -> база рекурсии
    if n == 1:
        return A * B

    # Разделение матриц на блоки
    mid = n // 2
    A11, A12, A21, A22 = A[:mid, :mid], A[:mid, mid:], A[mid:, :mid], A[mid:, mid:]
    B11, B12, B21, B22 = B[:mid, :mid], B[:mid, mid:], B[mid:, :mid], B[mid:, mid:]

    # Вычисление 7 промежуточных матриц
    M1 = strassen_multiply(A11 + A22, B11 + B22)
    M2 = strassen_multiply(A21 + A22, B11)
    M3 = strassen_multiply(A11, B12 - B22)
    M4 = strassen_multiply(A22, B21 - B11)
    M5 = strassen_multiply(A11 + A12, B22)
    M6 = strassen_multiply(A21 - A11,B11 + B12)
    M7 = strassen_multiply(A12 - A22, B21 + B22)

    # Сборка результирующей матрицы
    C11 = M1 +M4 - M5 + M7
    C12 = M3 + M5
    C21 = M2 + M4
    C22 = M1 + M3 - M2 + M6

    C = np.zeros((n, n))  # Создаем пустую матрицу для результата
    C[:mid, :mid] = C11
    C[:mid, mid:] = C12
    C[mid:, :mid] = C21
    C[mid:, mid:] = C22

    return C

A = np.random.randint(0,10,(8,8))
B = np.random.randint(0,10,(8,8))
C = strassen_multiply(A, B)
print("Результат умножения матриц:")
print(C)
print(A@B)''')

def q29_th(): 
    print('''
    Для проведения быстрого матвека может понадобится следующее важное свойство Циркулянта, связывающее его с матрицей Фурье:

$$C = \frac{1}{n} F_n^* diag(F_n \cdot c) F_n$$

$$(c - \text{столбец матрицы} \  C)$$

Для **быстрого матвека** с циркулянтом:

1. Вложим Теплицеву матрицу, построенную по необходимому вектору, в циркулянт:

$$C = \begin{pmatrix} c_0 & c_{-1} & c_{-2} & c_2 & c_1 \\ c_1 & c_0 & c_{-1} & c_{-2} & c_2 \\ c_2 & c_1 & c_0 & c_{-1} & c_{-2} \\ c_{-2} & c_2 & c_1 & c_0 & c_{-1} \\ c_{-1} & c_{-2} & c_2 & c_1 & c_0 \end{pmatrix}$$

2. Получаем произведение:

$$\begin{pmatrix} y_1 \\ y_2 \\ y_3 \\ * \\ * \end{pmatrix} = \begin{pmatrix} c_0 & c_{-1} & c_{-2} & c_2 & c_1 \\ c_1 & c_0 & c_{-1} & c_{-2} & c_2 \\ c_2 & c_1 & c_0 & c_{-1} & c_{-2} \\ c_{-2} & c_2 & c_1 & c_0 & c_{-1} \\ c_{-1} & c_{-2} & c_2 & c_1 & c_0 \end{pmatrix} \cdot \begin{pmatrix} x_1 \\ x_2 \\ x_3 \\ 0 \\ 0 \end{pmatrix}$$

3. Умножение на теплицеву => умножение на циркулянт. Из связи циркулянта с преобразованием Фурье получаем ($\circ$ - поэлементное множение):

$$\begin{pmatrix} y_1 \\ y_2 \\ y_3 \\ * \\ * \end{pmatrix} = ifft\bigg( fft(\begin{pmatrix} c_0 \\ c_1 \\ c_2 \\ c_{-2} \\ c_{-1} \end{pmatrix}) \circ fft(\begin{pmatrix} x_1 \\ x_2 \\ x_3 \\ 0 \\ 0 \end{pmatrix}) \bigg)$$''')
def q28_th(): 
    print('''
    **Циркулянт** или **циркулянтная матрица** — это матрица вида $$C = \begin{pmatrix} c_1 & c_n & ... & c_2 \\ c_2 & c_1 & ... & c_3 \\ \vdots & \vdots & ... & \vdots \\ c_n & c_{n - 1} & ... & c_1 \end{pmatrix}$$ Т.е. матрица, в которой любая следующая строка (столбец), начиная с первой (с первого) получается циклической алфавитной перестановкой элементов предыдущей строки (столбца).

**Матрица Фурье**

Дискретное преобразование Фурье является линейным преобразованием, которое переводит вектор временных отсчётов в вектор спектральных отсчётов той же длины. Таким образом преобразование может быть реализовано как умножение симметричной квадратной матрицы на вектор:

$$X = \mathcal{F}x$$

Где $\mathcal{F}$ - **матрица Фурье**

**Матрица Фурье** задаётся следующим образом: $\mathcal{F}(i, k) = w^{(i-1)(k-1)}, w = \exp\{-j \cdot \frac{2\pi}{N}\}$ и выглядит:

$$\mathcal{F} = \frac{1}{\sqrt{N}}\begin{pmatrix} 1 & 1 & 1 & ... & 1 \\ 1 & w & w^2 & ... & w^{N-1} \\ 1 & w^2 & w^4 & ... & w^{2(N-1)} \\ \vdots & \vdots & \vdots & ... & \vdots \\ 1 & w^{N-1} & w^{2(N-1)} & ... & w^{(N-1)^2} \end{pmatrix}$$''')
    
def q27_th(): 
    print('''
    **Дискретная свёртка и Тёплицевы матрицы**

Дискретную свёртку можно представить как умножение матрицы на вектор:

$$z_i = \sum_{j=0}^{n-1} x_j y_{i-j}, \Leftrightarrow z = Ax,$$

где элементы матрицы $A$ равны $a_{ij} = y_{i-j}$, то есть они зависят только от разности между индексами строки и столбца(и получается, что матрица A - Теплицева матрица)

**Тёплицевы матрицы**

Матрица называется Тёплицевой, если её элементы определены как $a_{ij} = t_{i-j}$

* Тёплицева матрица полностью определяется первой строкой и первым столбцом (то есть $2n-1$ параметр).

* Это плотная матрица, однако она имеет структуру, то есть определяется $O(n)$ параметрами (сравните с разреженными матрицами)

* Основная операция для вычисления дискретной свёртки – это произведение Тёплицевой матрицы на вектор.
''')
def q26_th(): 
    print('''
    **Свёртка**

* Одна из основных операций в обработке сигналов/машинном обучении – это свёртка двух функций

* Пусть $x(t)$ и $y(t)$ две данные функции. Их свёртка определяется как $$(x * y)(t) = ∫_{-∞}^{∞} x(τ) y(t - τ) dτ$$



**Теорема о свёртке и преобразование Фурье**(связь свертки и Фурье)

Широко известный факт: свёртка во временном пространстве (time domain) эквивалентна произведению в частотном пространстве (frequency domain).

* Преобразование из одного пространства в другое осуществляется с помощью преобразования Фурье:

$$\hat{x}(w) = (F(x))(w) = ∫_{-∞}^{∞}
 e^{iwt} x(t) dt$$

* Тогда $$F(x*y) = F(x)F(y)$$

* Таким образом, алгоритм вычисления свёртки можно записать следующим образом:

  1. Вычислить преобразование Фурье от $x(t)$ и $y(t)$
  2. Вычислить их произведение
  3. Применить к результату обратное преобразование Фурье


**Операция дискретной свёртки**

* Если приблизим интеграл $(x * y)(t) = ∫_{-∞}^{∞} x(τ) y(t - τ) dτ$ с помощью суммы значений подынтегрального выражения на равномерной сетке, тогда нам останется просуммировать выражение $$z_i = \sum_{j=0}^{n-1} x_j y_{i-j},$$

  которое называется **дискретной свёрткой**. Его можно рассматривать как применение фильтра с коэффициентами $x$ к сигналу $y$.''')
    
def q25_th(): 
    print('''
    Быстрое преобразование Фурье — алгоритм ускоренного вычисления дискретного преобразования Фурье, позволяющий получить результат за время, меньшее чем $O(N^2)$.

В основе алгоритма лежат идеи о симметрии ДПФ и принципы динамического программирования. Для снижения времени вычисления исходная последовательность делится на две подпоследовательности, работать с которыми значительно проще.

**Алгоритм БПФ:**

1. Разделение последовательности на две подпоследовательности из элементов на чётных и нечётных позициях.

$$x_{even}(n)=x(2n), \quad x_{odd}(n)=x(2n + 1)$$

2. Для каждой подпоследовательности рекурсивно выполняется алгоритм БПФ, пока длина последовательности не станет достаточно маленькой для прямого вычисления преобразования Фурье или пока длина последовательности не станет равна 1, в таком случае значение ДПФ равно самому элементу последовательности.

3. Комбинирование результатов. Для учёта вклада нечётных компонент рассчтывается величина $W_k=\exp\{-j \cdot \frac{2\pi k}{N}\}$. Результаты комбинируются следующим образом:

$$X(k)=X_{even}​(k)+W_k\cdot​X_{odd​}(k), \quad X(𝑘+𝑁/2)=X_{even}​(k)-W_k\cdot​X_{odd​}(k)$$

**Фильтрацяи сигнала с использованием БПФ:**

1. Сигнал разбивается на фрагменты
2. К каждому фрагменту применяется БПФ
3. Определяются частоты, которые необходимо отфильтровать. Их мощность ставится равной 0.
4. К каждому фрагменту применяем обратное преобразование Фурье, чтобы получить очищенный исходный сигнал.''')
def q24_th(): 
    print('''
    Для некоторой периодической последовательности отсчётов $\{x(k)\}$ с периодом $N$ верны следующие выражения.

Дискретное преобразование Фурье является спектром дискретного периодического сигнала, то есть, его разложением на гармоники.

**Дискретное преобразование Фурье:**

$$X(n) = \sum\limits_{k=0}^{N-1} x(k) \exp\{-j \cdot \frac{2\pi n k}{N}\}$$

**Обратное дискретное преобразование Фурье:**

$$x(k) = \frac{1}{N}\sum\limits_{k=0}^{N-1} X(n) \exp\{j \cdot \frac{2\pi n k}{N}\}$$

**Симметрии в дискретном преобразовании Фурье:**

1. Для вещественнозначных сигналов ДПФ является Эрмитовым (то есть имеет место симметрия:) $$X(-n) = X^*(n)$$
(Т.е. положительные частоты являются комплексно-сопряжёнными соответствующим отрицательным частотам)
2. Чётная и нечётная симметрии

    Если сигнал чётный ($x(k) = x(N-k)$), то его ДПФ будет вещественнозначным и чётным.

    Если сигнал нечётный ($x(k) = -x(N-k)$), то его ДПФ будет комплексным и нечётным.

**Ограничения и недостатки ДПФ:**
1. Алиасинг или наложение частот

    Неправильная дискретизация аналогового сигнала приводит к тому, что высокочастотные его составляющие накладываются на низкочастотные, в результате чего восстановление сигнала во времени приводит к его искажениям. Для предотвращения этого эффекта частота дискретизации должна быть достаточно высокой, а сигнал должен быть надлежащим образом отфильтрован перед оцифровкой.

2. Сложность вычислений

    Из выражений ДПФ можно видеть, что для вычисления каждой гармоники нужно $N$ операций комплексного умножения и сложения и соответственно $N^2$ операций на полное выполнение ДПФ.''')
def q23_th(): 
    print('''
    Моделирование волны основывается на математическом описании периодических колебаний, которые можно выразить с помощью тригонометрических функций, например, синуса или косинуса:  

y(t) = A * sin(ω * t + φ)

где:  
- A — амплитуда  
- ω — угловая частота  
- t — время  
- φ — фаза  

**Амплитуда (A)** - Максимальное отклонение волны от её среднего значения (обычно нуля). Определяет высоту волны.  

**Период (T)** - Время, за которое волна совершает один полный цикл.  

T = 1 / f, где f — частота.  

**Длина волны (lambda)** - Расстояние, которое волна проходит за один полный период.  

λ = v * T = v / f, где v — скорость распространения волны.  

**Частота (f)** - Количество циклов волны в единицу времени. Измеряется в Герцах.  

f = 1 / T

**Герц (Hz)** - Единица измерения частоты. 1 Герц равен одному циклу в секунду.  **Пример**: Если f = 2 Hz, это означает, что волна совершает два полных колебания за одну секунду.  

**Дискретизация** - Процесс преобразования непрерывного сигнала в последовательность дискретных точек.  **Зачем это нужно?** Для моделирования волны на компьютере, где все данные хранятся в цифровом формате.  

**Частота дискретизации**  - Количество измерений (сэмплов) волны в единицу времени.  

**Фаза (phi)** - Начальное смещение волны относительно нуля во времени.  


**Угловая частота (omega)** - Измеряется в радианах в секунду и показывает скорость изменения фазы волны.  ''')
def q22_th(): 
    print('''
    Условия сходимости:

1. Для неявного метода
$$y_{n + i} = h \frac{\boldsymbol{\beta}_k}{\boldsymbol{\alpha}_k} f\left(\mathbf{x}_{n + k}, y\left(\mathbf{x}_{n + k}\right)\right) + \mathbf{g}_n,\quad \boldsymbol{\beta}_k \neq 0.$$

если $\lim_{h \to 0} (y_n - y(x_n))=0$ - сходится

2. Метод класса $\sum{i=0}^k \alpha_i y_{n+i} - h \sum_{i=0}^n \beta_i f\left(x_{n+i}, y_{n+i}\right)$, $n=0,1,2,...$ сходится, если для каждой задачи Коши $y_n \rightarrow y\left(x_0\right)$ при $h \rightarrow 0$, $n=\frac{x-x_0}{h}$. Для любых $x \in [x_0, x_k]$.

Метод должен удовлетворять условию минимального уровня локальной
точности

---
Невязка $\rho_{n+k}$ которая получается после подстановки точного решения $y(x)$ дифференциального уравнения в разностное,
$$
\rho_{n+k}=\sum_{i=0}^k \alpha_i y_{n+i}-h \sum_{i=0}^n \beta_i f\left(x_{n+i}, y\left(x_{n+i}\right)\right)
$$
имеет порядок $O(h^{s+1})$ и называется погрешностью аппроксимации. Число s называется порядком аппроксимации или степенью разностного уравнения, а $r_{n+k}=(\rho_{n+k})/h$ – погрешностью дискретизации.

Метод является согласованным, если
$$
\max _{0 \leq n \leq N} \frac{r_{n+k}}{h_n} \rightarrow 0 \quad \text { при } h \rightarrow 0
$$
и имеет порядок согласованности $S$,
$$
\max _{0 \leq n \leq N} \frac{\| r_{n+k} \|}{O(h^i)} = O\left(h^i\right)
$$

---

Метод из класса $\sum_{i=0}^{n} \alpha_i y_{n+i}=h\sum_{i=0}^n \beta_i f(x_{n+i},y(x_{n+i}))$, $n=0,1,2,\ldots$ удовлетворяет корневую условность, если все корни характеристического полинома $\rho(\theta)$ лежат внутри единичной окружности или на самой окружности, причем те корни, которые лежат на единичной окружности, являются простыми.

Если метод согласован, то $\rho(\theta)$ обязательно имеет корень $\theta_1 = +1$.

Корни характеристического полинома классифицируются следующим образом:

$\theta_1 = +1$ - главный корень;

$|\theta| \leq 1$, $i=2,3,\ldots$, $k$- посторонние корни.

---

Метод удовлетворяющий корневому условию называют **нуль-устойчивым.**

**Согласованность** – определяет величину погрешности аппроксимации, **нуль-устойчивость** – определяет характер развития этой и других погрешностей в пределе при $h \rightarrow 0$, $Nh = x_k - x_0$.

Метод из класса
$\sum_{i=0}^k \alpha_i y_{n+i} = h \sum_{i=0}^{\infty} \beta_i f\left(x_{n+i}, y\left(x_{n+i}\right)\right)$, $n = 0,1,2,...$
сходится тогда и только тогда, когда он является согласованным и нуль-устойчивым.

---
**Устойчивость** численного метода - непрерывная зависимость численных результатов от входных данных и ограниченность погрешности при заданных пределах изменения параметров метода (шагов сетки, числа итераций и т.д.)

**Сходимость** численного метода - стремление численных результатов к точному решению, при стремлении параметров метода к определенным предельным значениям, например, шага сетки к 0 или количества итераций к бесконечности.''')
def q21_th(): 
    print('''
    Метод Милна относится к многошаговым методам и представляет один из методов прогноза и коррекции. Для решения дифференциального уравнения с использованием метода Милна необходимо начать с выбора начального условия и шага интегрирования. Решение производится в два этапа. Первый – прогнозирование значения функции, второй – коррекция полученного значения. Если полученное значение после коррекции существенно отличается от спрогнозированного, то проводят еще один этап коррекции. Если такая ситуация повторяется, коррекция проводится до того момента, пока значение не будет удовлетворять требуемому. Однако очень часто ограничиваются одним этапом коррекции.

Метод Милна не является «самодостаточным», для его применения требуется получить исходные данные с помощью какого – либо одношагового метода.

Обычно для получения исходных значений для применения метода Милна используют метод Рунге-Кутты. С его помощью находят исходные значения.

Алгоритм:

1) По предсказывающей формуле вычисляется грубое значение y на правом конце интервала: yk + 1: yk + 1 = yk – 3 + 4/3 · (2 · fk – fk – 1 + 2 · fk – 2) · Δt.

2) Рассчитывается производная в k + 1 точке: fk + 1 = f(t + Δt, yk + 1).

3) Снова рассчитывается yk + 1 по уточненной формуле, используя уже новое значение производной в точке k + 1: yk + 1 = yk – 1 + 1/3 · (fk + 1 + 4 · fk + fk – 1) · Δt.

4) Рассчитывается производная в k + 1 точке с учетом вновь вычисленного более точного значения yk + 1: fk + 1 = f(t + Δt, yk + 1). Здесь же производится подсчет итераций счетчиком i: i := i + 1.

5) Проверка точности: |yk + 1i-я итерация – yk + 1(i + 1)-я итерация| ≤ ε. Если условие выполнено, и точность ε достигнута, то переходим на следующий шаг 6, иначе осуществляется переход на шаг 3 и процесс уточнения повторяется с новыми значениями y и f, причем их старое значение берется с предыдущей итерации.

6) Подготовка к новому шагу: изменение счетчика времени t, изменение номера шага k:
t := t + Δt
k := k + 1.

7) Проверка окончания расчета: t ≤ T. Если условие выполняется, то расчет продолжается для следующей точки, и осуществляется переход на шаг 1, иначе — конец.''')
def q20_th(): 
    print('''
    Сравнивая явные и неявные методы Адамса, можно отметить следующее:
 1. Недостаток неявных методов состоит в необходимости на каждом шаге решать уравнение относительно неизвестной величины $у_{n+1}$.
 2. Некоторое преимущество неявных методов состоит в точности: при одной и той же шаговости к неявные методы имеют порядок сходимости к + 1, в отличие от явных, у которых по рядок сходимости к.
 3. Главное преимущество неявных методов состоит в возможности решать жесткие системы


Сравнивая метод Адамса с методом Рунге-Кутта той же точности, отмечаем его экономичность, поскольку он требует вычисления лишь одного значения правой части на каждом шаге (метод Рунге-Кутта – четырех). При этом, метод Адамса неудобен тем, что невозможно начать счет по одному лишь известному значению y. Расчет может быть начат лишь с узла x3.

Явный метод Адама: Использует предыдущие значения $y_n$, $y_{n-1}$, ... для аппроксимации следующего значения $y_{n+1}$. Формула для трехшагового метода Адамса-Баффорта:
$$ y_{n+1} = y_n + \frac{h}{12}(23 f(t_n, y_n) - 16 f(t_{n-1}, y_{n-1}) + 5 f(t_{n-2}, y_{n-2})) $$


Неявный метод Адама: Использует текущие и будущие значения для более точного результата. Формула для трехшагового метода Адамса-Мултона:
$$ y_{n+1} = y_n + \frac{h}{12}((5f(t_{n+1}, y_{n+1}) + 8f(t_n, y_n) - f(t_{n-1}, y_{n-1})))$$

---

Явные методы

Преимущества: Простота реализации и вычислительная эффективность.
Недостатки: Ограниченная стабильность, особенно для жестких систем.

Неявные методы

Преимущества: Более высокая стабильность, подходящая для жестких систем.
Недостатки: Более сложная реализация и необходимость решения нелинейных уравнений на каждом шаге.''')
    
    
    
def q19_th(): 
    print('''
    Классический **метод Рунге-Кутты 2-го порядка**, он же Метод Эйлера с
пересчетом, описывается следующим уравнением:

$y_i = y_{i-1} + h \cdot f(x_i, y_i)$

Схема является неявной, так как искомое значение $y_i$
входит в обе части
уравнения.
Затем вычисляют значение производной в точке $(x_i, y_i)$ и окончательно
полагают:

$y_i = y_{i-1} + h \cdot \cfrac{f(x_{i-1}, y_{i-1}) + f(x_i, y_i^*)}{2}$

то есть усредняют значения производных в начальной точке и в точке “грубого
приближения”. Окончательно запишем рекуррентную формулу метода РунгеКутты 2-го порядка в следующем виде:

$y_i = y_{i-1} + \frac{h}{2} \cdot (k_1 + k_2)$

где:

$k_1 = f(x_{i-1}, y_{i-1})$

$k_2 = f(x_{i-1} + h, y_{i-1} + h \cdot k_1)$

Метод имеет второй порядок точности: Локальная погрешность метода Рунге–Кутты 2–го порядка $e_2 = C∙h^3$, где C –
некоторая постоянная, и пропорциональна кубу шага интегрирования: при
уменьшении шага в 2 раза локальная погрешность уменьшится в 8 раз.


**Метод Рунге-Кутты 3-го порядка:**

$y_{n+1} = y_n + \cfrac{(k_1 + 4k_2 + k_3)}{6}$

$k_1 = h * f(x_n, y_n)$

$k_2 = h * f(x_n + \frac{h}{2}, y_n + \frac{k_1}{2})$

$k_3 = h * f(x_n + h, y_n - k_1 + 2k_2)$

**Метод Рунге-Кутты 4-го порядка:**

$y_{n+1} = y_n + \cfrac{(k_1 + 2(k_2 + k_3) + k_4)}{6}$

$k_1 = h * f(x_n, y_n)$

$k_2 = h * f(x_n + \frac{h}{2}, y_n + \frac{k_1}{2})$

$k_3 = h * f(x_n + \frac{h}{2}, y_n + \frac{k_2}{2})$

$k_4 = h * f(x_n + h, y_n + k_3)$

Локальная ошибка - $O(h^5)$

Глобальная ошибка - $O(h^4)$''')
def q18_th(): 
    print('''
    Рассмотрим еще одно семейство многошаговых методов, которые
используют неявные схемы, – метод прогноза и коррекции (они
называются также методами **предиктор-корректор**). Суть этих
методов состоит в следующем.
На каждом шаге вводятся два этапа, использующих многошаговые
методы:

1) с помощью явного метода (**предиктора**) по известным значениям
функции в предыдущих узлах находится начальное приближение
$𝑦_{𝑖+1} = 𝑦_{𝑖+1}^{(0)}$
в новом узле.

2) используя неявный метод (**корректор**), в результате итераций
находятся приближения $𝑦_{𝑖+1}^{(1)}, 𝑦_{𝑖+1}^{(2)}, ...$


К методам «предиктор-корректор» относится, например, метод Эйлера – Коши, где мы вычисляем

$y_{i+1}^{(0)} = y_i + h \cdot f(x_i, y_i)$

начальное приближение, с помощью явного метода – Эйлера (предиктор), затем

$y_{i+1}^{(1)} = y_i + h \cdot \cfrac{f(x_i, y_i) + f(x_{i+1}, y_{i+1}^{(0)})}{2}$

– следующее приближение значения функции $y_{i+1}$ в $x_{i+1}$-ой точке, $y_{i+1}^{(1)}$(корректор).


Один из вариантов метода прогноза и
коррекции может быть получен на основе
метода Адамса четвертого порядка:

на этапе предиктора
$y_{i+1} = y_i + \frac{h}{24}(55f_i - 59f_{i-1} + 37f_{i-2} - 9f_{i-3})$

на этапе корректора
$y_{i+1} = y_i + \frac{h}{24}(9f_{i+1} + 19f_i - 5f_{i-1} + f_{i-2})$

Явная схема используется на каждом шаге
один раз, а с помощью неявной схемы
строится итерационный процесс вычисления
$y_{i+1}$
, поскольку это значение входит в правую часть выражения $f_{i+1} = f(x_{i+1},
y_{i+1})$. Расчет по этому методу может быть начат только со значения y4
.
Необходимые при этом y1
, y2
, y3 находятся по методу Рунге-Кутта, y0
задается начальным условием.''')
    
    
def q17_th(): 
    print('''
    $\textbf{Метод Эйлера}$ — это один из самых простых методов численного решения обыкновенных дифференциальных уравнений (ОДУ). Он основан на аппроксимации решения с использованием касательной к графику функции и позволяет шаг за шагом приближённо вычислять значение функции.

**Формулировка метода**

Рассмотрим задачу Коши для ОДУ первого порядка:

$\frac{dy}{dx} = f(x,y), \space \space \space \space  y(x_0) = y_0$

Метод Эйлера позволяет найти приближённое значение y в следующей точке $x_{n+1} = x_n+h(h-шаг)$ по формуле:

$y_{n+1} = y_n+h \cdot f(x_n, y_n)$,

где $y_n$ - приближенное значение функции в точке $x_n$

Геометрическая интерпретация
Метод Эйлера можно рассматривать как последовательное построение касательных к кривой $y= y(x)$. На каждом шаге рассчитывается наклон касательной (то есть значение производной $f(x,y))$, и вдоль этой касательной проводится линейное приближение на длину шага $h$.

**Плюсы метода Эйлера**

1) $\it\text{Простота реализации}$:

Метод легко реализовать программно, он не требует сложных вычислений.

2) $\it\text{Интуитивная понятность}$:

Метод основан на простых геометрических и алгебраических принципах.


**Минусы метода Эйлера**

1) $\it\text{Низкая точность}$:

Ошибка метода Эйлера имеет порядок $O(h)$, что означает, что точность решения сильно зависит от величины шага $h$. Для достижения приемлемой точности шаг должен быть очень маленьким, что увеличивает количество вычислений.

2) $\it\text{Накопление ошибок}$:

Поскольку метод основан на последовательных шагах, ошибки на каждом шаге суммируются, что приводит к значительному отклонению от истинного решения.''')
def q16_th(): 
    print('''
    $\textbf{Метод центральной разности}$ — это численный метод для приближённого вычисления производной функции. Он используется, когда аналитическое нахождение производной либо невозможно, либо затруднено.

**Плюсы метода:**

1) $\it\text{Более высокая точность}$:

По сравнению с методами односторонних разностей (прямой и обратной), метод центральной разности обладает более высокой точностью, поскольку ошибка аппроксимации составляет $𝑂(h^2)$, тогда как в методах односторонних разностей —  $𝑂(h)$

2) $\it\text{Cимметричность}$:

Метод симметричен относительно точки
𝑥, что делает его более устойчивым и точным для гладких функций.






**Минусы метода:**

1) $\it\text{Невозможность вычисления на краях интервала}$:

Если требуется вычислить производную на границе заданного интервала, метод центральной разности использовать нельзя, поскольку он требует значений функции с обеих сторон от точки 𝑥.

2) $\it\text{Чувствительность к шагу ℎ}$:

Слишком маленький шаг может привести к накоплению ошибок округления, а слишком большой шаг уменьшает точность аппроксимации.''')
def q15_th(): 
    print('''
    **Локальные ошибки** - погрешности, образовавшиеся на каждом шаге (разница между точным и вычисленным значением на каждом шаге) = невязка метода

**Глобальные ошибки (накопленные)** - погрешности, образовавшиеся за $n$ шагов

Порядок глобальной погрешности относительно шага интегрирования на единицу ниже, чем порядок локальной погрешности. Таким образом, глобальная ошибка метода Эйлера есть  $O(h)$, т. е. данный метод имеет первый порядок. Иными словами, размер шага и ошибка для метода Эйлера связаны линейно. Практическим следствием этого факта является ожидание того, что при уменьшении приближенное решение будет все более точным и при стремлении к нулю будет стремиться к точному решению с линейной скоростью ; т.е. ожидаем, что при уменьшении шага вдвое ошибка уменьшится примерно в два раза.

Порядок численного метода для решения ОДУ определяется порядком его глобальной погрешности. Он может быть также опрделён, как количество вычислений значения производной $f(x, y)$ искомой ф-ии на каждом шаге. В соответствии с этим метод Эйлера является методом первого порядка.

для методов Рунге-Кутты глобальная ошибка — $O(h^p)$, где $p$ зависит от порядка метода (например, для метода Рунге-Кутты 4-го порядка — это $O(h^4))$''')
    
    
    
def q14_th(): 
    print('''
    Обыкновенные дифференциальные уравнения (оду) - ур-я, содержащие одну или несколько производных от искомой ф-и:

$F(x,y, y^,, y^{,,}, ..., y^{(n)}) = 0$

x - независимая переменная, y = y(x) - искомая ф-я

Наисвысший порядок производной n, входящей в предыдущее уравнение, называют порядком дифференциального ур-я

Рассмотрим с-му ОДУ первого порядка, записанную в виде:

$y^{'} (x) = f(x, y(x))$

Решение: любая ф-я y(x), которая удовлетворяет ур-ю. Решением ОДУ на интервале (a,b) называется ф-я $y = Φ(x)$, которая при её подстановке в исходное уравнение обращает его в тождество на (a, b)

Решение ОДУ в неявном виде $\Phi (x, y) = 0$ называется интегралом ОДУ

Существует мн-во возможных решенийю Для одного уникального решения необходимо указать независимые условия (для с-мы размером n)

Например, когда n условий заданы для одной точки.

$y(0) = y_0$

Это задача Коши (задача с начальными условиями). Либо дифференциальная задача''')
    
    
def q13_th(): 
    print('''
    **Определение разреженных матриц**

* Разреженные матрицы – это матрицы, такие что количество ненулевых элементов в них существенно меньше общего числа элементов в матрице.

* Из-за этого вы можете выполнять базовые операции линейной алгебры (прежде всего решать линейные системы) гораздо быстрее по сравнению с использованием плотных матриц.


**Приложения разреженных матриц**
Разреженные матрицы возникают в следующих областях:

* математическое моделирование и решение уравнений в частных производных
* обработка графов(графы представляют в виде матриц смежности, которые чаще всего разрежены
), например анализ социальных сетей
* рекомендательные системы
* в целом там, где отношения между объектами "разрежены"

**Хранение разреженных матриц**

1. $\it\text{COO (координатный формат)}$
* Простейший формат хранения разреженной матрицы – координатный.
* В этом формате разреженная матрица – это набор индексов и значений в этих индексах -> $i, j, val$
где $i, j$ массивы индексов, $val$ массив элементов матрицы.
* Таким образом, нам нужно хранить $ 3\cdot nnz$ элементов, где $nnz$ обозначает число ненулевых элементов в матрице.

  $\it{Недостатки}:$
  * Он неоптимален по памяти
  * Он неоптимален для умножения матрицы на вектор
  * Он неоптимален для удаления элемента
  Первые два недостатка решены в формате CSR.

2. $\it\text{CSR - Compressed sparse row}$

  В формате CSR матрица хранится также с помощью трёх массивов, но других: $ia, ja, sa$, где:
  * $ia$ (начало строк) массив целых чисел длины
  * $ja$ (индексы столбцов) массив целых чисел длины $nnz$
  * sa (элементы матрицы) массив действительных чисел длины $nnz$

  Всего необходимо хранить $2 \cdot nnz + n + 1$
 элементов.

3. $\it\text{LIL (список списков)}$

4. $\it\text{CSC (compressed sparse column)}$
5. $\it\text{блочные варианты}$

В scipy представлены конструкторы для каждого из этих форматов, например

scipy.sparse.lil_matrix(A).

**Прямые методы для решения больших разреженных систем:**
(прямые методы - численные методы, которые находят точное решение систем линейных уравнений вида Ax=b)
* LU разложение (Для разреженных матриц часто используют модифицированные алгоритмы LU-разложения, которые минимизируют заполнение(добавление новых ненулевых элементов в ходе вычислений) с помощью перестановок строк и столбцов)
* Различные методы переупорядочивания для минимизации заполнения факторов''')
    
    
    
def q12_th(): 
    print('''
    **Метод разделяй и властвуй** вычисления собственных значений и векторов трёхдиагональной матрицы - наиболее быстрый из существующих методов вычисления всех собственных значений и собственных векторов трехдиагональной матрицы, начиная с порядка n, который примерно равен 26. (Точное значение этого порогового порядка в конкретном случае зависит от компьютера.)
Пусть у нас есть трёхдиагональная матрица и мы разделили её на блоки:

   $$
      T = \begin{pmatrix}
      T_1 & B  \\
      B^T & T_2
      \end{pmatrix}
  $$

Можем записать матрицу $T$ в виде

   $$
      T = \begin{pmatrix}
      T_1 & B  \\
      B^T & T_2
      \end{pmatrix} + \rho vv^*
  $$

где $v^*$ – эрмитово-сопряжённый вектор, $v = (0, ..., 0, 1, 1, 0, ..., 0)^T$

Пусть мы уже разложили матрицы $T_1$ и $T_2$:

$T_1 = Q_1 Ʌ_1 Q^*_1$

$T_2 = Q_2 Ʌ_2 Q^*_2$


Тогда (проверьте!),

   $$
       \begin{pmatrix}
      Q_1^* & 0  \\
      0 & Q_2^*
      \end{pmatrix} T    
      \begin{pmatrix}
      Q_1^* & 0  \\
      0 & Q_2^*
      \end{pmatrix} = D + \rho uu^*
  $$  
  
  $$
      D = \begin{pmatrix}
      Ʌ_1 & 0  \\
      0 & Ʌ_2
      \end{pmatrix}
  $$

то есть мы свели задачу к задаче вычисления собственных значений у матрицы вида "диагональная матрица плюс матрица малого ранга"

**Матрица вида диагональная матрица плюс матрица малого ранга**

Собственные значения матрицы вида $D + \rho uu^*$ вычислить не просто.
Характеристический многочлен имеет вид

$det(D + \rho uu^* - \lambda I) = det(D - \lambda I) det (I + \rho (D - \lambda I)^{-1}uu^*) = 0$

Тогда:

$det(I + \rho (D - \lambda I)^{-1}uu^*) = 1 + \rho \sum_{i=1}^n \frac{|u_i|^2}{d_i - \lambda} = 0$

**Характеристическое уравнение**

$1 + \rho \sum_{i=1}^n \frac{|u_i|^2}{d_i - \lambda} = 0$''')
    
def q11_th(): 
    print('''
    **Сходимость QR алгоритма**

Если у нас есть разложение вида:  
$$A = X \Lambda X^{-1}, \quad A = \begin{bmatrix} A_{11} & A_{12} \\ A_{21} & A_{22} \end{bmatrix} $$  

и  
$$
\Lambda = \begin{bmatrix} \Lambda_1 & 0 \\ 0 & \Lambda_2 \end{bmatrix},  
\quad \lambda(\Lambda_1) = \{\lambda_1, \dots, \lambda_m\},  
\quad \lambda(\Lambda_2) = \{\lambda_{m+1}, \dots, \lambda_r\},
$$

а также есть зазор между собственными значениями в матрицах $ \Lambda_1 $ и  $ \Lambda_2 $:  
$$
|\lambda_1| \geq \dots \geq |\lambda_m| > |\lambda_{m+1}| \geq \dots \geq |\lambda_r| > 0,
$$

тогда блок $ A_{21}^{(k)} $ матрицы $ A_k $ сходится к нулевому в процессе работы QR алгоритма со скоростью  
$$
\|A_{21}^{(k)}\| \leq Cq^k, \quad q = \left| \frac{\lambda_{m+1}}{\lambda_m} \right|,
$$
где $ m $ — размер матрицы $ \Lambda_1 $.  

Таким образом, нам нужно увеличить зазор между $ \Lambda_1 $ и $ \Lambda_2 $. Это можно сделать с помощью **QR алгоритма со сдвигами**.

QR-алгоритм со сдвигами – это модификация базового QR-алгоритма, которая ускоряет его сходимость. В ней вводится сдвиг $s_k$
 , чтобы быстрее выделить собственные значения матрицы.

**QR алгоритм со сдвигами**

$A_k - s_kI = Q_kR_k$

$A_{k+1} = R_kQ_k+s_kI$

Сходимость такого алгоритма линейная с фактором $$\big|\frac{\lambda_{m+1} - s_k}{\lambda_m - s_k}\big|$$

где $\lambda_m$– $m$-ое большее по модулю собственное значение. Если сдвиг близок к собственному вектору, сходимость более быстрая - становится почти квадратичной

* Существуют различные стратегии выбора сдвигов.

* Использование сдвигов – это общий подход к ускорению сходимости итерационных методов вычисления собственных значений.''')
    
    
def q10_th(): 
    print('''
    **Спектр** — это спектр линейного оператора, который представляет собой множество собственных значений оператора.

**Псевдоспектр** матрицы $A$ — это обобщение спектра, которое учитывает влияние малых возмущений на собственные значения. Он определяется как множество комплексных чисел $\lambda$, для которых матрица $(A−\lambda I)$ становится почти вырожденной, то есть:
$$||(A−λI)^{-1}||\ge \frac{1}{\epsilon}$$

для некоторого малого
$\epsilon>0$, где $||\cdot||$ — операторная норма.

* Для динамических систем с матрицей $A$, спектр может много сообщить о поведении системы (например, о её устойчивости)

* Однако для не нормальных матриц, спектр может быть неустойчивым относительно малых возмущений матрицы

* Для измерения подобных возмущений было разработана концепция псевдоспектра.

Рассмотрим объединение всех возможных собственных значений для всевозможных возмущений матрицы $A$.

$$\Lambda_{\epsilon}(A) = \{ \lambda \in \mathbb{C}: \exists E, x \ne 0: (A + E) x = \lambda x, \quad \Vert E \Vert_2 \leq \epsilon. \}$$

Для малых $E$ и нормальных $A$ это круги вокруг собственных значений, для не нормальных матриц, структура может сильно отличаться.''')

def q9_th(): 
    print('''
    **Определение.** Нормальная матрица — это квадратная матрица $A$, которая коммутирует со своей эрмитово-сопряжённой матрицей $
A^*$, то есть матрица $A$ нормальная, если
$$ AA^* = A^* A. $$

**Нормальные матрицы**

**Теорема**: $A$ – **нормальная матрица**, тогда и только тогда, когда существует такая унитарная матрица $U$, что $$A = U \Lambda U^*$$, где $\Lambda$-диагональная матрица, содержащая собственные значения матрицы $A$ на диагонали.

**Важное следствие**
Любая нормальная матрица – **унитарно диагонализуема**. Это означает, что она может быть приведена к диагональному виду с помощью унитарной матрицы $U$. Другими словами, каждая нормальная матрица имеет ортогональный базис из собственных векторов.

**Эрмитова** (или самосопряжённая) ма́трица — квадратная матрица, элементы которой являются комплексными числами, и которая, будучи транспонирована, равна комплексно сопряжённой:
$A^T = \overline{A}$. То есть для любого столбца $i$ и строки $j$ справедливо равенство $a_{ij} = \overline{a_{ji}}$ где $\overline{a}$— комплексно сопряжённое число к $a$, или $A = (\overline{A})^T = A^*$,
где * — эрмитово сопряжение. То есть эрмитова матрица — это квадратная матрица, которая равна своей эрмитово-сопряжённой матрице.

**Эрмитово - сопряженная матрица(сопряженно-транспонированная)** - матрица $A^*$ с комплексными элементами, полученная из исходной матрицы $A$ транспонированием и заменой каждого эелемента комплексно-сопряженным ему.

Пример:

$$\begin{equation*}
A =
\begin{pmatrix}
3 & 2+i\\
2 - i & 1\\
\end{pmatrix}
\end{equation*}$$

$$\begin{equation*}
A^* =
\begin{pmatrix}
3 & 2+2i\\
2-i & 1
\\
\end{pmatrix}
\end{equation*}$$

**Унитарно - диагонализуемые матрицы**: матрица $A$ унитарно - диагонализуемая, если сущетвует унитарная матрица $U$ такая, что $U^*AU$ - диагональная матрица.

(Унитарная матрица - квадратная матрица с комплексными элементами, результат умножения которой на эрмитово - сопряженную равен единичной матрице $U^*U = UU^* = I$. Иначе говоря, матрица унитарна тогда и т.т., когда существует обратная к ней матрица, удовлетворяющая условию $U^{-1} = U^*$)

**Верхне-гессенбергова форма матрицы**
Матрица $A$ имеет верхне-гессенбергову форму, если $$a_{ij} = 0, при \space i\geq j+2.$$

$$H =
\begin{bmatrix}
* & * & * & * & * \\
* & * & * & * & * \\
0 & * & * & * & * \\  
0 & 0 & * & * & * \\
0 & 0 & 0 & * & *  
\end{bmatrix}
$$


**Приведение произвольной матрицы к верхне-гессенберговой форме**

С помощью отражений Хаусхолдера можно привести любую матрицу к верхне-гессенберговой форме:
$$U^*AU = H$$

* Единственное отличие от вычисления разложения Шура заключается в занулении последних $n-2, n-3,...$
 элементов в первом, втором и так далее столбцах

* Сложность такого приведения $O(n^3)$ операций

* Если матрица приведена к верхне-гессенберговой форме, то одна итерация QR алгоритма имеет сложность
$O(n^2)$ операций (например, используя вращения Гивенса)

* Также верхне-гессенбергова форма матрицы сохраняется после выполнения одной итерации QR алгоритма.


вся теория

**Определение.** Нормальная матрица — это квадратная матрица $A$, которая коммутирует со своей эрмитово-сопряжённой матрицей $
A^*$, то есть матрица $A$ нормальная, если
$$ AA^* = A^* A. $$

**Нормальные матрицы**

**Теорема**: $A$ – **нормальная матрица**, тогда и только тогда, когда существует такая унитарная матрица $U$, что $$A = U \Lambda U^*$$, где $\Lambda$-диагональная матрица, содержащая собственные значения матрицы $A$ на диагонали.

**Важное следствие**
Любая нормальная матрица – **унитарно диагонализуема**. Это означает, что она может быть приведена к диагональному виду с помощью унитарной матрицы $U$. Другими словами, каждая нормальная матрица имеет ортогональный базис из собственных векторов.

-----
**Эрмитова** (или самосопряжённая) ма́трица — квадратная матрица, элементы которой являются комплексными числами, и которая, будучи транспонирована, равна комплексно сопряжённой:
$A^T = \overline{A}$. То есть для любого столбца $i$ и строки $j$ справедливо равенство $a_{ij} = \overline{a_{ji}}$ где $\overline{a}$— комплексно сопряжённое число к $a$, или $A = (\overline{A})^T = A^*$,
где * — эрмитово сопряжение. То есть эрмитова матрица — это квадратная матрица, которая равна своей эрмитово-сопряжённой матрице.

**Эрмитово - сопряженная матрица(сопряженно-транспонированная)** - матрица $A^*$ с комплексными элементами, полученная из исходной матрицы $A$ транспонированием и заменой каждого эелемента комплексно-сопряженным ему.

Пример:

$$\begin{equation*}
A =
\begin{pmatrix}
3 & 2+i\\
2 - i & 1\\
\end{pmatrix}
\end{equation*}$$

$$\begin{equation*}
A^* =
\begin{pmatrix}
3 & 2+2i\\
2-i & 1
\\
\end{pmatrix}
\end{equation*}$$

-----
**Унитарно - диагонализуемые матрицы**: матрица $A$ унитарно - диагонализуемая, если сущетвует унитарная матрица $U$ такая, что $U^*AU$ - диагональная матрица.

(Унитарная матрица - квадратная матрица с комплексными элементами, результат умножения которой на эрмитово - сопряженную равен единичной матрице $U^*U = UU^* = I$. Иначе говоря, матрица унитарна тогда и т.т., когда существует обратная к ней матрица, удовлетворяющая условию $U^{-1} = U^*$)

----
**Верхне-гессенбергова форма матрицы**
Матрица $A$ имеет верхне-гессенбергову форму, если $$a_{ij} = 0, при \space i\geq j+2.$$

$$H =
\begin{bmatrix}
* & * & * & * & * \\
* & * & * & * & * \\
0 & * & * & * & * \\  
0 & 0 & * & * & * \\
0 & 0 & 0 & * & *  
\end{bmatrix}
$$


**Приведение произвольной матрицы к верхне-гессенберговой форме**

С помощью отражений Хаусхолдера можно привести любую матрицу к верхне-гессенберговой форме:
$$U^*AU = H$$

* Единственное отличие от вычисления разложения Шура заключается в занулении последних $n-2, n-3,...$
 элементов в первом, втором и так далее столбцах

* Сложность такого приведения $O(n^3)$ операций

* Если матрица приведена к верхне-гессенберговой форме, то одна итерация QR алгоритма имеет сложность
$O(n^2)$ операций (например, используя вращения Гивенса)

* Также верхне-гессенбергова форма матрицы сохраняется после выполнения одной итерации QR алгоритма.''')
    
    
def q8_th(): 
    print('''
    $\LargeТеорема\spaceШура$


**Теорема:** Пусть матрица $A \in \mathbb{C}^{n \times n}$. ТОгда существует матрица $U$ унитарная и матрица $T$ верхнетреугольная такие, что $$T = U^*AU$$

$A = UTU^* - $разложение Шура

**Набросок доказательства**.
1. Каждая матрица имеет как минимум один ненулевой собственный вектор (для корня характеристического многочлена матрица $(A-\lambda I)$ вырождена и имеет нетривиальное ядро). Пусть

$$Av_1 = \lambda_1 v_1, \quad \Vert v_1 \Vert_2 = 1.$$

2. Пусть $U_1 = [v_1,v_2,\dots,v_n]$, где $v_2,\dots, v_n$ любые векторы ортогональные $v_1$. Тогда
  
  $$
      U^*_1 A U_1 = \begin{pmatrix}
      \lambda_1 & *  \\
      0 & A_2
      \end{pmatrix},
  $$
  
  где $A_2$ матрица размера $(n-1) \times (n-1)$. Это называется **блочнотреугольной формой**. Теперь мы можем проделать аналогичную процедуру для матрицы $A_2$ и так далее.  
  
  
**Замечание**: Поскольку в доказательстве необходимы собственные векторы, оно не является практичным алгоритмом.

**Приложение теоремы Шура**

Важное приложение теоремы Шура связано с так называемыми **нормальными матрицами**.  

**Определение.** Матрица $A$ называется **нормальной матрицей**, если  

$$ AA^* = A^* A. $$

**Q:** Какие примеры нормальных матриц вы можете привести?

Примеры: эрмитовы матрицы, унитарные матрицы.

$\LargeРазложение\spaceШура$
- Нужно найти унитарную матрицу $U$ и верхнетреугольную матрицу $T$, такие что для данной матрице $A$ выполнено

$$ A = U T U^*. $$

- <font color='red'> **Не путайте** QR алгоритм и QR разложение! </font>

- QR разложение – это представление матрицы в виде произведения двух матриц, а QR алгоритм использует QR разложение для вычисления разложения Шура.

Зачем нужно разложение Шура?

- Численные методы:
Разложение Шура часто используется как основа для численного поиска собственных значений. В частности, QR-алгоритм сводится к нахождению разложения Шура.

- Контроль собственных значений:
Так как разложение Шура даёт матрицу $T$, где на диагонали стоят собственные значения, оно полезно для анализа спектра матрицы.

**Путь к QR алгоритму**

Рассмотрим выражение

$$A = Q T Q^*,$$

и перепишем его в виде

$$
   Q T = A Q.
$$

Слева замечаем QR разложение матрицы $AQ$.

Используем его чтобы записать одну итерацию метода неподвижной точки для разложения Шура.

**Вывод QR алгоритма из уравнения неподвижной точки**

Запишем следующий итерационный процесс

$$
    Q_{k+1} R_{k+1} = A Q_k, \quad Q_{k+1}^* A = R_{k+1} Q^*_k
$$

Введём новую матрицу

$$A_k = Q^* _k A Q_k = Q^*_k Q_{k+1} R_{k+1} = \widehat{Q}_k R_{k+1}$$

тогда аппроксимация для $A_{k+1}$ имеет вид

$$A_{k+1} = Q^*_{k+1} A Q_{k+1} = ( Q_{k+1}^* A = R_{k+1} Q^*_k)  = R_{k+1} \widehat{Q}_k.$$

Итак, мы получили стандартную форму записи QR алгоритма.

Финальные формулы обычно записывают в **QRRQ**-форме:

1. Инициализируем $A_0 = A$.
2. Вычислим QR разложение матрицы $A_k$: $A_k = Q_k R_k$.
3. Обновим аппроксимацию $A_{k+1} = R_k Q_k$.

Продолжаем итерации пока $A_k$ не станет достаточно треугольной (например, норма подматрицы под главной диагональю не станет достаточно мала).

**Что известно о сходимости и сложности**

**Утверждение**

Матрицы $A_k$ унитарно подобны матрице $A$

$$A_k = Q^*_{k-1} A_{k-1} Q_{k-1} = (Q_{k-1} \ldots Q_1)^* A (Q_{k-1} \ldots Q_1)$$

а произведение унитарных матриц – унитарная матрица.

Сложность одной итерации $\mathscr{O}(n^3)$, если используется QR разложение для общего случая.

Мы ожидаем, что $A_k$ будет **очень близка к треугольной матрице** для достаточно большого $k$.''')
    
    
def q7_th(): 
    print('''
    $\textbf{Круги Гершгорина}$

Есть интересная теорема, которая часто помогает локализовать собственные значения.
Она называется $\it\text{теоремой Гершгорина}$.

Она утверждает, что все собственные значения $\lambda_i, i = \overline{1,n}$ находятся внутри объединения кругов Гершгорина $C_i$, где $C_i$– окружность на комплексной плоскости с центром в $a_{ii}$ и радиусом $r_i = \sum_{j \neq i} |a_{ij}|$


Более того, если круги не пересекаются, то они содержат по одному собственному значению внутри каждого круга.


**Доказательство**(на всякий случай)

Сначала покажем, что если матрица $A$ обладает строгим диагональным преобладанием, то есть $$|a_{ii}| > \sum_{j \neq i} |a_{ij}|,$$

тогда такая матрица невырождена.


Разделим диагональную и недиагональную часть и получим $$A = D+S = D(I+D^{-1}S),$$

где $||D^{-1}S||_1 < 1$. Поэтому, в силу теоремы о ряде Неймана, матрица $I + D^{-1}S$ обратима и, следовательно, матрица $A$ также обратима.

Теперь докажем утверждение теоремы от противного:

* если любое из собственных чисел лежит вне всех кругов, то матрица $(A - \lambda I)$ обладает свойством строгого диагонального преобладания
* поэтому она обратима
* это означает, что если $(A - \lambda I)x = 0$, то $x = 0$.''')
    
    
def q6_th():
    print('''
    $\it\textbf{Степенной метод}$

* Часто в вычислительной практике требуется найти не весь спектр, а только некоторую его часть, например самое большое или самое маленькое собственые значения.
* Также отметим, что для Эрмитовых матриц $(A = A^*)$
 собственные значения всегда действительны.

* Степенной метод – простейший метод вычисления $\it\text{максимального по модулю}$ собственного значения. Это также первый пример итерационного метода и Крыловского метода.

**Что необходимо помнить о степенном методе**

* Степенной метод даёт оценку для максимального по модулю собственного числа или спектрального радиуса матрицы
* Одна итерация требует одного умножения матрицы на вектор. Если можно умножить вектор на матрицу зa $O(n)$(например, она разреженная), тогда степенной метод можно использовать для больших $n$
* Сходимость может быть медленной
* Для грубой оценки максимального по модулю собственного значения и соответствующего вектора достаточно небольшого числа итераций

**Степенной метод: вид**

Задача на собственые значения $$Ax = \lambda x, ||x||_2 = 1 \text{(для устройчивости)}$$

может быть записана как итерации с неподвижной точкой, которые называются $\it\text{степенным методом}$ и дают максимальное по модулю собственное значение матрицы $A$.

Степенной метод имеет вид
$$x_{k+1} = Ax_k, x_{k+1} := \frac{x_{k+1}}{||x_{k+1}||_2}$$
и $x_{k+1} → v_1$, где $Av_1 = \lambda_1v_1 $ и $\lambda_1$ максимальное по модулю собственное значение, и $v_1$ – соответствующий собственный вектор.

На $(k+1)$-ой итерации приближение для $\lambda_1$ может быть найдено следующим образом $$\lambda^{k+1} = (Ax_{k+1}, x_{k+1})$$

Заметим, что $\lambda^{(k+1)}$ не требуется для $(k+2)$-ой итерации, но может быть полезно для оценки ошибки на каждой итерации: $||Ax_{k+1} - \lambda^{(k+1)}x_{k+1}||$
.

Метод сходится со скоростью геометричекой прогрессии, с константой $q = |\frac{\lambda_2}{\lambda_1}| < 1$, где $\lambda_1 > \lambda_2 \geq ... \geq \lambda_n$
. Это означает, что сходимость может быть сколь угодно медленной при близких значениях у $\lambda_1$ и $\lambda_2$.

**Общая сложность степенного метода**

Пусть $k$ — число итераций, необходимых для достижения заданной точности $ε$. Тогда общая сложность метода будет равна:
$O(k⋅n^2)$''')
    
def q5_th():
    print('''
    $\LargeРазложение\spaceШура$
- Нужно найти унитарную матрицу $U$ и верхнетреугольную матрицу $T$, такие что для данной матрице $A$ выполнено

$$ A = U T U^*. $$
  * Собственные значения матрицы $A$ находятся на диагонали матрицы $T$.

 **Не путайте** QR алгоритм и QR разложение!

- QR разложение – это представление матрицы в виде произведения двух матриц, а QR алгоритм использует QR разложение для вычисления разложения Шура.

**Путь к QR алгоритму**

Рассмотрим выражение

$$A = Q T Q^*,$$

и перепишем его в виде

$$
   Q T = A Q.
$$

Слева замечаем QR разложение матрицы $AQ$.

Используем его чтобы записать одну итерацию метода неподвижной точки для разложения Шура.

**Вывод QR алгоритма из уравнения неподвижной точки**

Запишем следующий итерационный процесс

$$
    Q_{k+1} R_{k+1} = A Q_k, \quad Q_{k+1}^* A = R_{k+1} Q^*_k
$$

Введём новую матрицу

$$A_k = Q^* _k A Q_k = Q^*_k Q_{k+1} R_{k+1} = \widehat{Q}_k R_{k+1}$$

тогда аппроксимация для $A_{k+1}$ имеет вид

$$A_{k+1} = Q^*_{k+1} A Q_{k+1} = ( Q_{k+1}^* A = R_{k+1} Q^*_k)  = R_{k+1} \widehat{Q}_k.$$

Итак, мы получили стандартную форму записи QR алгоритма.

Финальные формулы обычно записывают в **QRRQ**-форме:

1. Инициализируем $A_0 = A$.
2. Вычислим QR разложение матрицы $A_k$: $A_k = Q_k R_k$.
3. Обновим аппроксимацию $A_{k+1} = R_k Q_k$.

Продолжаем итерации пока $A_k$ не станет достаточно треугольной (например, норма подматрицы под главной диагональю не станет достаточно мала).

**Что известно о сходимости и сложности**

**Утверждение**

Матрицы $A_k$ унитарно подобны матрице $A$

$$A_k = Q^*_{k-1} A_{k-1} Q_{k-1} = (Q_{k-1} \ldots Q_1)^* A (Q_{k-1} \ldots Q_1)$$

а произведение унитарных матриц – унитарная матрица.

Сложность одной итерации $\mathscr{O}(n^3)$, если используется QR разложение для общего случая.

Мы ожидаем, что $A_k$ будет **очень близка к треугольной матрице** для достаточно большого $k$.

**Сходимость и сложность QR алгоритма**

- QR алгоритм сходится от первого диагонального элемента к последнему.

- По крайней мере 2-3 итерации необходимо для определения каждого диагонального элемента матрицы $T$.

- Каждый шаг состоит в вычислении QR разложения и одного произведения двух матриц, в результате имеем сложность $\mathscr{O}(n^3)$.

**Q**: означает ли это итоговую сложность $\mathscr{O}(n^4)$?

**A**: к счастью, нет!

- Мы можем ускорить QR алгоритм, используя сдвиги, поскольку матрица $A_k - \lambda I$ имеет те же векторы Шура (столбцы матрицы $U$).''')
    
def q4_th():
    print('''
    Что такое собственный вектор?

**Определение**. Вектор $x \neq 0$ называется собственным для квадратной матрицы A, если найдётся такое число $\lambda$, что $$Ax = \lambda x$$


Число $\lambda$ называется $\it{собственным}$ значением.

Так как матрица $A - \lambda I$ должна иметь нетривиальное ядро (что такое ядро?), собственные значения являются корнями характеристического полинома $$det(A - \lambda I) = 0$$

**Важность**

$\it\text{Собственные значения – это частоты выбраций}$

Обычно вычисление собственных значений и собственных векторов необходимо для изучения:

* вибраций в механических структурах
* снижения сложности моделей сложных систем

**Для чего используют:**

1. Упрощение сложных преобразований
- Собственные векторы и собственные значения помогают разложить сложные преобразования на простые части. Например, поворот, масштабирование или сжатие в каком-то направлении проще понять, если выделить направления (собственные векторы), которые остаются неизменными.

2. Диагонализация матриц
- Собственные векторы и значения используются для представления матрицы в более удобной форме — диагональной. Это важно, потому что:

  - Вычисления с диагональными матрицами (например, возведение в степень) намного проще.
  - Это позволяет изучать матрицу с минимальными усилиями.

3. Машинное обучение и анализ данных

- PCA (метод главных компонент): Собственные векторы помогают найти главные направления в данных, чтобы снизить размерность и оставить только важные признаки.
- Кластеризация: Собственные значения используются в алгоритмах, таких как спектральная кластеризация.

4. Дифференциальные уравнения

- Собственные значения и векторы упрощают решение линейных дифференциальных уравнений, которые описывают многие явления в природе и технике.

**Google PageRank**

Одна из самых известных задач, сводящихся к вычислению собственного вектора, – это задача вычисления Google PageRank.

* Задача состои в ранжировании веб-страницы: какие из них являются важными, а какие нет
* В интернете страницы ссылаются друг на друга
* PageRank определяется рекурсивно.

  Обозначим $p_i$ за важность $i$-ой страницы. Тогда определим эту важность как усреднённую важность всех страниц, которые ссылаются на данную страницу. Это определение приводит к следующей линейной системе $$p_i = \sum_{j \in N(i)}\frac{p_j}{L(j)},$$



  где

  * $L(j)$ – число исходящих ссылок с $j$-ой страницы,
  * $N(i)$– число соседей $i$-ой страницы.

  Это может быть записано следующим образом $$p = Gp,   G_{ij} = \frac{1}{L(j)}$$

  

  или как задача на собственные значения $$Gp = 1p$$


  то есть мы уже знаем, что у матрицы $G$ есть собственное значение равное $1$. Заметим, что $G$ – левостохастичная матрица, то есть сумма в каждом столбце равна $1$.''')
    
def q3_th():
    print('''
    Алгоритм Штрассена — это эффективный алгоритм умножения квадратных матриц, снижающий сложность с $O(n^3)$ до $O(n^{log_27}) \approx O(n^{2.81})$. В стандартном методе умножения матриц используется 8 умножений подматриц, что приводит к сложности  $O(n^3)$. Алгоритм Штрассена заменяет 8 умножений на 7,поэтому сложность становится равной  $O(n^{log_27})$



Метод Штрассена становится быстрее наивного алгоритма, если

$$2n^3>7n^{log_27},$$ $$n>667$$

классическое понятие сходимости, как его применяют, например, к итерационным методам или методам численного интегрирования, напрямую нельзя применить к методу Штрассена, поскольку это не итерационный метод, а детерминированный алгоритм, который выполняет конечное число операций и всегда возвращает определённый результат.

Почему классическое понятие сходимости неприменимо?
* Отсутствие итеративности
  Сходимость обычно анализируют в контексте методов, которые последовательно приближаются к решению через итерации. В методе Штрассена нет итераций — он разово применяет набор рекурсивных операций для вычисления произведения матриц, поэтому понятие «приближения к решению» здесь неприменимо.

* Детерминированный результат
  Алгоритм Штрассена всегда возвращает точное произведение матриц (при отсутствии ошибок округления). В отличие от итерационных методов, он не генерирует последовательность приближений, которая может стремиться к точному решению.


Очевидный способ вычисления правой стороны — просто сделать 8 умножений и 4 сложения. Но представьте, что умножения намного дороже сложений, поэтому мы хотим уменьшить количество умножений, если это вообще возможно. Штрассен использует трюк, чтобы вычислить правую сторону с одним умножением меньше и намного большим количеством сложений (и нескольких вычитаний).

Вот 7 умножений (пока это просто хитрые умножения, тут можно не искать логику):

$
M1 = (A + D) * (E + H) = AE + AH + DE + DH \\
M2 = (C + D) * E = CE + DE \\
M3 = A * (F - H) = AF - AH \\
M4 = D * (G - E) = DG - DE \\
M5 = (A + B) * H = AH + BH \\
M6 = (C - A) * (E + F) = CE + CF - AE - AF \\
M7 = (B - D) * (G + H) = BG + BH - DG - DH \\
$


Теперь сделаем несколько простых сложений и умножений.

Для AE+BG:
1. Итак, чтобы вычислить AE+BG, начнем с M1+M7 (что дает нам члены AE и BG)
$$M1 + M7 = (AE + AH + DE + DH) + (BG + BH - DG - DH)$$
$$M1 + M7 = AE + AH + DE + BG + BH - DG$$
$$M1 + M7 = AE + BG + AH + DE  + BH - DG$$
$$M1 + M7 = (AE + BG) + (AH + DE  + BH - DG)$$
2. затем прибавим/вычтем некоторые другие M, пока AE+BG не останется всем.
$$M1 + M7 + M4 = (AE + BG) + (AH + DE  + BH - DG) + (DG - DE)$$
$$M1 + M7 + M4 = (AE + BG) + (AH + BH)$$
$$M1 + M7 + M4 - M5 = (AE + BG) + (AH + BH) - (AH + BH)$$
$$M1 + M7 + M4 - M5 = (AE + BG)$$
Чудесным образом M выбираются так, что $M1+M7+M4-M5$ работает. То же самое с другими тремя требуемыми результатами.

Для AF+BH:
$$M3 + M5 = (AF - AH) + (AH + BH)$$
$$M3 + M5 = AF + BH - AH + AH$$
$$M3 + M5 = AF + BH$$

Для CE+DG:
$$M2 + M4 = (CE + DE) + (DG - DE)$$
$$M2 + M4 = CE + DG + DE - DE$$
$$M2 + M4 = CE + DG$$

Для CF+DH:
$$M1 - M2 = (AE + AH + DE + DH) - (CE + DE)$$
$$M1 - M2 = AE + AH + DE + DH - CE - DE$$
$$M1 - M2 = AE + AH + DH - CE + DE - DE$$
$$M1 - M2 = AE + AH + DH - CE$$

$$M1 - M2 + M3 = (AE + AH + DH - CE) + (AF - AH)$$
$$M1 - M2 + M3 = AE + AH + DH - CE + AF - AH$$
$$M1 - M2 + M3 = AE + DH - CE + AF + AH - AH$$
$$M1 - M2 + M3 = AE + DH - CE + AF$$

$$M1 - M2 + M3 + M6 = (AE + DH - CE + AF) + (CE + CF - AE - AF)$$
$$M1 - M2 + M3 + M6 = AE + DH - CE + AF + CE + CF - AE - AF$$
$$M1 - M2 + M3 + M6 = DH + CF + AE - AE - CE + CE + AF - AF$$
$$M1 - M2 + M3 + M6 = DH + CF$$

Теперь просто надо понять, что это работает не только для матриц 2x2, но и для любых (четных) матриц. При этом мы рекурсивно уменьшаем каждую матрицу.
''')

def q1_th():
    print('''**Определение**. Произведение матрицы $A$ размера $n×k$ и матрицы $B$ размера $k×m$– это матрица $C$ размера $n×m$ такая что её элементы записываются как $$c_{ij}=∑_{s=1}^{k}a_{is}b_{sj},i=1,…,n,j=1,…,m$$

Для $m=k=n$ сложность наивного алгоритма составляет $2n^3−n^2=O(n^3)$:

Почему рукописная(наивная) реализация такая медленная?

1) не используется параллелилизм

2) не используются преимущества быстрой памяти, в целом архитектуры памяти

**Определение**. Произведение матрицы $A$ размера $n×k$ и вектора $B$ размера $1×k$– это вектор $C$ длины $n$, такой, что его элементы записываются как $$c_{i}=∑_{j=1}^{k}a_{ij}b_{j},i=1,…,n$$''')
    
def q1():
    print('''def matmul(a, b): #наивное перемножение матриц
        n = a.shape[0]
        k = a.shape[1]
        m = b.shape[1]
        c = np.zeros((n, m))
        for i in range(n):
            for j in range(m):
                for s in range(k):
                    c[i, j] += a[i, s] * b[s, j]
        return c


    def mat_vec_mult(matrix, vector): # Наивное перемножение матрицы на вектор
        num_rows = len(matrix)
        num_cols = len(matrix[0])
        result = [0] * num_rows

        for i in range(num_rows):
            for j in range(num_cols):
                result[i] += matrix[i,j] * vector[j]

        return result


    mat_vec_mult(np.array([[1,2],[2,3],[4,7]]),[4,5]), matmul(np.array([[1,2],[2,3]]),np.array([[1,2],[2,3]]))''')
    
    
def q2():
    print('''
    from collections import OrderedDict

    class LRUCache:
        def __init__(self, capacity: int):
            """
            Инициализация кэша с заданной ёмкостью.
            """
            self.cache = OrderedDict()
            self.capacity = capacity

        def get(self, key: int) -> int:
            """
            Получить значение из кэша по ключу.
            Если ключа нет, вернуть -1.
            """
            if key in self.cache:
                # Переместить используемый элемент в конец (считается недавно использованным)
                self.cache.move_to_end(key)
                return self.cache[key]
            return -1

        def put(self, key: int, value: int):
            """
            Добавить элемент в кэш. Если кэш заполнен, удалить наименее используемый элемент.
            """
            if key in self.cache:
                # Если ключ уже существует, обновить значение и переместить в конец
                self.cache.move_to_end(key)
            self.cache[key] = value
            if len(self.cache) > self.capacity:
                # Удалить первый (наименее недавно использованный) элемент
                self.cache.popitem(last=False)

    # Пример использования
    cache = LRUCache(2)

    # Операции
    cache.put(1, 1)  # Кэш: {1: 1}
    cache.put(2, 2)  # Кэш: {1: 1, 2: 2}
    print(cache.get(1))  # Вернет 1, Кэш: {2: 2, 1: 1}
    cache.put(3, 3)  # Кэш: {1: 1, 3: 3} (удален 2)
    print(cache.get(2))  # Вернет -1 (так как 2 удален)
    cache.put(4, 4)  # Кэш: {3: 3, 4: 4} (удален 1)
    print(cache.get(1))  # Вернет -1
    print(cache.get(3))  # Вернет 3, Кэш: {4: 4, 3: 3}
    print(cache.get(4))  # Вернет 4, Кэш: {3: 3, 4: 4}''')


def q2_th():
    print('''Иерархия памяти — это способ организации различных типов памяти компьютера так, чтобы ускорить работу процессора. Память делится на уровни по скорости доступа и размеру: быстрые уровни маленькие и дорогие, а медленные — большие и дешевые.

**Уровни иерархии:**

**1. Регистр процессора:**

- Самый верхний уровень.
- Находится внутри процессора.
- Скорость: сверхбыстрая, доступ за один такт процессора.
- Объем: крошечный (несколько килобайт).
- Стоимость: очень высокая.

**2. Кэш-память процессора (CPU Cache):**
Состоит из 3 уровней:
- L1 (уровень 1):
  - Самая быстрая и дорогая кэш-память.
  - Очень маленький объем (16–128 КБ).
-L2 (уровень 2):
  - Чуть медленнее, но больше (256 КБ – несколько МБ).
- L3 (уровень 3):
  - Медленнее L1 и L2, общий для всех ядер процессора.
  - Объем до десятков МБ.
- Назначение: хранение данных, часто используемых процессором, для минимизации задержек.

**3. Оперативная память (RAM):**

- Скорость: медленнее кэша, но быстрее SSD.
- Объем: значительно больше (гигабайты).
- Стоимость: относительно дорогая.
- Используется для хранения данных и инструкций программ во время выполнения.

**4. Твердотельные накопители (Solid State Drives):**

- Включают неэнергозависимую флэш-память.
- Скорость: медленнее RAM, но быстрее, чем механические жесткие диски.
- Объем: большие (терабайты).
- Стоимость: средняя.
- Используются для долговременного хранения данных.
- Механические жесткие диски (HDD):

**5. Самый нижний уровень.**
- Скорость: самая медленная.
- Объем: очень большой (терабайты).
- Стоимость: самая низкая.
- Используются для долговременного хранения данных, к которым доступ требуется редко.


**План кеша (Cache Planning)**
Кэш работает как промежуточный буфер между процессором и оперативной памятью для ускорения доступа к часто используемым данным. Процесс организации кэша включает следующие аспекты:

**1. Кэш-линии:**

- Данные организуются в блоки фиксированного размера (обычно 32–128 байт).
- При кэшировании загружается вся кэш-линия, а не только отдельный байт.

**2. Ассоциативность кэша:**

- Определяет, как строки памяти сопоставляются с блоками в кэше.
  - Прямое отображение: каждая строка памяти может храниться только в определенном блоке кэша.
  - Полностью ассоциативный кэш: каждая строка памяти может находиться в любом блоке кэша.
  - N-канальный ассоциативный кэш: компромисс между двумя подходами.
  
**3. Алгоритмы замещения:**

- Когда кэш заполняется, нужно освободить место для новых данных.
- Пример: LRU (Least Recently Used), FIFO (First In, First Out), Random Replacement.


**Алгоритм LRU (Least Recently Used)**
LRU — один из самых распространенных алгоритмов замещения данных в кэше.

**Принцип работы:**

- При кэш-промахе (отсутствие данных в кэше) заменяется тот блок данных, который дольше всех не использовался.
- Данные, к которым был последний доступ, считаются самыми "свежими".

**Реализация:**

- Используется структура данных (обычно связанный список или стек).

**При каждом доступе к данным:**

- Если данные уже в кэше — переместить их в начало списка.
- Если данных нет в кэше:
- Если кэш заполнен, удалить последний элемент списка (самый "старый").
- Добавить новые данные в начало списка.

**Плюсы:**

- Эффективно для данных с локальностью запросов.
- Снижает частоту промахов.

**Минусы:**

Увеличенные затраты на обновление структуры (в худшем случае $\mathscr{O}(n)$)''')
