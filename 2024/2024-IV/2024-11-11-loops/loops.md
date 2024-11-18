# О циклах по умному

## 1. Теория
Несколько лет назад увидел в одной статье такую фразу:
"Циклы в вашей программе - это баги".
Тогда я её не понял, но предложенная там же идея заменять циклы
на функциональные конструкции типа `map`-`reduce` мне понравилась.

Цикл, зачастую, маскирует замысел разработчика
под не самой простой синтаксической конструкцией,
особенно если он работает с изменяемым состоянием.
При чтении такого кода нужно отклоняться от линейной последовательности,
нужно понимать, что состояние на входе в тело цикла
может быть изменено в предыдущих итерациях.
А на самом деле мы просто хотели максимальное значение из списка.

Понятно, что для простых конструкций типа `min` и `max`
в большинстве современных языков есть функции в стандартной библиотеке,
и для них циклы пишутся, разве что, в учебных целях.
Есть более сложные конструкции, реализующие логику,
которая не обязательно является универсальной,
а может быть характерна только для данного проекта.
Лучше бы такие вещи оборачивать в функции с говорящими названиями,
даже если что-то встречается в коде (пока) только в одном месте.

Чаще всего, однако, цикл это `reduce` в той или иной форме.
Чисто формально, `map`, `filter` и т.п. - частные случаи `reduce`,
где копится новая последовательность.


## 2. Практика

### 2.1. Много данных - один тест
```Python
...
for a, b in (
        (o, o),
        (x, o),
        (x, x),
        (x, y),
        (y, x),
        ):
    self.assertEqual(T(a) - b, T(a) - T(b))
```
Казалось бы, что такого?
Просто один и тот же тест применяется к разным комбинациям исходных данных.
Только цикл с его возможностями доступа к контексту и изменению состояний -
это слишком мощный инструмент для таких действий,
и слишком непонятный.
Даже цепочка из `assert`ов была бы нагляднее.

Здесь ситуация усугубляется тем, что заголовок цикла имеет сложную структуру,
для понимания которой нужно прочитать тело, то есть,
читать код нужно задом наперёд.
С этим помогла бы функция типа `Seq.iter action source` из F#,
потому что там `action` идёт перед `source`,
и сразу видно что делаем, и тогда понятно как парсится список кортежей.
В Python нет аналога, потому что `map` - ленивая функция,
а тут нужна жадная, или будет некрасиво.

После небольшой подготовки
```Python
def iterate[T](action: Callable[[T], None], source: Iterable[T]) -> None:
    for s in source:
        action(s)


class XTestCase(unittest.TestCase):

    def assertSameResults[S, R](
            self,
            a: Callable[[S], R],
            b: Callable[[S], R],
            source: Iterable[S]
            ):
        iterate(
            lambda s: self.assertEqual(a(s), b(s)),
            source)
```
можно сделать так:
```Python
self.assertSameResults(
    lambda v: T(v[0]) - v[1],
    lambda v: T(v[0]) - T(v[1]),
    (
        (o, o),
        (x, o),
        (x, x),
        (x, y),
        (y, x),
    ))
```
К сожалению, в Python 3 нет автоматической распаковки кортежей аргументов,
а то можно было бы писать `lambda a, b: ...`.


### 2.2. Много данных - много тестов
Если взглянуть на ситуацию шире, то у нас тут выше
ещё один неявный цикл по тому же набору данных:
```Python
self.assertEqual(T(o) - T(o), T(o))
self.assertEqual(T(x) - T(o), T(x))
self.assertEqual(T(x) - T(x), T(o))
self.assertEqual(T(x) - T(y), T(
    {1: {B(11)}, 2: {B(12), C(13)}}))
self.assertEqual(T(y) - T(x), T(
    {1: {C(15)}, 2: AAA(16), 3: C(17)}))

self.assertSameResults(
    lambda v: T(v[0]) - v[1],
    lambda v: T(v[0]) - T(v[1]),
    (
        (o, o),
        (x, o),
        (x, x),
        (x, y),
        (y, x),
    ))
```
Можно объединить данные в один набор и...
```Python
test: tuple[ParamMapping3, ...] = (
    (o, o, o),
    (x, o, x),
    (o, x, o),
    (x, x, o),
    (
        x, y,
        {1: {B(11)}, 2: {B(12), C(13)}}),
    (
        y, x,
        {1: {C(15)}, 2: AAA(16), 3: C(17)}),
)

self.assertSameResults(
    lambda v: T(v[0]) - T(v[1]),
    lambda v: T(v[2]),
    test)

self.assertSameResults(
    lambda v: T(v[0]) - v[1],
    lambda v: T(v[0]) - T(v[1]),
    map(lambda v: v[:2], test))
```
или даже...
```Python
def assertSameResults[S, R](
        self,
        *func: Callable[[S], R],
        source: Iterable[S]
        ):
    assert len(func) > 0
    def action(s: S):
        sample = func[1](s)
        iterate(
            lambda f: self.assertEqual(f(s), sample),
            func[1:])
    iterate(action, source)

...

self.assertSameResults(
    lambda v: T(v[0]) - T(v[1]),
    lambda v: T(v[2]),
    lambda v: T(v[0]) - v[1],
    source = cast(Iterable[ParamMapping3], (
        (o, o, o),
        (x, o, x),
        (o, x, o),
        (x, x, o),
        (
            x, y,
            {1: {B(11)}, 2: {B(12), C(13)}}),
        (
            y, x,
            {1: {C(15)}, 2: AAA(16), 3: C(17)}),
        )))
```


### 2.3. Пригодилась
```Python
for x in reversed(type(self).__call_chain(method_name)):
    x(self)
```
Вот и пригодилась новая функция `iterate`:
```Python
iterate(
    lambda f: f(self),
    source = reversed(type(self).__call_chain(method_name)))
```
Такая запись делает замысел очевидным:
выполнить действие для каждого элемента последовательности в обратном порядке.


### 2.4. Школьный подход
```Python
def _parse_slices(args: Sequence[SAxis]) -> _SliceInfo:
    axes = list[Axis]()
    slices = list[int | Slice]()
    sliced_axes = list[Axis]()
    for s in args:
        axes.append(s.target)
        slices.append(s.arg)
        if not isinstance(s.arg, int):
            sliced_axes.append(s.target)
    return _SliceInfo(tuple(axes), tuple(slices), tuple(sliced_axes))
```
Нас в школе так учили: для оптимизации всё нужно засунуть в один цикл.
Но здесь оптимизация не нужна. Это далеко не самое узкое место в программе.
Куда лучше позаботиться о наглядности кода.
```Python
def _parse_slices(args: Sequence[SAxis]) -> _SliceInfo:
    return _SliceInfo(
        axes = tuple(a.target for a in args),
        slices = tuple(a.arg for a in args),
        sliced_axes = tuple(
            a.target for a in args
            if not isinstance(a.arg, int)))
```
Теперь каждый элемент вычисляется независимо от других.


### 2.5. Словарь словарей
Здесь создаётся двухуровневый словарь,
в котором внешний ключ зависит от значений во входном словаре:
```Python
def __init_keys(
            self,
            source: Mapping[K, Parameter | Set[Parameter]]
            ) -> None:
    params = dict[Type[Parameter], MutableMapping[K, Parameter]]()
    for k, ps in source.items():
        pars = ps if isinstance(ps, Set) else {ps}
        for p in pars:
            tp = _root_type(type(p))
            if tp not in params:
                params[tp] = {}
            if k in params[tp]:
                raise ParameterError(
                    f"Parameter conflict at {k}: " + \
                    f"{params[tp][k]} vs {p}")
            params[tp][k] = p
    self.__params = params
```
Сначала не хотел с этим куском связываться:
тут в цикле закодирована довольно сложная логика.
Потом подумал: как раз поэтому и нужно его упростить,
тут цикломатическая сложность слишком высока.

Можно убрать все циклы, используя стандартные операции со словарями и списками:
```Python
def __init_keys(
        self,
        source: Mapping[K, Parameter | Set[Parameter]]
        ) -> None:
    key_param = chain.from_iterable(
        zip(repeat(k), _ensure_set(v))
        for k, v in source.items())
    root_groups = group_by_first(
        (_root_type(type(p)), (k, p))
        for k, p in key_param)
    root_key_groups = {
        r: group_by_first(v)
        for r, v in root_groups.items()}
    conflicts = {
        k: p
        for v in root_key_groups.values()
        for k, p in v.items()
        if len(p) > 1}
    if conflicts:
        raise ParameterError(f"Parameter conflicts: {conflicts}")
    self.__params = {
        r: {k: assume_single_value(p) for k, p in v.items()}
        for r, v in root_key_groups.items()}
```
Один цикл всё же остался внутри `group_by_first`:
```Python
def group_by_first[K, V](
        source: Iterable[tuple[K, V]]
        ) -> Mapping[K, Sequence[V]]:
    dest = dict[K, list[V]]()
    for k, v in source:
        if k not in dest:
            dest[k] = []
        dest[k].append(v)
    return dest
```
У этой функции нет аналогов в стандартной библиотеке Python,
и её реализация через `reduce` на этом языке была бы слишком громоздкой.


## Выводы
Преобразование циклов к `map`-`reduce` возможно в любом случае.
Иногда, правда, результат может оказаться хуже исходного кода,
особенно в императивных языках.
Пример - функция `group_by_first` в 2.5.
Это, конечно, не означает, что такие циклы не нужно трогать.
Их как раз желательно вытащить в чистом виде в отдельные функции,
где из названия будет понятно, что цикл будет делать.
Если же цикл останется в своём контексте,
то без комментариев его назначение будет трудно понять.

Проблема циклов в том, что это очень низкоуровневые конструкции:
уровень абстракции для них ниже, чем для любого функционального инструмента.
Поэтому их желательно изолировать,
хотя бы чтобы избежать смешивания уровней абстракции.
Функциональные выражения также могут оказаться сложны для понимания,
и тогда их тоже нужно изолировать в новые функции
с названиями, раскрывающими суть действия.
