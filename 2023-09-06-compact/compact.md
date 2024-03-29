# 1. Призрачное состояние

# 1.1 Неоптимизированная рекурсия
```Python
def fact(n: int) -> int:
    if n < 2:
        return 1
    return n * fact(n - 1)
```
В этом учебном примере, который я показывал студентам,
неявно присутствует стек, который постепенно заполняется значениями,
и может переполниться, если `n` достаточно велико.
Это призрачное состояние лежит даже глубже уровня кода,
его здесь не видно.

Аналогично, внутреннее состояние есть и у версии с циклом.
```Python
def fact(n: int) -> int:
    r = 1
    for i in range(2, n + 1):
        r *= i
    return r
```
Их здесь даже два: `r` и `i`.
Хотя здесь переполнение не происходит, мутабельные состояния запутывают код,
что в более сложных примерах будет создавать проблемы.

Можно использовать хвостовую рекурсию,
но лучшая версия - с функциями высшего порядка:
```Python
fact = lambda n: reduce(mul, range(1, n + 1))
```

# 1.2 Ещё одна функция с циклом
```Python
class BasisTensor(Tensor):

    def __init__(
            self,
            array: NDArray[Any, Any],
            axes: tuple[Axis, ...],
            tags: dict[Axis, set[Any]]) -> None:
        basis_tags, rest_tags = split_tags(tags, Basis)
        super().__init__(array, axes, rest_tags)
        self.__bases = dict()
        for axis, axis_tags in basis_tags.items():
            assert len(axis_tags) == 1
            tag = next(iter(axis_tags))
            assert isinstance(tag, Basis)
            self.__bases[axis] = tag
    
    ...
```
Это только одна из многих и не самая сложная функция, где теги осей
перебираются в цикле, и создаются промежуточной переменные,
чтобы убедиться, что множество имеет размер ровно 1.

Решение этой проблемы было радикальным - глубокое изменение
способа передачи тегов конструкторам:
```Python
class BasisTensor(Tensor):

    def __init__(
            self,
            array: NDArray[Any, Any],
            axes: tuple[WrapAxis, ...],
            tags: dict[str, dict[Axis, Any]]) -> None:
        self.__bases, rest_tags = split_tags(tags, "basis")
        super().__init__(array, axes, rest_tags)
        ...
    
    ...
```


# 2. Неточность

## 2.1 Неявное ограничение структуры входных данных
```Python
def subst_k(op: BasisTensor, k: BasisTensor) -> BasisTensor:
    ...
```
Эта функция умеет работать вовсе не с любыми экземплярами `BasisTensor`,
а только с теми, где есть определённым образом "настроенные" оси:
```Python
# `op` must have axes of type `KAxis` with bases `k_basis_xyz` or `k_basis_1xyz`
# `k` must have single axis of type `KAxis` with basis `k_basis_xyz`
def subst_k(op: BasisTensor, k: BasisTensor) -> BasisTensor:
    ...
```
Правильная спецификация, соответствующая изначальному замыслу, другая.
Во-первых, нам не нужно дублировать информацию в типе оси и типе базиса.
Во-вторых, нужна поддержка большего разнообразия базисов.
```Python
# `op` must have axes with bases of type `KBasis`
# `k` must have single axis with basis of type `KBasis`
# The bases of `op` and `k` must match by k-vector dimension
# for example: k_basis_xyz in `k` and k_basis_xyz or k_basis_1xyz in `op`
def subst_k(op: BasisTensor, k: BasisTensor) -> BasisTensor:
    ...
```


## 2.2 Слишком общий тип входных данных
```Python
class Tensor:
    @classmethod
    def wrap(cls: Type[TensorType], array: NDArray[Any, Any], *axes: WrapAxis) -> TensorType:
        ...
    
    def get_array(self, *axes: WrapAxis) -> NDArray[Any, Any]:
        ...
    
    ...
```
В старой версии кода `WrapAxis` - это почти всё, что угодно,
в том числе и то, что функция `get_array` обрабатывать по спецификации и не должна.
```Python
class Tensor:
    # `axes` accepts any axis description:
    # +a - add axis with size=1
    # a[size] - require definite axis size
    # a(key=value) - send custom information to tensor constructor
    # a[n] * b[m] - split single array axis into (n x m) array using reshape
    @classmethod
    def wrap(cls: Type[TensorType], array: NDArray[Any, Any], *axes: TagAxisDescr) -> TensorType:
        ...
    
    # `axes` accepts any axis description without custom information and sizes:
    # +a - add axis with size=1
    # a * b - merge two or more axes into one using reshape
    def unwrap(self, *axes: AxisDescr) -> NDArray[Any, Any]:
        ...

    ...
```
В новой версии есть чёткое разделение: `AxisDescr` не может содержать никакую
дополнительную информацию, а `TagAxisDescr` - может.
Дополнительная информация используется только при "обёртывании" массива,
поэтому она доступна только методу `wrap`, но не `unwrap`.


## 2.3
В старой версии класс `DualTensor` производил копирование дополнительной
информации между связанными осями.
```Python
class DualTensor(Tensor):
    __row_col_links: dict[Axis, Axis]
    __col_row_links: dict[Axis, Axis]

    def __init__(
            self,
            array: NDArray[Any, Any],
            axes: tuple[Axis, ...],
            tags: AxisTags) -> None:
        ...
        for col, row_tags in link_tags.items():
            ...
            new_col_tags = rest_tags.get(col, set()) | row_conj_tags
            new_row_tags = rest_tags.get(row, set()) | col_conj_tags
            if new_col_tags:
                rest_tags[col] = new_col_tags
            if new_row_tags:
                rest_tags[row] = new_row_tags
        super().__init__(array, axes, rest_tags)
        ...

    ...
```
Предполагалось, что это упростит интерфейс,
но это привело к неявному ограничению на порядок множественного наследования:
```Python
# Настройки осей будут сначала скопированы между строками и столбцами,
# а затем обработаны в `WaveMatrices`
class MatchMatrices(DualTensor, WaveMatrices):
    ...

# Настройки осей будут обработаны в `WaveMatrices` отдельно для строк
# и столбцов. Это ошибочное поведение!
class MatchMatrices(WaveMatrices, DualTensor):
    ...
```
Пока `DualTensor` явно виден, это ещё терпимо,
но если в наследовании будет ещё пара уровней,
то данное поведение станет скрытым, а код - более хрупким.

Более глубокий анализ преметной области показал,
что копирование информации между связанными осями может быть нежелательным
для некоторых видов тензоров.
Пусть каждый из них занимается копированием отдельно,
а тензоры вообще не думают о связанных осях (см. далее 3.3).


# 3. Интерфейс проще реализации

## 3.1 Параметр, скрытый в другом параметре
```Python
class BandBasis(Basis):
    @property
    @abstractmethod
    def valence_band_size(self) -> int:
        assert False

class Kane8Basis(BandBasis):
    @property
    def size(self) -> int:
        return 8
    
    @property
    def valence_band_size(self) -> int:
        return 6

...

basis = Kane8Basis()
hamiltonian = BandHamiltonian.wrap(source, u_ket(basis), u_bra(u_ket))
```
Размер валентной зоны для `hamiltonian` передаётся внутри параметра `basis`
в виде свойства `BandBasis.valence_band_size`.

Во-первых, это создаёт дополнительную когнитивную нагрузку при чтении кода.

Во-вторых, в тензоре, хранящем решения уравнения после их отбора,
размер валентной зоны может быть произвольным (задаётся пользователем).
Тогда, информация, хранящаяся в `basis` будет ложной.

Просто передавать размер валнетной зоны через базис - плохая идея.
Для этого нужно использовать отдельный явный механизм:
```Python
class ValenceBandSize(DualTag)
    __value: int

    def __init__(self, value: int) -> None:
        self.__value = value

    @property
    def conj(self) -> "ValenceBandSize": # для автоматического копирования этих данных из u_ket в u_bra
        return self

...

hamiltonian = BandHamiltonian.wrap(source, u_ket(basis, ValenceBandSize(6)), u_bra(u_ket))
```


## 3.2 Передача информации с помощью динамической типизации
В общем случае это не плохо, но в предыдущем примере - не очень:
```Python
hamiltonian = BandHamiltonian.wrap(source, u_ket(basis, ValenceBandSize(6)), u_bra(u_ket))
```
Названия переменных имеют физический смысл, но вот эквивалентный пример
```Python
t = SomeTensorType.wrap(source, a(b, SomeSize(6)), c(a))
```
Как быстро понять, что `b` - базис, а не ось?
Как быть уверенными, что под `c(a)`
подразумевается именно `a`-строки и `c`-столбцы,
а не опечатка при передаче чего-то другого в качестве параметра к `c`? 

Лучше сделать передачу параметров (`a(b)`) более явной,
отделив её от связывания осей (`c(a)`):
```Python
t = SomeTensorType.wrap(source, a(basis=b, some_size=6), c(a))
```


## 3.3 Один механизм для принципиально разных действий
Связывание осей и разделение их на строки и столбцы на уровне логики
является более фундаментальным, чем просто передача параметров.
Например, этот механизм управляет копированием параметров
между связанными осями.

Лучше связать оси друг с другом независимо от тензоров, добавив к ним
операцию сопряжения:
```Python
t = SomeTensorType.wrap(source, a(basis=b, some_size=6), a.conj)
```
Функции, для которых связывание осей важно, обработают эту информацию сами.
Тензорам лучше оставаться как можно более простыми контейнерами и не залезать
на этот уровень логики.

Дополнительно мы избавляемся от необходимости ряда проверок входных данных,
например, уже не получится привязать две оси к одной:
```Python
# нужна дополнительная проверка параметров
t = SomeTensorType.wrap(src, a, b(a), c(a))
```
```Python
# будет отловлено проверкой на повторяющиеся оси: a.conj == a.conj
t = SomeTensorType.wrap(src, a, a.conj, a.conj)
```


# Резюме
Сложно было найти в моём новом коде действительно проблемное
призрачное состояние, т.е. такое, которое вело бы
к недокументированному поведению.
Тем не менее я посчитал, что любые мутабельные состояния потенциально опасны,
и нужно вырабатывать привычку обходиться без них.

Самый большой недостаток, который я устранил при выполнении данного задания -
зависимость от порядка множественного наследования.
Это настоящая мина замедленного действия.
Даже я бы на неё наверняка наступил, что уж говорить про студентов.
Не стоит полагаться на тонкости MRO (method resolution order) в Python.
Хоть это и документированный алгоритм, понять эту документацию непросто,
а отлавливать такие ошибки - большая головная боль.

В новой версии порядок вызова конструкторов не важен.
Они могут читать теги и сохранять свою информацию независимо друг от друга.
Лишь бы все дополнительные данные были вычищены, на пути к базовому классу,
который уже работает с "чистыми" осями.
Даже если для каких-то сложных вещей понадобится особый порядок обработки тегов,
это уже будет всяко не у самого корня иерархии классов,
и контролировать это будет легче.

С неточностью было сложнее всего.
Я нашёл больше примеров, где спецификация в виде типов аргументов функции
слишком общая, и её надо сужать, а не расширять реализацию.
