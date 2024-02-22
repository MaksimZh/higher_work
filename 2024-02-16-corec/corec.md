# Как проектировать программы in small

## 1. Рефлексия по теории
После начала изучения ФП я стал часто использовать рекурсию вместо циклов.
Временами из-за этого получался более объёмный код, чем в императивном стиле,
особенно если сразу делать хвостовую рекурсию.
Главная причина этого, видимо, в том, что я пытался сразу решить всю задачу
одной рекурсивной функцией, даже если в ней сразу несколько подзадач
(т.е. сложная структура выходных данных, как несколько списков, например).
В теории рекомедуется разделять обработку сложных данных на несколько функций,
и ещё пробовать ориентироваться не только на входные данные,
но и на выходные и на промежуточные.
Пришло время расширить набор используемых инструментов.


## 2. Работа с кодом

## 2.1 Упаковка массива в тензор
```Python
class SimpleTensor[A: BaseAxis]:
    ...
    
    def __init__(
            self, array: NDArray[Any], sizes: dict[A, int],
            *patterns: AxisPattern[A]):
        # Вызов рекурсивной функции:
        wrap_data = _eval_wrap(sizes, array.shape, patterns)
        self.__array = array.reshape(wrap_data.reshape_sizes)
        self.__axis_indices = wrap_data.axis_indices
```
В старой версии использовалась рекурсивная функция,
причём ни формат входных, ни формат выходных данных не были рекурсивными
по своей логике (хотя это и списки).
Эта функция обрабатывала сразу два списка (`shape` и `patterns`),
причём их взаимодействие было нетривиальным, т.е. нельзя было работать
сразу с `zip(shape, patterns)`.
```Python
class SimpleTensor[A: BaseAxis]:
    ...

    def __init__(
            self, array: NDArray[Any], sizes: dict[A, int],
            *patterns: AxisPattern[A]):
        if SimpleTensor._dimension_number(patterns) != array.ndim:
            raise DimensionsNumberError
        # A -> распаковка добавлений осей -> B
        shape_pattern_pairs = \
            SimpleTensor._calc_pattern_shapes(array.shape, patterns)
        # B -> распаковка разбиений осей -> C
        shape_axis_pairs = \
            SimpleTensor._calc_axis_shapes(sizes, shape_pattern_pairs)
        # C -> разделение размеров и осей -> D
        shape, axes = SimpleTensor._unpack_shape_axes(shape_axis_pairs)
        self.__array = array.reshape(shape)
        self.__axis_indices = {ax: i for i, ax in enumerate(axes)}
```
В новой версии используется сразу несколько промежуточных
представлений данных (B, C, D).
Переходы между ними настолько простые,
что явная рекурсия вообще не понадобилась:
оказалось достаточно функций высокого порядка
и инструментов из стандартной библиотеки.
Раньше все эти шаги делались сразу для каждого элемента входного списка,
и рекурсивная функция выглядела страшновато.

В новой версии использовалась только одна действительно нетривиальная функция,
которую разберём в следующем разделе.


## 2.2 Объединение двух последовательностей на основе условия
Нужно сформировать последовательность,
из элементов `if_true` и `if_false` в соответствии со значениями в `pred`.

Первое, что пришло в голову:
```Python
def select_items[A, B](
        pred: Iterable[bool],
        if_true: Iterable[A],
        if_false: Iterable[B]) -> Iterable[A | B]:
    dest = list[A | B]()
    it_true = iter(if_true)
    it_false = iter(if_false)
    try:
        for p in pred:
            source = it_true if p else it_false
            dest.append(next(source))
    except StopIteration:
        return dest
    return dest
```
Попытка решить вопрос с помощью рекурсии и pattern matching
(без мутабельного списка и исключений) была неудачной:
```Python
def select_items[A, B](
        pred: Iterable[bool],
        if_true: Iterable[A],
        if_false: Iterable[B]) -> Iterable[A | B]:
    match pred, if_true, if_false:
        # Результат начинается с головы if_true если pred начинается с True
        case [True, *p_tail], [head, *tail], other:
            return head, *select_items(p_tail, tail, other)
        # Результат начинается с головы if_false если pred начинается с False
        case [False, *p_tail], other, [head, *tail]:
            return head, *select_items(p_tail, other, tail)
        # Результат пустой, если не хватает голов (т.е., в остальных случаях)
        case _:
            return ()
```
Python - это не Haskell или F#,
и он не может разбить бесконечную последовательность на голову и хвост.
Код выше работает только для конечных контейнеров, а мне нужно для любых.

Наверное, самый "питоновский" способ - через генераторы:
```Python
def select_items[A, B](
        pred: Iterable[bool],
        if_true: Iterable[A],
        if_false: Iterable[B]) -> Iterable[A | B]:
    it_true = iter(if_true)
    it_false = iter(if_false)
    for p in pred:
        try:
            yield next(it_true if p else it_false)
        except StopIteration:
            return
```
Опять рекурсии не получилось.
Зато функция стала короче и проще.


# 2.3 Распаковка массива из тензора
```Python
class SimpleTensor[A: BaseAxis]:
    ...
    
    @final
    def unwrap(self, *patterns: NestIter[AxisPattern[A]]) -> NDArray[Any]:
        # Вызов рекурсивной функции
        unwrap_data = _eval_unwrap(
            self.__axis_indices, self.__array.shape, patterns)
        return self.__array \
            .transpose(unwrap_data.transpose_indices) \
            .reshape(unwrap_data.reshape_sizes)
```
Снова рекурсия появилась из любви к ФП и рекурсивного характера
входных данных.
Рекурсивный тип входных данных - это для удобства пользователя,
лучше сразу избавиться от этих сложностей,
перейдя к линейному промежуточному представлению (`plain_patterns`):
```Python
@final
def unwrap(self, *patterns: NestIter[AxisPattern[A]]) -> NDArray[Any]:
    # Распаковываем рекурсивные входные данные
    plain_patterns = unwrap_iterables(patterns)
    # Проверяем на дубликаты
    axes = tuple(self._get_axes(plain_patterns))
    if len(axes) > len(set(axes)):
        raise DuplicateAxisError(axes)
    # Вычисляем индексы
    indices = tuple(self._get_indices(plain_patterns))
    # Вычисляем размеры
    shape = tuple(self._get_shapes(plain_patterns))
    return self.__array.transpose(indices).reshape(shape)
```
Здесь нам нужны индексы и размеры, и теперь они вычисляются отдельно.
В каком-то смысле, это выходные данные, только мы их сразу используем,
а не возвращаем.

В новой версии вместо одной сложной рекурсивной функции вызывается
несколько простых, например:
```Python
def _get_indices(self, patterns: Iterable[AxisPattern[A]]) -> Iterable[int]:
    
    def check_and_get_index(ax: A) -> int:
        if ax not in self.__axis_indices:
            raise AxisNotFoundError(ax)
        return self.__axis_indices[ax]

    for p in patterns:
        if isinstance(p, BaseAxis):
            yield check_and_get_index(p)
            continue
        if isinstance(p, AxisAdd):
            continue
        assert isinstance(p, AxisMerge)
        yield from self._get_indices(p.axes)
```
Это не вполне классическая рекурсия: максимальная глубина равна единице,
поскольку `AxisMerge` не может содержать вложенных `AxisMerge`
(это запрещено на уровне типов).
Данная функция следует за типом выходных данных и была бы ко-рекурсивной,
если бы этот тип был рекурсивным.
Однако, выходные данные - это последовательность, и поэтому функция выполнена
как генератор.


### Рефлексия по работе с кодом
Ни одной по-настоящему ко-рекурсивной функции не получилось.
Удалось только заметной упростить код разбив большие функции,
которые делали всё и сразу,
на не сколько маленьких, которые преобразуют данные
между промежуточными представлениями,
либо вычисляют что-то одно.

Такой подход кажется не оптимальным с точки зрения выполнения,
но он удобен для понимания кода,
а больших списков осей тензоров всё равно не ожидается.
В оси тензоров отображается логика предметной области и стратегии вычислений,
и поэтому они помещаются на листе бумаги, а иногда даже в голове человека.
Пока понадобились только тензоры максимум 8-го ранга.

Вероятно, отсутствие настоящей ко-рекурсии связано с тем, что в моём проекте
не так много действительно глубоких рекурсивных типов данных.
Последовательности (в частности, списки и кортежи) в Python не принято
обрабатывать рекурсивно, в отличие от функциональных языков.
Одна из трудностей - то, что у итераторов нет проверки на пустоту,
только генерация специального исключения
при попытке получить следующий элемент.
Мне это очень не нравится, но таков уж дизайн.


## Рефлексия
Вот и пополнилась моя копилка ещё парой инструментов, и очень вовремя.
Моё увлечение ФП привело к использованию рекурсии ради рекурсии даже там,
где можно было обойтись более простыми решениями.
Аналогия с молотком тут очень удачная - всё кажется гвоздями.

Наибольшие результаты в плане упрощения кода приносит введение промежуточных
состояний.
Это похоже на конвеер - каждая функция делает простое действие
и передаёт результат следующей,
вместо того, чтобы попытаться сделать всё и сразу.
Благодаря этому можно, например, сразу распаковать
рекурсивные (для удобства пользователя) входные данные
в линейную (для удобства обработки) структуру,
и все остальные функции радикально упрощаются,
сводясь чуть ли не к map/reduce.
