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
        shape, axes = SimpleTensor._unpack_shape(shape_axis_pairs)
        self.__array = array.reshape(shape)
        self.__axis_indices = {ax: i for i, ax in enumerate(axes)}
```
В новой версии используется сразу несколько промежуточных
представлений данных.
При этом явная рекурсия здесь не нужна:
достаточно простых линейных операций над списками.



### Рефлексия по работе с кодом


## Рефлексия
