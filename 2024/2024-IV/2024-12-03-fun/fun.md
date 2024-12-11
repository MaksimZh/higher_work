# Функциональные интерфейсы

## 1. Теория
При изучении функционального программирования (ФП) меня всегда смущали
иммутабельные стеки, списки, очереди и т.п.
То, что в императивном коде просто меняет состояние,
в функциональном создаёт новую коллекцию,
а это расходы памяти на хранение и времени на копирование.

Такие сомнения - следствие привычки к императивному мышлению.
В школе я учил Pascal, в университете - C++, в аспирантуре - D,
на работе - Python.
У человека, который ещё в школе начал с изучения ФП,
возник бы резонный вопрос:

> эти память и копирование сейчас с вами в одной комнате?

Да, прямо под столом слева - в системном блоке,
только при чём здесь программа?
Память и копирование - это детали реализации.
То, что мы мыслим такими терминами при написании программ -
это оптимизация, возможно, преждевременная.

В мире чистых функций нет ни памяти, ни копирования, ни перезаписи,
а есть значения и их последовательности.
Это чистая математика!
Для особых случаев, когда возврат к предыдущим значениям-состояниям невозможен,
у нас есть монады.

То, что в императивном коде мы видим, что последовательность значений
хранится в одной перезаписываемой ячейке памяти -
это оптимизация и детали реализации.
В идеале, о таких мелочах должен беспокоиться компилятор.


## 2. Практика
Хотя я в основном использую Python,
уже довольно давно стараюсь писать максимум кода
именно в функциональном стиле.
Поэтому найти на чём потренироваться непросто.
Есть, правда, несколько классических алгоритмов,
которые было бы интересно переписать в стиле ФП.


### 2.1. Сортировка пузырьком
Давно уже размышлял о том, как доказать корректность сортировки пузырьком.
Так родилась идея об инвариантах, которые выполняются на каждом шаге,
в результате чего размер отсортированной части массива постепенно растёт.
За инвариантами будет следить специальный иммутабельный класс.

```Python
class BubbleSegments:
    __order: Callable[[int, int], bool]
    __head: list[int]
    __tail: list[int]
    __sorted: list[int]

    # У нас есть три списка: head, tail и sorted
    # - если head и tail не пустые, то первый элемент tail упорядочен
    #   относительно любого элемента из head
    # - массив sorted упорядочен внутри себя и упорядочен относительно
    #   любого элемента из head и tail
    def __init__(self, order: Callable[[int, int], bool], a: list[int]) -> None:
        # Вначале есть только tail, и инварианты выполняются,
        # потому что два других списка пусты
        self.__head = []
        self.__tail = a
        self.__sorted = []
        self.__order = order

    # Секретный конструктор, недоступный клиентскому коду,
    # чтобы нельзя было испортить инварианты
    @classmethod
    def __init(
            cls,
            order: Callable[[int, int], bool],
            head: list[int], tail: list[int], sorted: list[int],
            ) -> "BubbleSegments":
        instance = cls.__new__(cls)
        instance.__order = order
        instance.__head = head
        instance.__tail = tail
        instance.__sorted = sorted
        return instance
    
    def __repr__(self) -> str:
        return f"{self.__head} {self.__tail} {self.__sorted}"

    @property
    def sorted(self) -> list[int]:
        return self.__sorted

    def advance(self) -> "BubbleSegments":
        # Сортировка завершена?
        if len(self.__tail) == 0:
            return self
        # В tail остался один элемент, и он точно упорядочен
        # относительно head и sorted 
        if len(self.__tail) == 1:
            return self.__init(
                self.__order,
                [],
                self.__head,
                self.__tail + self.__sorted)
        # Первые два элемента tail упорядочены - первый идёт в head
        if self.__order(*self.__tail[:2]):
            return self.__init(
                self.__order,
                self.__head + self.__tail[:1],
                self.__tail[1:],
                self.__sorted)
        # Первые два элемента tail не упорядочены - второй идёт в head,
        # и тогда первый будет упорядочен относительно head + tail[1]
        return self.__init(
                self.__order,
                self.__head + self.__tail[1:2],
                self.__tail[:1] + self.__tail[2:],
                self.__sorted)


def fubble(a: list[int], order: Callable[[int, int], bool]) -> list[int]:
    s = BubbleSegments(order, a)
    while len(s.sorted) < len(a):
        s = s.advance()
    return s.sorted
```


### 2.2. Решето Эратосфена
Вместо того, чтобы модифицировать массив, создаём новый.
Этот код буквально разбивает хвост списка на равные куски,
отсеивая последний элемент.
Вместо циклов используется рекурсия
и функции для работы с последовательностями.

```Python
def kill_last(a: tuple[int, ...]) -> tuple[int, ...]:
    return a[:-1] + (0,)

def sieve(a: list[int], b: list[int]) -> list[int]:
    if b == []:
        return a
    if b[0] == 0:
        return sieve(a, b[1:])
    return sieve(
        a + b[:1],
        list(
            chain.from_iterable(
                map(
                    kill_last,
                    batched(b[1:], b[0])))))

def f_prime(n: int) -> list[int]:
    return sieve([], list(range(2, n + 2)))
```


### 2.3. Сортировка быстрым слиянием
Есть иммутабельный класс `Sorted` (сортированный список),
у которого есть метод `merge` слияния с другим таким списком.
Клиентский код может создавать только `Sorted` размера 0 и 1,
а списки большего размера - только через `merge`.
В итоге, когда мы сливаем все элементы в один список -
он точно отсортирован.

```Python
@final
class Sorted:
    __data: list[int]

    def __repr__(self) -> str:
        return str(self.__data)

    # Клиентский код может создавать только сортированные списки размера 0 и 1
    def __init__(self, data: Optional[int] = None) -> None:
        self.__data = [] if data is None else [data]

    @property
    def data(self) -> list[int]:
        return self.__data

    @property
    def size(self) -> int:
        return len(self.__data)

    # Секретный конструктор для сортированного списка любого размера
    @classmethod
    def __init(cls, data: list[int]) -> "Sorted":
        instance = cls.__new__(cls)
        instance.__data = data
        return instance    
    
    # Слияние создаёт новый сортированный список,
    def merge(self, other: "Sorted") -> "Sorted":
        # Немного императивного кода внутри, хотя можно и рекурсией
        dest = list[int]()
        a = self.data
        b = other.data
        while a and b:
            if a[0] < b[0]:
                dest.append(a[0])
                a = a[1:]
                continue
            dest.append(b[0])
            b = b[1:]
            continue
        # Используем секретный конструктор
        return self.__init(dest + a + b)


def merge_all(a: list[Sorted]) -> list[Sorted]:
    if len(a) == 1:
        return a
    if len(a) % 2 == 1:
        return merge_all(a + [Sorted()])
    return merge_all([p[0].merge(p[1]) for p in batched(a, 2)])


def fun_sort(a: list[int]) -> list[int]:
    return merge_all(list(map(Sorted, a)))[0].data
```


### 2.4. Поиск в ширину на поле
Почему бы и нет?
Только копировать поле не будем.
Вместо этого позаботимся о том,
чтобы был доступ только к последней его версии.

```Python
from typing import Optional, Type

class Field:
    # Либо ссылка на данные, либо ничего
    __data: Optional[list[list[int]]]

    # Нельзя просто взять и создать абстрактное поле
    def __init__(self) -> None:
        assert False

    # Приватный конструктор
    # Только поле может создать поле
    def _init(self, field: list[list[int]]) -> None:
        self.__data = field
    
    # Приватный конструктор для создания нового экземпляра
    @classmethod
    def _create[T: Field](cls: Type[T], field: list[list[int]]) -> T:
        instance = cls.__new__(cls)
        instance._init(field)
        return instance

    # Приватный метод для доступа к данным
    def _lock(self) -> list[list[int]]:
        # А поле точно не устарело?
        assert self.__data is not None
        f = self.__data
        # Стираем ссылку на данные у этого экземпляра
        self.__data = None
        return f
    
    def get(self, y: int, x: int) -> int:
        assert self.__data is not None
        return self.__data[y][x]


class StartField(Field):

    # Загрузить данные можно только при создании поля этого типа
    def __init__(self, field: list[list[int]]) -> None:
        # Копируем данные, чтобы иметь уникальную ссылку
        self._init([row.copy() for row in field])

    # Начинаем поиск
    # Результат - другой тип поля
    def start(self, y: int, x: int) -> "SearchField":
        f = self._lock()
        assert f[y][x] == 0
        f[y][x] = 1
        # Ссылка на данные есть только у возвращаемого значения
        return SearchField._create(f)


class SearchField(Field):
    
    # Продолжать поиск можно только с этим типом поля
    def advance(self) -> "SearchField | StopField":
        f = self._lock()
        modified = False
        for y in range(len(f)):
            for x in range(len(f[0])):
                if f[y][x] != 0:
                    continue
                adjacent = list(filter(
                    lambda x: x > 0,
                    [f[y - 1][x], f[y + 1][x], f[y][x - 1], f[y][x + 1]]))
                if not adjacent:
                    continue
                f[y][x] = min(adjacent) + 1
                modified = True
        # Ссылка на данные есть только у возвращаемого значения
        if modified:
            # Что-то изменилось - продолжаем
            return SearchField._create(f)
        else:
            # Заполнили все доступные клетки
            return StopField._create(f)

class StopField(Field):
    # В таком поле поиск продолжать нельзя
    pass


def path_len(
        field: list[list[int]],
        start: tuple[int, int],
        stop: tuple[int, int]) -> int:
    start = (start[0] + 1, start[1] + 1)
    stop = (stop[0] + 1, stop[1] + 1)
    width = len(field[0])
    assert all(len(f) == width for f in field[1:])
    f = StartField(
        [[-1] * (width + 2)] + \
        [[-1] + row.copy() + [-1] for row in field] + \
        [[-1] * (width + 2)]).start(*start)
    while type(f) == SearchField and f.get(*stop) == 0:
        f = f.advance()
    return f.get(*stop) - 1

field = [
    [ 0,  0,  0,  0,  0,  0],
    [ 0, -1, -1,  0, -1,  0],
    [ 0,  0, -1,  0, -1,  0],
    [ 0,  0, -1, -1, -1,  0],
    [ 0,  0, -1,  0, -1,  0],
]

print(path_len(field, (0, 0), (4, 5)))
print(path_len(field, (3, 1), (2, 5)))
print(path_len(field, (3, 1), (4, 3)))
```

Можно иметь несколько ссылок на один экземпляр поля,
но при создании нового экземпляра с помощью `start` или `advance`
внутри старого экземпляра окажется `None`.


## Выводы
В идеальном случае нам было бы не нужно заботиться
о хранении и копировании данных.
Например, в 2.1 - 2.3. компилятор мог бы догадаться,
что старые данные не используются,
и размещать списки в том же месте памяти.
В 2.4 эта оптимизация сделана вручную
вместе с защитой от попыток случайного использования старых состояний.

Компилятор, который сможет проводить такие оптимизации,
станет настоящим прорывом,
так как позволит полностью сосредоточиться
на логике преобразования данных
и абстрагироваться от механизма их хранения.
Встроенные механизмы защиты старых состояний присутствуют в
Rust (borrowing)
и Haskell (монаду IO не скопируешь).
Так что прогресс в этой области есть.
