# Как правильно думать над моделью данных

## 1. Выводы по теории
Избыток (дублирование) информации усложняет реализацию
(особенно синхронизацию), но упрощает интерфейс для пользователей.

Здесь имеется в виду интерфейс в широком смысле - как спецификация,
включающая в себя не только формат доступа к данным,
но и гарантии сложности (скорости работы) отдельных операций.
Если у нас есть набор пар `(A, B)`,
то наличие словарей вида `A[B]` и `B[A]`
делает операции поиска по `A` и `B` одинаково быстрыми.
Если же есть только один словарь, то одна из операций в общем случае
будет существенно медленнее.

Каждая операция изменения должна поддерживать
инвариан согласованности словарей.
Тут важен баланс между сложностью кода и скоростью операций.
Время на синхронизацию тоже нужно учитывать.

Моё личное мнение:
производительность важнее простоты,
а надёжность важнее производительности.
Если мы можем обеспечить надёжность кода синхронизации
за счёт правильного проектирования и тестирования,
то стоит в него вложиться ради увеличения производительности.

В примере с двумя словарями возможен вариант,
когда один из них генерируется и кэшируется по запросу.
Это довольно сложный вариант, но он имеет преимущество,
когда большое количество операций записи
чередуется с большим количеством операций чтения.
В этом случае синхронизация при каждой записи нецелесообразна,
а кэширование ускорит чтение.


## 2. Информационная избыточность

### 2.1. Виды осей
```Python
class AxisKindTensor(Tensor):
    __axis_kind_map: Mapping[Axis, Set[Type[AxisKind]]]
    
    ...
    
    def axis_kinds(self, axis: Axis) -> Set[Type[AxisKind]]:
        return self.__axis_kind_map.get(axis, set())
```
Если хочется выбрать все оси определённого вида,
или сгруппировать их по кластерам придётся потрудиться.
Раз такие операции нужны часто, лучше сразу строить несколько словарей,
тем более, что объект всё равно иммутабельный,
а значит синхронизация нужна лишь один раз.
```Python
class AxisKindTensor(Tensor):
    __kind_mapping: "_KindMapping"
    
    ...

    def axis_kinds(self, axis: Axis) -> Set[Type[AxisKind]]:
        return self.__kind_mapping.axis_kinds(axis)
    
    def axes_of_kind(self, kind: Type[AxisKind]) -> Set[Axis]:
        return self.__kind_mapping.axes_of_kind(kind)
    
    def axis_kind_cluster(self, axis: Axis, kind: Type[AxisKind]) -> Hashable:
        return self.__kind_mapping.axis_kind_cluster(axis, kind)
    
    def axis_clusters_of_kind(
            self, kind: Type[AxisKind]) -> Mapping[Hashable, Set[Axis]]:
        return self.__kind_mapping.axis_clusters_of_kind(kind)


class _KindMapping:
    __axis_kind_map: Mapping[Axis, Set[Type[AxisKind]]]
    __kind_axis_map: Mapping[Type[AxisKind], Set[Axis]]
    __axis_clusters: Mapping[Axis, Mapping[Type[AxisKind], Hashable]]


    def __init__(self, data: Mapping[Axis, Set[AxisKind]]) -> None:
        self.__axis_kind_map = {}
        self.__kind_axis_map = {}
        self.__axis_clusters = {}
        for axis, kinds in data.items():
            types = set(map(type, kinds))
            assert len(types) == len(kinds)
            self.__axis_kind_map[axis] = types
            clusters = {}
            for kind in kinds:
                for k in _with_super_kinds(type(kind)):
                    self.__kind_axis_map[k] = \
                        self.__kind_axis_map.get(k, set()) | {axis}
                    clusters[k] = kind.cluster
            self.__axis_clusters[axis] = clusters
    
    ...
```


### 2.2.
```Python
class Params[T]:
    __mapping: Mapping[T, Set[Any]]

    def __init__(self, params: Mapping[T, Set[Any]]) -> None:
        self.__mapping = {k: v for k, v in params.items() if v}


    def find(self, pred: Callable[[Any], bool]) -> Mapping[T, Set[Any]]:
        found = {
            k: set(filter(pred, v))
            for k, v in self.__mapping.items()}
        return {k: v for k, v in found.items() if v}
    
    ...
```
Поиск сканирует весь словарь,
но его можно ускорить, так как элементы множества всегда `Hashable`:
```Python
class Params[T]:
    __mapping: Mapping[T, Set[Any]]
    __value_map: Mapping[Any, Set[T]]


    def __init__(self, params: Mapping[T, Set[Any]]) -> None:
        self.__mapping = {k: v for k, v in params.items() if v}
        self.__value_map = transpose_mapping(params)


    def find(self, pred: Callable[[Any], bool]) -> Mapping[T, Set[Any]]:
        return transpose_mapping({
            v: k for v, k in self.__value_map.items()
            if pred(v)})
    
    ...
```


### 2.3. Параметры тензора
```Python
class Tensor(MROChain, np.lib.mixins.NDArrayOperatorsMixin):
    __container: Container[Any, Axis]
    __params: Params[Axis]

    @property
    def params(self) -> Params[Axis]:
        return self.__params
    
    ...
```
У класса `Params` есть удобный метод `apply`,
который привязывает все параметры к осям.
Тут уже есть информационная избыточность,
так как размеры осей хранятся и в поле `__container`,
и в поле `__params`.
Из последнего их как раз удобно привязывать к осям,
но часто нужно привязать только размеры, или только не-размеры:
```Python
class Tensor(MROChain, np.lib.mixins.NDArrayOperatorsMixin):
    __container: Container[Any, Axis]
    __params: Params[Axis]

    @property
    def params(self) -> Params[Axis]:
        return self.__params
    
    @property
    def size_params(self) -> Params[Axis]:
        self.__cache_params()
        return self.__size_params
    
    @property
    def non_size_params(self) -> Params[Axis]:
        self.__cache_params()
        return self.__non_size_params
    
    def __cache_params(self):
        if hasattr(self, "_Tensor__size_params"):
            return
        rest, size = self.__params.extract(if_instance(SizeTag))
        self.__size_params = Params(size)
        self.__non_size_params = rest
```


### Выводы
Даже в таком небольшом проекте нашлось несколько мест,
где избыточная информация оказалась полезна.
Особенно хорошо получилось с тензором,
где она генерируется по запросу.
Вероятно, это было бы уместно и в случае с поиском параметров.

По замыслу, все эти объекты иммутабельны,
но кэшируемые свойства не меняют наблюдаемое поведение,
так что они не должны ничего поломать.


## Общие выводы
Более 20 лет назад в школе я изучал Pascal.
Программам было доступно всего 64кб памяти,
и нас приучали экономить на всём,
вплоть до использования царь-переменных,
которые меняли своё назначение на протяжении кода одной функции.
Теперь для меня куда важнее удобство интерфейсов,
которое увеличивает производительность
и снижает риск ошибок за счёт увеличения качества кода.
Да и физической памяти теперь уже по 64Гб и дома и на работе.

В общем случае, всё, что улучшает качество кода
на более высоких уровнях абстракции,
стоит усложнения и избыточности на низких уровнях абстракции.
Низкие уровни на то и низкие,
что там узкая специализация,
и код спрятан и хорошо локализован.
Лучше одна сложная функция,
чем дублирующийся избыточный код,
расползающийся по куче модулей.
