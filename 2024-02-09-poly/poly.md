# Повышаем полиморфность кода

## 1. Выводы по изучению материла
Утверждение о том, что полиморфность уменьшает количество степеней свободы
контринтуитивно, но истинно.
Можно вместо "полиморфность" подставить слово "абстрактность",
тогда всё становится понятно.
Абстрактные сущности имеют меньше возможностей, и следовательно -
меньше степеней свободы.
Что более ценно, они имеют меньше причин для изменения,
поэтому, более полиморфный (абстрактный) код более устойчив.

Здесь сразу два позитивных момента.
Первое - меньше свободы и возможности что-то испортить.
Второе - меньше возможных причин для изменения кода.


## 2. Работа с кодом

### 2.1
```Python
def assume_single[T](source: set[T] | frozenset[T]) -> T:
    assert len(source) == 1
    return next(iter(source))
```
Вместо множеств можно использовать любой контейнер.
```Python
def single_value[T](source: Iterable[T]) -> T:
    match tuple(source):
        case (val,):
            return val
        case _:
            assert False
```


### 2.2
```Python
def all_single_values(source: dict[Any, set[Any]]) -> bool:
    return all(len(v) == 1 for v in source.values())
```
Вместо словаря множеств - любой контейнер вида ключ-значение,
в котором значения имеют размер.
```Python
def all_single_values(source: Mapping[Any, Sized]) -> bool:
    return all(len(v) == 1 for v in source.values())
```


### 2.3
```Python
def assume_single_values[K, V](source: dict[K, set[V]]) -> dict[K, V]:
    return {k: assume_single(v) for k, v in source.items()}
```
Вместо словаря множеств - любой контейнер вида ключ-значение,
в котором значения являются контенерами.
```Python
def assume_single_values[K, V](source: Mapping[K, Iterable[V]]) -> dict[K, V]:
    return {k: single_value(v) for k, v in source.items()}
```


### 2.4
```Python
def add[A: BaseAxis](*axes: NestIter[A]) -> tuple[AxisPattern[A], ...]:
    if not axes:
        return ()
    if isinstance(axes[0], BaseAxis):
        return (+axes[0],) + add(*axes[1:])
    assert isinstance(axes[0], Iterable)
    return add(*axes[0], *axes[1:])
```
Возвращаем не кортеж, а контейнер, и кстати, рекурсия больше не нужна,
благодаря введению полиморфной функции `unwrap_iterables`,
которая распаковывает любые вложенные контейнеры.
```Python
def add[A: BaseAxis](*axes: NestIter[A]) -> Iterable[AxisPattern[A]]:
    return tuple(+axis for axis in unwrap_iterables(axes))
```


### 2.5
```Python
class Tensor(SimpleTensor[Axis]):
    ...

    def __init__(
            self,
            array: NDArray[Any],
            *patterns: AxisPatternArg):
        axis_data = _collect_params(patterns)
        params = self.__prepare_params(axis_data.params).ready
        sizes = assume_single_values(params.by_type(int))
        super().__init__(array, sizes, *axis_data.axis_patterns)
        self.__params = params
        self.__post_init()


def _collect_params(
        patterns: tuple[AxisPatternArg, ...]
        ) -> _CollectData:
    return _rec_collect_params(patterns, _CollectData())

def _rec_collect_params(
        patterns: tuple[AxisPatternArg, ...],
        data: _CollectData) -> _CollectData:
    if len(patterns) == 0:
        return data
    if isinstance(patterns[0], Axis):
        ...
    if isinstance(patterns[0], ParamAxis):
        ...
    if isinstance(patterns[0], AxisAdd):
        ...
    if isinstance(patterns[0], AxisMerge):
        ...
    assert isinstance(patterns[0], Iterable)
    ...
```
Раньше нужна была рекурсия, которая отвечала
и за итерации по элементам кортежа, и за распаковку вложенных контейнеров.

Теперь мы используем аналог функторов в смысле ФП - это контейнеры,
поддерживающие протокол `Structured`, который содержит два метода:
для распаковки и упаковки элементов.
Теперь можно применять произвольные функции
к произвольным структурированным контейнерам.
```Python
class Structured[T](Protocol):
   
    def struct_unwrap(self) -> Iterable[T]:
        ...

    @classmethod
    def struct_wrap[N](cls, items: Iterable[N]) -> "Structured[N]":
        ...

def struct_map[S, D](
        func: Callable[[S], D], src: Iterable[S | Structured[S]]
        ) -> Iterable[D | Structured[D]]:
    ...

def struct_acc_map[A, S, D](
        func: Callable[[A, S], tuple[A, D]],
        seed: A, src: Iterable[S | Structured[S]],
        ) -> tuple[A, Iterable[D | Structured[D]]]:
    ...
```
Далее, мы превращаем `AxisAdd` и `AxisMerge` в структурированные контейнеры
и убираем рекурсию с кучей веток, экономя десятки строк кода.
```Python
class Tensor(SimpleTensor[Axis]):
    ...

    def __init__(
            self,
            array: NDArray[Any],
            *patterns: AxisPatternArg):
        
        def collect(
                params: AxisParams, axis: Axis | ParamAxis
                ) -> tuple[AxisParams, Axis]:
            return (params, axis) if isinstance(axis, Axis) \
                else (params << axis, axis.pure)

        axis_patterns: Iterable[AxisPattern[Axis]]
        user_params, axis_patterns = \
            struct_acc_map( #type: ignore
                collect, AxisParams(),
                unwrap_iterables(patterns))
        params = self.__prepare_params(user_params).ready
        sizes = assume_single_values(params.by_type(int))
        super().__init__(array, sizes, *axis_patterns)
        self.__params = params
        self.__post_init()
```


### Выводы по работе с кодом
