# Защитный код

# 1.
```Python
class WaveMatrices:
    __tensor: Tensor
    __axes: WaveMatrixAxes

    def __init__(
            self,
            tensor: Tensor,
            dir: str,
            components: str | set[str],
            extra: set[str] = set()) -> None:
        if isinstance(components, str):
            components = {components}
        assert all_str_unique(dir, components, extra)
        assert to_str_set(dir, components, extra) <= tensor.axes
        assert dir not in components
        assert tensor.get_dim(dir) == 2
        wave_axes = WaveAxes(dir, extra)
        wave_dims = [tensor.get_dim(ax) for ax in to_str_set(wave_axes)]
        wave_dims_combined = reduce(mul, wave_dims, 1)
        component_dims = [tensor.get_dim(ax) for ax in components]
        component_dims_combined = reduce(mul, component_dims, 1)
        assert wave_dims_combined == component_dims_combined
        self.__tensor = tensor
        self.__axes = WaveMatrixAxes(wave_axes, components)

    ...
```

Здесь сразу несколько путей для улучшения кода.

Во-первых, оси тензора на уровне логики - это не то же самое, что названия осей.
В идеале, оси должны быть частью конкретного типа тензора, но в Python
добиться этого непросто:
нужно работать с метаклассами и писать плагины для линтеров.
Поэтому для начала сделаем оси отдельным типом, чтобы это были не строки.

Если ось - отдельный объект, а не сторока, то нет равных осей.
Либо это одна и та же ось, либо разные.
Каждая ось создаётся один раз,
а затем используется в других частях кода,
которые **логически связаны** друг с другом.
Теперь они оказываются **связаны на уровне кода**.
Если допущена опечатка в названии оси, то линтер сразу её найдёт,
ведь теперь это идентификатор, а не строка.

Во-вторых, код выше, очевидно, делит оси на категории:
  - волновые оси `wave`:
      - ось направления `dir`;
      - дополнительные волновые оси `extra`;
  - компонентные оси `component`;
  - остальные оси.

На первый взгляд кажется, что категории относятся к тезору
(то как он интерпретирует оси), а не к самим осям.
Однако, на уровне логики этот тензор и оси тесно связаны в предметной области.
Конкретно в данном случае категории осей "заготовлены" под применение методов
трансфер-матрицы и матрицы рассеяния (отсюда и деление волн на направления).
Так что ничто не мешает нам привязать категории к осям.
Сделать это удобно с помощью *льготного наследования*, иерархия которого
будет совпадать с иерархией категорий предметной области.
```Python
class WaveAxis(Axis):
    pass

class WaveDirAxis(WaveAxis):
    pass

class ComponentAxis(Axis):
    pass
```

В-третьих, как только мы перенесли информацию о категориях
из `WaveMatrices` в оси, этот класс больше не хранит новой информации
по сравнению с классом `Tensor`.
Ну и на уровне логики, набор матриц - тензор, который используется в некоторой
специфической области.
Самое время использовать *наследование подтипов*.

Вот результат:
```Python
class WaveMatrices(Tensor):

    def __init__(
            self,
            array: NDArray[Any, Any],
            *axes: Axis) -> None:
        super().__init__(array, *axes)
        dir_axes = self.get_axes(WaveDirAxis)
        assert len(dir_axes) == 1
        dir_axis = dir_axes.pop()
        assert self.get_dim(dir_axis) == 2
        wave_dims = [self.get_dim(ax) for ax in self.get_axes(WaveAxis)]
        wave_dims_combined = reduce(mul, wave_dims, 1)
        component_dims = [self.get_dim(ax) for ax in self.get_axes(ComponentAxis)]
        component_dims_combined = reduce(mul, component_dims, 1)
        assert wave_dims_combined == component_dims_combined
    
    ...
```
Нам больше не нужен класс `WaveMatrixAxes` и поле такого типа,
а вместо пяти assert-ов осталось три.
То есть, код стал проще.

Интерфейс тоже стал проще: не нужно создавать тензор отдельно
и дублировать имена осей.

Было:
```Python
wm = WaveMatrices(
    Tensor(array, "a", "b", "c", "d", "x", "y"),
    dir="a", components = {"c", "d"}, extra={"b"})
```
Стало:
```Python
# оси a, b и т.д. созданы где-то раньше
wm = WaveMatrices(array, a, b, c, d, x, y)
```


# 2.
```Python
class MatchMatrices:
    __tensor: Tensor
    __axes: MatchMatrixAxes

    def __init__(
            self,
            tensor: Tensor,
            row_dir: str, col_dir: str,
            extra: dict[str, str] = {}) -> None:
        assert all_str_unique(row_dir, col_dir, extra.keys(), extra.values())
        assert to_str_set(row_dir, col_dir, extra.keys(), extra.values()) <= tensor.axes
        assert tensor.get_dim(row_dir) == 2
        assert tensor.get_dim(col_dir) == 2
        assert all([(tensor.get_dim(a) == tensor.get_dim(b)) for (a, b) in extra.items()])
        self.__tensor = tensor
        self.__axes = MatchMatrixAxes(row_dir, col_dir, extra)

    ...
```

Всё, что было сделано в предыдущем примере применимо и здесь.

Дополнительно, в данном случае присутствует деление на столбцы и строки матрицы.
Раньше было деление на волны и компоненты, но там не было соответствия 1 к 1
между осями, хватало совпадения произведения размерностей массива.
Для задания связи 1 к 1 вместо словаря используем новые типы данных.

```Python
class WaveAxis(Axis):
    
    def __call__(self, row: "WaveAxis") -> "LinkedAxes":
        return LinkedAxes(row, self)


class LinkedAxes:
    __row: WaveAxis
    __col: WaveAxis
    
    def __init__(self, row: WaveAxis, col: WaveAxis) -> None:
        self.__row = row
        self.__col = col

    @property
    def row(self) -> WaveAxis:
        return self.__row

    @property
    def col(self) -> WaveAxis:
        return self.__col


class MatchMatrices(Tensor):
    __row_links: dict[WaveAxis, WaveAxis]
    __col_links: dict[WaveAxis, WaveAxis]
    
    def __init__(
            self,
            array: NDArray[Any, Any],
            *axes: Axis | LinkedAxes) -> None:
        self.__row_links = dict()
        self.__col_links = dict()
        tensor_axes = list[Axis]()
        for ax in axes:
            if isinstance(ax, LinkedAxes):
                assert ax.row not in self.__row_links
                self.__row_links[ax.row] = ax.col
                assert ax.col not in self.__col_links
                self.__col_links[ax.col] = ax.row
                tensor_axes.append(ax.col)
                continue
            tensor_axes.append(ax)
        super().__init__(array, *tensor_axes)
        row_dir_axes = set(self.get_axes(WaveDirAxis) & self.__row_links.keys())
        assert len(row_dir_axes) == 1
        col_dir_axes = set(self.get_axes(WaveDirAxis) & self.__col_links.keys())
        assert len(col_dir_axes) == 1
        assert self.row_axis_for(self.col_dir_axis) == self.row_dir_axis
        assert self.col_axis_for(self.row_dir_axis) == self.col_dir_axis
        assert self.get_dim(self.row_dir_axis) == 2
        assert self.get_dim(self.col_dir_axis) == 2
        assert (self.__row_links.keys() | self.__col_links.keys()) == self.get_axes(WaveAxis)
        for row, col in self.__row_links.items():
            assert self.get_dim(row) == self.get_dim(col)
    
    ...
```
От поля `__axes: MatchMatrixAxes` мы избавились, но assert-ов меньше не стало.
Здесь имеет место обратный эффект.
Раньше то, что у нас только две оси направлений (по одной для строк и столбцов)
было жёстко задано в списке аргументов конструктора.
Теперь ничто не мешает передать в конструктор любое количество осей такого типа.
С этим разберёмся позже.

Пока порадуемся, что интерфейс стал проще.

Было:
```Python
mm = MatchMatrices(
    Tensor(array, "a", "b", "c", "d", "x", "y"),
    "a", "c", extra={"b": "d"})
```
Стало:
```Python
mm = MatchMatrices(array, a, b, c(a), d(b), x, y)
```
Интерфейс конструктора очень похож для тензора и его подтипов:
просто перечисляем оси как они идут в массиве.
Тип осей и специальные операторы (например, `c(a)`)
подскажут конструктору как их интерпретировать.


# 3.
```Python
def calc_transfer_matrices(
        left_wave: WaveMatrices, right_wave: WaveMatrices,
        row_suffix: str, col_suffix: str,
        ) -> TransferMatrices:
    assert row_suffix != col_suffix
    assert left_wave.dir_axis == right_wave.dir_axis
    assert left_wave.extra_wave_axes == right_wave.extra_wave_axes
    assert left_wave.component_axes == right_wave.component_axes
    assert left_wave.array_axes == right_wave.array_axes
    dir_axis = left_wave.dir_axis
    extra_axes = tuple(left_wave.extra_wave_axes)
    component_axes = tuple(left_wave.component_axes)
    array_axes = tuple(left_wave.array_axes)
    array_shape = tuple(left_wave.tensor.get_dim(ax) for ax in array_axes)
    assert all(
        left_wave.tensor.get_dim(ax) == right_wave.tensor.get_dim(ax) \
        for ax in left_wave.tensor.axes)
    ...
```

Вот одна из функций, ради которых всё затевалось.
Она переименовывает оси с помощью суффиксов.
Мало того, что мы и так могли допустить опечатку в имени оси,
так теперь ещё это имя делится на корень и суффикс.
На уровне логики ось - отдельная сущность.
На уровне кода - имя или имя + суффикс.

Эти суффиксы понадобились, потому что будет умножение
`right_matrix^-1 * left_matrix`
(здесь лево и право - это про физическое пространство, а не про порядок умножения).
Все оси у тензоров одинаковы.
Компонентные оси "съест" умножение, а волновые оси станут строками и столбцами,
и их нужно будет различать.

Но теперь для разделения строк и столбцов есть класс `LinkedAxes`
и оператор-скобки.

```Python
def calc_transfer_matrices(
        left_wave: WaveMatrices, right_wave: WaveMatrices,
        *col_axes: LinkedAxes
        ) -> TransferMatrices:
    assert left_wave.axes == right_wave.axes
    axes_tuple = tuple(left_wave.axes)
    assert left_wave.get_array(*axes_tuple).shape == right_wave.get_array(*axes_tuple).shape
    __row_links = dict[WaveAxis, WaveAxis]((ax.row, ax.col) for ax in col_axes)
    assert __row_links.keys() == left_wave.get_axes(WaveAxis)
    ...
```

Снова избавились от части assert-ов и ещё от концепции суффиксов.

Интерфейс тоже изменился: вместо суффиксов идентификаторы иммутабельных объектов.

Было:
```Python
calc_transfer_matrices(left, right, "_r", "_c")
```
Стало:
```Python
calc_transfer_matrices(left, right, c(a), d(b))
```


# 4.
От следующего решения в итоге отказался,
но оно показывает ряд интересных моментов.

```Python
class Tensor:
    __array: NDArray[Any, Any]
    __axis_indices: dict[Axis, int]

    def __init__(self, array: NDArray[Any, Any], *axes: Axis) -> None:
        assert len(axes) == array.ndim
        assert all_axes_unique(axes) # !!!
        self.__array = array
        self.__axis_indices = dict(zip(axes, range(len(axes))))

    ...
```
Тензор проверяет нет ли совпадающих осей.
В дальнейшем планируется передавать не только оси,
но и более сложные конструкции, например, для добавления новых осей и
разбиения отдельных осей массива на несколько осей тензора.
Тогда количество проверок возрастёт.

Можно передать часть проверок на уровень выше, если использовать
нестандартный кортеж для осей `AxisTuple`, который при создании следит за
тем, чтобы не было совпадений, а также правильно интерпретирует новые оси
и разбиение.
Для создания такого кортежа можно использовать другой оператор вместо запятой:
```Python
array = np.zeros(10, 12)
t1 = Tensor(array, a | b)            # две оси
t2 = Tensor(array, a | b[4] * c[3])  # разбиваем вторую ось (12 = 4 * 3)
t3 = Tensor(array, a | +b | с)       # добавляем новую ось b размерности 1
t4 = Tensor(array, a | b | +a)       # ОШИБКА! ось a встречается дважды
```
В последнем случае ошибка возникнет до вызова конструктора.
Сам конструктор будет таким:
```Python
def __init__(self, array: NDArray[Any, Any], axes: AxisTuple) -> None:
    assert len(axes) == array.ndim
    ...
```
Очень заманчиво создать несколько разных типов кортежей, которые автоматически
выводятся на основе того, что за оси мы комбинируем.
Затем ограничения на оси задавать на уровне типов данных:
```Python
class MatchMatrices(Tensor):
    __row_links: dict[WaveAxis, WaveAxis]
    __col_links: dict[WaveAxis, WaveAxis]
    
    def __init__(
            self,
            array: NDArray[Any, Any],
            axes: MatchMatrixAxisTuple) -> None:
        # в axes нет повторов
        # в axes ровно по одной оси-направлению для строк и столбцов
        # ...
        ...
```
Однако, здесь есть две проблемы, из-за которых от такого подхода
было решено отказаться.

Во-первых, в лучшем случае это просто перенос проверок в другой класс.
В худшем случае, проверки будут размазаны по нескольким классам и будет
трудно при чтении кода собрать в голове логику требований конструктора
ко входным данным.

Во-вторых, при проектировании оказалось, что счёт разных классов для
кортежей и их элементов пойдёт на десятки.
Для того, чтобы не запутаться в этом, нужна гораздо более мощная система типов,
чем есть в Python.
Более того, здесь нужна уже какая-то другая математика:
абстракции над множеством типов.
Иначе очень легко запутаться в десятках типов и связях между ними:
```Python
a, b, c: Axis
a[n] -> SizeAxis
a | b -> AxisTuple
b * c -> AxisMerge
a | b * c -> AxisUnwrapTuple
a[n] * b[m] -> SizeAxisMerge
a * b[m] -> AutoSizeAxisMerge
a[n] * b[m] | c -> AxisWrapTuple
...
```
А так, конечно, хорошо бы, чтобы при создании тензора требовался `AxisWrapTuple`,
при извлечении массива - `AxisUnwrapTuple` и т.д.
Но это точно не про Python.
Здесь даже C++ выглядит предпочтительнее из-за явной статической типизации
и возможностей перегрузки функций.


# 5.
```Python
class Tensor:
    ...
    
    def get_array(self, *axes: Axis | NewAxis | AxisMerge) -> NDArray[Any, Any]:
        array_axes = ArrayAxes()
        for ax in axes:
            array_axes.append(ax)
        indices = tuple(self.__index(ax) for ax in array_axes.present_axes_order)
        ...
    
    def __index(self, axis: Axis) -> int:
        assert axis in self.__axis_indices
        return self.__axis_indices[axis]
```
Приватный метод `__index` используется ровно в одном методе и, фактически,
нужен лишь для проверки того, что ось есть в словаре.

Перенесём проверку на более высокий уровень в коде
```Python
class Tensor:
    ...
    
    def get_array(self, *axes: Axis | NewAxis | AxisMerge) -> NDArray[Any, Any]:
        array_axes = ArrayAxes()
        for ax in axes:
            array_axes.append(ax)
        assert set(array_axes.present_axes_order) == self.__axis_indices.keys()
        indices = tuple(self.__axis_indices[ax] for ax in array_axes.present_axes_order)
        ...
```
Условие стало более жёстким (и правильным), и логика стала очевидна:
все оси тензора должны быть задействованы, и никакие больше.
Для этого теперь используется сравнение множеств, а не скрытая проверка в цикле.


# Резюме
Помимо прямого запрета недопустимых состояний, для снижения вероятности ошибок
я использовал также упрощение и унификацию интерфейса разных тензоров.
Иногда упрощение интерфейса наоборот приводит к увеличению количества проверок,
как было в случае номер 2.
Здесь нужен баланс.
В данном случае я считаю, что вполне допустимы проверкаи в конструкторах,
которые связывают "сырые" входные данные с более мощными абстракциями.

Некоторые решения (пункт 4) хороши с точки зрения теории, но их реализация
может всё испортить, если соответствующие абстракции плохо поддерживаются
конкретными инструментами.
Создавать сложные системы типов имеет смысл в компилируемых языках
со статической типизацией.
В Python все эти типы "доживут" до запуска программы и будут создавать
накладные расходы.
Стоит ли возможность отлова ошибок линтером таких затрат - вопрос, который
нужно решать отдельно в каждом конкретном случае.

Даже если забыть про Python, работа со сложными системами типов требует
совсем другого уровня понимания этой темы.
Разные операторы, применяемые к осям, дают разные типы, а их комбинации
дают ещё больше типов и т.д.
Хорошо бы как-то это всё упорядочить и автоматизировать, по аналогии с тем,
как это делается с преобразованиями пространства в знакомой мне теории групп.
Вероятно, в теории типов есть наработки по этой теме, но насколько хорошо
это всё поддерживается современными языками программирования?
