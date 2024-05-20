# Неочевидные проектные ошибки (1)

## 1. Производная
Не нужно производную брать!
То есть, производную брать нужно, но не всегда нужно брать производную.
```Python
class ArrayPoly:
    ...
    
    def __call__(self, x, deriv=0):
        if isinstance(x, np.ndarray):
            return self.__evalArray(x, deriv)
        elif isinstance(x, ArrayPoly):
            assert(deriv == 0)  # <------------------
            return self.__substPoly(x)
        else:
            return self.__evalScalar(x, deriv)
    
    ...
```
Проблемы с подстановкой полинома в полином и производной возникли из-за того,
что метод `__call__` делает слишком много:
вычисление значения и взятие производной.

Нужно перенести производную в другой метод.
Пусть производная тоже будет полиномом:
```Python
class ArrayPoly:
    ...
    
    def __call__(self, x):
        if isinstance(x, np.ndarray):
            return self.__evalArray(x)
        if isinstance(x, ArrayPoly):
            return self.__substPoly(x)
        return self.__evalScalar(x)

    def get_deriv(self, deriv=1) -> ArrayPoly:
        ...
    
    ...
```
Теперь и методы вычисления будут проще, и другой полином в производную можно
подставлять.
Красота!


## 2. Квадратная матрица
Когда код - просто песня:
```Python
class ArrayPoly:
    def __init__(self, coefs):
        ...
    ...

def det(a: ArrayPoly):                  # Определитель квадратной матрицы
    assert(a.ndim >= 2)                 # А может, и не матрицы
    assert(a.shape[-1] == a.shape[-2])  # А может, не квадратной
    ...                                 # Хотим мы посчитать
```
Тут нужно порабоать с системой типов
```Python
class ArrayPoly:
    def __init__(self, coefs):
        ...
    ...

class MatrixPoly(ArrayPoly):
    def __init__(self, coefs):
        assert coefs.ndim >= 2  # Массивы матриц тоже ОК, хотя бы два измерения
        super().__init__(coefs)
    ...

class SquareMatrixPoly(MatrixPoly):
    def __init__(self, coefs):
        assert coefs.ndim >= 2
        assert coefs.shape[-1] == coefs.shape[-2]
        super().__init__(coefs)
    ...

def det(a: SquareMatrixPoly):
    ...
```
Проверки ушли в конструкторы,
значит ошибки в формате коэффициентов будут выявляться раньше.
То, что определитель вычисляется только для квадратной матрицы, проверит линтер.


## 3. Умножение матриц
```Python
class ArrayPoly:
    ...
    def __matmul__(self, value: ArrayPoly):
        assert(self.ndim >= 2)
        assert(value.ndim >= 2)
        ...

class MatrixPoly(ArrayPoly):
    ...
```
Всему своё место
```Python
class ArrayPoly:
    ...

class MatrixPoly(ArrayPoly):
    ...
    def __matmul__(self, value: MatrixPoly):
        ...
```

## 4. Возведение в неотрицательную степень
Когда код писался без линтера:
```Python
class ArrayPoly:
    ...
    def __pow__(self, value):
        if type(value) != int:
            return NotImplemented
        ...
```
Когда есть линтер:
```Python
class ArrayPoly:
    ...
    def __pow__(self, value: int):
        assert value >= 0
        ...
```
Когда прошёл Быструю прокачку в ООП:
```Python
class Nonnegative:
    ...

class ArrayPoly:
    ...
    def __pow__(self, value: Nonnegative):
        ...
```


## 5. Матрица матриц
Неявная типизация
```Python
def _calcL(mxA, atol):
    assert(mxA.ndim == 4)
    ...
```
Явная типизация
```Python
def _calcL(mxA: NDArray[Shape["*, *, *, *"], Complex], atol: float) -> list[list[SquareMatrixPoly]]:
    assert atol > 0 # забыл в прошлый раз
    ...
```
А что если... АТД?
```Python
class EquationCoefficients:
    ...

class AbsTolerance:
    ...

class CharacteristicPolynomials:
    ...

def _calc_characteristic_polynomials(mxA: EquationCoefficients, atol: AbsTolerance) -> CharacteristicPolynomials:
    ...
```
