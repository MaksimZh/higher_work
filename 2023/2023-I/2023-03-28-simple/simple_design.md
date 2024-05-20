# Правила простого проектного дизайна

## 1. Избавляться от точек генерации исключений

### 1.1 Параметры процедуры
Вместо того, чтобы проверять имя и тип параметра
добавил в проект параметризованные
[дескрипторы](https://docs.python.org/3/reference/datamodel.html#implementing-descriptors)
`Input` и `Output`.
Теперь имена входных и выходных значений, а также их тип, будет проверять линтер.

Было:
```Python
class Summator(Solver):
    def put(id: str, value: Any) -> None:
        if id not in {"left", "right"}:
            ... # ошибка
        if not _type_fits(type(value), int):
            ... # ошибка
        ...
    
    def get(id: str) -> Any:
        if id != "result":
            ... # ошибка
        ...
    ...
...
s = Summator()
s.put("foo", 5)       # ошибка во время выполнения
s.put("left", "lol")  # ошибка во время выполнения
```
Стало:
```Python
class Summator(Solver):
    left = Input[int]()
    right = Input[int]()
    result = Output[int]()
    ...
...
s = Summator()
s.foo = 5       # линтер: нет такого атрибута
s.left = "lol"  # линтер: несовместимый тип
```

### 1.2 Связывание процедур
Вместо описания графа вычислений с помощью списка узлов со связями
теперь узлы создаются как объекты и связываются через атрибуты.
Входы и выходы теперь наглядно перечисляются в начале описания класса,
а опечатки в именах атрибутов и ошибки при связывании аргументов
с несовместимыми типами ловятся линтером.
Бонус: имена для связей теперь не обязательны.

Было:
```Python
class Block(SolverFactory):
    def __init__(self, description: list[SolverNodeDescription]) -> None:
        ...
    ...
...
# ошибки будут видны только во время выполнения
block = Block(
    [
        (W, {"a": In("aa"), "b": In("bb")}, {"c": Link("u1"), "d": Link("v1")}),
        (W, {"a": Link("u1"), "b": Link("v1")}, {"c": Link("u2"), "d": Link("v2")}),
        (W, {"a": Link("u2"), "b": Link("v2")}, {"c": Out("cc"), "d": Out("dd")}),
    ])
```
Стало:
```Python
class MyBlock(Solver):
    aa = Input[int]()
    bb = Input[int]()
    cc = Output[int]()
    dd = Output[int]()
    
    # линтер отловит большинство опечаток
    def __init__(self) -> None:
        self.w1 = W()
        self.w2 = W()
        self.w3 = W()
        self.w1.a = self.aa
        self.w1.b = self.bb
        self.w2.a = self.w1.c
        self.w2.b = self.w1.d
        self.w3.a = self.w2.c
        self.w3.b = self.w2.d
        self.cc = self.w3.c
        self.dd = self.w3.d
```


## 2. Отказаться от дефолтных конструкторов без параметров

### 2.1 Создание процедуры
Раньше при создании нескольких процедур одного типа объекты отличались только
своими связями.
В случае ошибки было трудно понять какая именно процедура "упала".
Теперь нужно явно указывать какому блоку процедура принадлежит и как называется.

Было:
```Python
class W(Solver):
    ...

class My1(Solver):
    ...
    def __init__(self) -> None:
        self.w1 = W()
        self.w2 = W()
        ...

class My2(Solver):
    ...
    def __init__(self) -> None:
        self.w1 = W()
        self.w2 = W()
        ...

# Удачной отладки >:D
```
Стало:
```Python
class W(Solver):
    def __init__(self, owner: Solver, id: str) -> None:
        ...
    ...

class My1(Solver):
    ...
    def __init__(self, owner: Solver, id: str) -> None:
        self.w1 = W(self, "w1")
        self.w2 = W(self, "w2")
        ...

class My2(Solver):
    ...
    def __init__(self, owner: Solver, id: str) -> None:
        self.w1 = W(self, "w1")
        self.w2 = W(self, "w2")
        ...
```
Но ведь мы можем задать другого "владельца" (`owner`), или ошибиться в имени.
А можно вообще забыть создать процедуру.

С учётом правила 1. следует делать так:
```Python
class SubSolver(Generic[T]):
    def __init_subclass__(cls) -> None:
        # здесь мы узнаем тип `T` и сохраним его
        self.__solver_type = ...

    def __set_name__(self, owner_type: Type[Solver], name: str) -> None:
        # запомним, как этот атрибут называется в классе
        self.__id = name

    def __get__(self, owner: Solver, obj_type: type) -> T:
        attr_name = f"__{self.__id}"
        # создать объект с правильными `owner` и `id`, если его ещё нет
        if not hasattr(owner, attr_name):
            setattr(owner, attr_name, self.__solver_type(owner, self.__id))
        # вернуть этот объект
        return getattr(owner, attr_name)

...

class My1(Solver):
    w1 = SubSolver[W]()
    w2 = SubSolver[W]()
    ...

class My2(Solver):
    w1 = SubSolver[W]()
    w2 = SubSolver[W]()
    ...
```

## 2.2 Создание процедуры 2
Можно сразу создавать процедуру с указанными входными параметрами.

Было:
```Python
class MyBlock(Solver):
    aa = Input[int]()
    bb = Input[int]()
    w1 = SubSolver[W]()
    w2 = SubSolver[W]()
    w3 = SubSolver[W]()
    cc = Output[int]()
    dd = Output[int]()
    
    def __init__(self) -> None:
        self.w1.a = self.aa
        self.w1.b = self.bb
        self.w2.a = self.w1.c
        self.w2.b = self.w1.d
        self.w3.a = self.w2.c
        self.w3.b = self.w2.d
        self.cc = self.w3.c
        self.dd = self.w3.d
```
Станет, если будет работать:
```Python
class MyBlock(Solver):
    aa = Input[int]()
    bb = Input[int]()
    w1 = SubSolver(W(a=aa, b=bb))
    w2 = SubSolver(W(a=w1.c, b=w1.d))
    w3 = SubSolver(W(a=w2.c, b=w2.d))
    cc = Output(w3.c)
    dd = Output(w3.d)
    
    def __init__(self, aa: InArg[int], bb: InArg[int]) -> None:
        self.aa = aa
        self.bb = bb
```
Можно было сгенерировать конструктор автоматически с помощью метакласса,
но тогда пришлось бы писать плагин к линтеру,
чтобы он понимал как с этим работать.


## 3. Избегать увлечения примитивными типами данных

## 3.1 NumPy
Массивы NumPy - это примитивные типы данных с анонимными осями:
```Python
def make_matrix(a):
    dim = a.shape[0] * a.shape[2]
    return a.transpose(0, 2, 1, 3).reshape(dim, dim)
```
Здесь куча магических чисел.

Лучше так:
```Python
def make_matrix(a: Tensor) -> Tensor:
    dim = a.get_size("basis") * a.get_size("bloch")
    return Tensor(
        a.get_array("basis", "bloch", "basis+", "bloch+").reshape(dim, dim),
        ("func", "func+"))
```
АТД `Tensor` знает свои оси поимённо и выдаёт правильно транспонированный массив.

## 3.2 Угловой момент
Угловой момент в квантовой механике может быть целым, или полуцелым.

Хранить его в виде целого числителя и делить пополам - некрасиво.

Хранить его в виде вещественного числа - можно задать неверное значение.

Решение - АТД `AngularMomentum`:
```Python
class AngularMomentum:

    def __init__(self, value: float) -> None:
        ...
    
    def is_int(self) -> bool:
        ...

    def __int__(self) -> int:
        ...
    
    def __float__(self) -> float:
        ...

    ...
```
