# Неочевидные проектные ошибки (2)

## 1. Сетка из графиков
Очень часто для построения графиков для статей используется подобный код:
```Python
from matplotlib import rcParams
rcParams["figure.figsize"] = [WIDTH_MM * INCHES_PER_MM, HEIGHT_MM * INCHES_PER_MM]
...
rcParams["figure.subplot.wspace"] = \
    NUM_COLS * midMarginW / (WIDTH_MM - leftMargin - rightMargin - (NUM_COLS - 1) * midMarginW)
rcParams["figure.subplot.hspace"] = \
    NUM_ROWS * midMarginH / (HEIGHT_MM - topMargin - bottomMargin - (NUM_ROWS - 1) * midMarginH)
...
for r in range(len(sourceParams)):
    for c in range(len(sourceParams[r])):
        subplot_index = NUM_COLS * r + c
        pp.subplot(NUM_ROWS, NUM_COLS, subplot_index)
        ...
```
Здесь в одном модуле перемешана логика построения графиков
и логика создания сетки.
Создание сетки - нетривиальная задача.
Нужно правильно задать расстояния между графиками (формулы в коде выше),
скрыть подписи осей у внутренних графиков и оставить их только по периметру,
сдвинуть подписи крайних делений, чтобы они не мешали соседям и т.п.

Логика построения сетки и осей я вынес в отдельный класс `GridFigure`,
который стал обёрткой для класса графика из `matplotlib`.
За построение графика отвечает потомок абстрактного класса `Figure`.
```Python
# Задаёт параметры внешнего вида, которые могут отличаться для разных журналов
class FigureStyle(ABC):
    @property
    @abstractmethod
    def tick_direction(self) -> str:
        assert False
    
    ...

# Строит график в заданных осях
class Figure(ABC):
    @abstractmethod
    def render(self, ax: PPAxes) -> None:
        assert False

# Содержит информацию об оси графика
class AxisData(NamedTuple):
    name: str
    values: list[float]

# Хранит сетку графиков
# Этот АТД - ограниченная версия двумерного массива графиков
# с двумя одномерными массивами данных осей.
# Сюда встроена проверка соответствия размеров массивов и значений индексов.
class Figures:
    ...

    def __init__(
            self,
            xaxis_data: list[AxisData],
            yaxis_data: list[AxisData],
            figures: list[list[Figure]],
            ) -> None:
        ...

...

# Размеры рисунка, поля и отступы
class Sizes(NamedTuple):
    figure: RectSizes
    margins: MarginSizes
    gaps: GapSizes

# Обёртка для рисунка из matplotlib
class GridFigure:

    ...

    def __init__(
            self,
            subfigures: Figures,
            sizes_mm: Sizes,
            style: FigureStyle,
            ) -> None:
        ...

    def save(self, file_name: str) -> None:
        ...

    def show(self) -> None:
        ...
```

Здесь логика настройки размеров и вида осей отделена от логики построения графиков
и скрыта за интерфейсом класса `GridFigure`.
Дополнительно действует неявное соглашение
(которое нужно отразить в документации),
о том, что метод `Figure.render` не должен перенастраивать оси,
хотя техническая возможность для этого есть.
Такой свободный доступ к осям сохранён, чтобы не ограничивать доступ к
функционалу `matplotlib` и не писать полноценную обёртку к этой библиотеке.

Конечно, в проектах большего масштаба желательно всё же сделать абстрактную
обёртку, чтобы не плодить зависимости от конкретной графической библиотеки в коде.


## 2. Сетка из графиков - вторая часть
Практика показала, что `FigureStyle` неимоверно разрастается, и передаётся
в качестве параметра где ни попадя.

Было решено сделать его не просто хранилищем значений, а поставщиком методов для
модификации графиков.
```Python
# Это стандартное поведение
# Класс-потомок может переопределить методы, чтобы изменить внешний вид графиков
class FigureStyler:
    @property
    def font_sizes_pt(self) -> FontSizes:
        return FontSizes(8, 9, 10)

    @property
    def axis_width_mm(self) -> float:
        return 0.25

    # Логика обработки графика разная в зависимости от его положения в сетке
    # Для разных положений - разные методы

    # Этот метод применяется первым к каждому графику
    def adjust_axes(self, ax: PPAxes, xaxis_data: AxisData, yaxis_data: AxisData) -> None:
        ax.tick_params(
            direction="in",
            labelsize=self.font_sizes_pt.small)
        self.__adjust_spines(ax)
        ax.set_xlim(xaxis_data.values[0], xaxis_data.values[-1])
        ax.set_xticks(xaxis_data.values)
        ax.set_ylim(yaxis_data.values[0], yaxis_data.values[-1])
        ax.set_yticks(yaxis_data.values)

    def adjust_bottom_axes(self, ax: PPAxes, xaxis_data: AxisData) -> None:
        ax.set_xlabel(xaxis_data.name, size=self.font_sizes_pt.medium)
        self.__align_xticklabels(ax)

    def adjust_not_bottom_axes(self, ax: PPAxes, xaxis_data: AxisData) -> None:
        ax.set_xlabel("")
        ax.set_xticklabels([])

    def adjust_left_axes(self, ax: PPAxes, yaxis_data: AxisData) -> None:
        ax.set_ylabel(yaxis_data.name, size=self.font_sizes_pt.medium)
        self.__align_yticklabels(ax)

    def adjust_not_left_axes(self, ax: PPAxes, yaxis_data: AxisData) -> None:
        ax.set_ylabel("")
        ax.set_yticklabels([])

    def __adjust_spines(self, ax: PPAxes):
        for name in ["left", "right", "top", "bottom"]:
            ax.spines[name].set_linewidth(self.axis_width_mm * PT_PER_MM)

    def __align_xticklabels(self, ax: PPAxes):
        t = ax.xaxis.get_major_ticks()
        t[0].label1.set_horizontalalignment("left")
        t[-1].label1.set_horizontalalignment("right")

    def __align_yticklabels(self, ax: PPAxes):
        t = ax.yaxis.get_major_ticks()
        t[0].label1.set_verticalalignment("bottom")
        t[-1].label1.set_verticalalignment("top")
...

class GridFigure:

    ...

    def __init__(
            self,
            subfigures: Figures,
            sizes_mm: Sizes,
            styler: FigureStyler,
            ) -> None:
        ...
        self.__render_subfigures(subfigures)
    
    ...
    
    def __render_subfigures(self, figures: Figures):
        for row in range(figures.nrows):
            for col in range(figures.ncols):
                figure = figures.get_figure(row, col)
                ax = self.__axs[row][col]
                figure.render(ax)
                # Применяем общий стиль
                self.__styler.adjust_axes(
                    ax,
                    figures.get_xaxis_data(col),
                    figures.get_yaxis_data(row))
                # Применяем стили в зависимости от положения
                # TODO: надо придумать как избавиться от `else`
                if row == figures.nrows - 1:
                    self.__styler.adjust_bottom_axes(ax, figures.get_xaxis_data(row))
                else:
                    self.__styler.adjust_not_bottom_axes(ax, figures.get_xaxis_data(row))
                if col == 0:
                    self.__styler.adjust_left_axes(ax, figures.get_yaxis_data(row))
                else:
                    self.__styler.adjust_not_left_axes(ax, figures.get_yaxis_data(row))
```

Доступа к осям стало больше и появилось ещё одно неявное разграничение:
настройка внешнего вида в `FigureStyler`, отображение данных в `Figure`.


## 3. Построение локальной нормальной формы Смита
Алгоритм из [диссертации одного американского учёного](https://escholarship.org/uc/item/4qj976xg).
Он применяется к матричным многочленам -
АТД в моём проекте, для которого определён ряд арифметических операций.
```Python
def smith(a, factor, atol=1e-12):
    size = a.shape[0]
    inv_right_matrix = ArrayPoly(np.eye(size, dtype=np.common_type(a.coefs, factor.coefs))[np.newaxis])
    remainder_matrix = ArrayPoly(np.zeros_like(inv_right_matrix.coefs))
    factor_powers = [ArrayPoly(1)]
    diag_factor_exponents = np.zeros(size, dtype=int)
    column = 0
    exponent = 0
    while column < size:
        for j in range(0, size - column):
            # subsequent // and % operations is essential part of the algorithm
            # we extract the terms with specific power of factor
            column_vector = a @ inv_right_matrix[:, column : column + 1]
            higher_pow_coef = column_vector // factor_powers[exponent]
            remainder_matrix[:, column : column + 1] = higher_pow_coef % factor
            del column_vector, higher_pow_coef
            expansion_coefs = expandLast(remainder_matrix[:, : column + 1], atol)
            is_lin_indep_columns = expansion_coefs is None
            if is_lin_indep_columns:
                diag_factor_exponents[column] = exponent
                column += 1
            else:
                for m in range(0, column):
                    inv_right_matrix[:, column] -= \
                        factor_powers[exponent - diag_factor_exponents[m]] * \
                        expansion_coefs[m] * \
                        inv_right_matrix[:, m]
                inv_right_matrix.coefs[..., column:] = \
                    np.roll(inv_right_matrix.coefs[..., column:], shift=-1, axis=-1)
        exponent += 1
        factor_powers.append(factor_powers[-1] * factor)
    del column, exponent

    left_matrix = a @ inv_right_matrix
    # multiply by inverse diagonal part of local normal Smith form
    for column in range(size):
        left_matrix[:, column] //= factor_powers[diag_factor_exponents[column]]
    return trim(inv_right_matrix, atol), trim(left_matrix, atol), diag_factor_exponents
```
Трудность в том, что к матрицам `inv_right_matrix` и `remainder_matrix`
применяется ряд нетривиальных операций, в которых легко ошибиться,
и смысл которых из кода не виден.

Фактически, на каждом шаге мы берём столбец из одной матрицы и,
в зависимости от результата вычислений с ним,
сохраняем его, или меняем.
При этом `inv_right_matrix` является и источником и приёмником столбцов,
а одни и те же столбцы матрицы `remainder_matrix`
перезаписываются по несколько раз.
Всё это не очень хорошо, потому что одни и те же структуры данных используются
для исходных данных, промежуточных результатов и сохранения ответа.
Три вложенных цикла и условие - это совсем некрасиво.

Чтобы исправить ситуацию - используем специализированные АТД:
очередь столбцов и матрица, формируемая как список столбцов
(без команды удаления, но с запросами для некоторых вычислений).
```Python
# Collects columns added to the right side
class ColumnCollector(Status):

    _nrows: int
    _data: list[ArrayPoly]
    
    # CONSTRUCTOR
    # Create empty collector
    def __init__(self, nrows: int) -> None:
        super().__init__()
        self._nrows = nrows
        self._data = []


    # COMMANDS

    # Add column to the right
    # PRE: `column` is Nx1 polynomial matrix
    # PRE: `column` height matches `nrows`
    # POST: `column` is added to the right end of the queue
    @status("OK", "NOT_COLUMN", "SIZE_MISMATCH")
    def push_right(self, column: ArrayPoly) -> None:
        ...


    # QUERIES

    # Check if queue is empty
    def is_empty(self) -> bool:
        return len(self._data) == 0


# Allows adding columns to the right side and getting/removing them from the left
class ColumnQueue(ColumnCollector):

    # CONSTRUCTOR
    # Create empty queue
    def __init__(self, nrows: int) -> None:
        super().__init__(nrows)

    
    # COMMANDS

    # Remove the left column 
    # PRE: queue is not empty
    # POST: left column removed
    @status("OK", "EMPTY")
    def pop_left(self) -> None:
        ...
    
    # QUERIES

    # Get left column
    # PRE: queue is not empty
    @status("OK", "EMPTY")
    def get_left(self) -> ArrayPoly:
        ...


# Column collector with some calculation stuff
class ExtendibleMatrix(ColumnCollector):

    # CONSTRUCTOR
    # Create empty matrix
    def __init__(self, nrows: int) -> None:
        super().__init__(nrows)


    # QUERIES
    
    # Get columns as matrix
    # PRE: collector is not empty
    @status("OK", "EMPTY")
    def get_matrix(self) -> ArrayPoly:
        ...
    
    # Expand given column over matrix columns
    # PRE: matrix is not empty
    # PRE: `column` size fits matrix
    # PRE: `column` is complanar with matrix columns
    @status("OK", "INVALID_COLUMN", "EMPTY", "NOT_COMPLANAR")
    def expand_column(self, column: ArrayPoly, atol: float = 1e-12) -> list[Any]:
        ...

    # Make linear combination of columns with given coefficients
    # PRE: matrix is not empty
    # PRE: `factors` size fits number of columns
    @status("OK", "EMPTY", "SIZE_MISMATCH")
    def combine_columns(self, factors: list[Any]) -> ArrayPoly:
        ...
```
Используем наследование, чтобы избежать дублирование кода.

Теперь можно переписать алгоритм.
```Python
def smith(a, factor, atol=1e-12):
    size = a.shape[0]
    inv_right_matrix = ExtendibleMatrix(size)
    remainder_matrix = ExtendibleMatrix(size)
    seed_matrix = ArrayPoly(np.eye(size, dtype=np.common_type(a.coefs, factor.coefs))[np.newaxis])
    seed_columns = ColumnQueue(size)
    for i in range(size):
        seed_columns.push_right(seed_matrix[:, i : i + 1])
    factor_powers = [ArrayPoly(1)]
    diag_factor_exponents = []
    exponent = 0
    new_seed_columns = ColumnQueue(size)
    while not (seed_columns.is_empty() and new_seed_columns.is_empty()):
        if seed_columns.is_empty():
            exponent += 1
            factor_powers.append(factor_powers[-1] * factor)
            seed_columns, new_seed_columns = new_seed_columns, seed_columns
        seed_column = seed_columns.get_left()
        seed_columns.pop_left()
        # subsequent // and % operations is essential part of the algorithm
        # we extract the terms with specific power of factor
        remainder_column = (a @ seed_column) // factor_powers[exponent] % factor
        if is_zero(remainder_column, atol):
            new_seed_columns.push_right(seed_column)
            continue
        expansion_coefs = remainder_matrix.expand_column(remainder_column)
        if remainder_matrix.is_status("expand_column", "EMPTY") \
                or remainder_matrix.is_status("expand_column", "NOT_COMPLANAR"):
            inv_right_matrix.push_right(seed_column)
            remainder_matrix.push_right(remainder_column)
            diag_factor_exponents.append(exponent)
            continue
        assert remainder_matrix.is_status("expand_column", "OK")
        assert not inv_right_matrix.is_empty()
        expansion_factor_powers = [factor_powers[exponent - dfe] for dfe in diag_factor_exponents]
        coefs = [ec * efp for ec, efp in zip(expansion_coefs, expansion_factor_powers)]
        new_seed = seed_column - inv_right_matrix.combine_columns(coefs)
        new_seed_columns.push_right(new_seed)

    inv_right_matrix = inv_right_matrix.get_matrix()
    left_matrix = a @ inv_right_matrix
    # multiply by inverse diagonal part of local normal Smith form
    for column in range(size):
        left_matrix[:, column] //= factor_powers[diag_factor_exponents[column]]
    return trim(inv_right_matrix, atol), trim(left_matrix, atol), np.array(diag_factor_exponents)
```
Один цикл вместо трёх!
Один спрятан в АТД, а ещё один больше не нужен благодаря использованию очердей и списков.
Плюс доступ по индексу в основной части алгоритма больше не используется.

Получилось длинее, чем без АТД, но код стал почти линейным.
Мы берём столбцы из `seed_columns` и либо временно откладываем их в `new_seed_columns`,
либо сохраняем результаты вычислений в `inv_right_matrix` и `remainder_matrix`.
Можно ещё сократить, если добавить новый слой АТД и вынести туда часть логики.

Граница здесь явная - в интерфейсе АТД.
Низкоуровневые операции скрыты внутри методов АТД, а основной алгоритм
перекладывает столбцы между ними и запускает вычисления.
