# Передача по ссылке

## 1. Мутабельные массивы
Здесь массив никуда не передаётся, но его заполнение происходит
с использованием мутабельного состояния:
```Python
_array_ec = np.zeros((8, 8, 4, 4), dtype=complex)
for i in range(2):
    _array_ec[i, i, 0, 0] = 1

_array_ev = np.zeros((8, 8, 4, 4), dtype=complex)
for i in range(2, 6):
    _array_ev[i, i, 0, 0] = 1

_array_es = np.zeros((8, 8, 4, 4), dtype=complex)
for i in range(6, 8):
    _array_es[i, i, 0, 0] = 1
```
Замысел не очевиден и сходу понять правильно ли работает код тоже нельзя.

В языке Python иммутабельные значения не предусмотрены, но можно просто
не менять состояние:
```Python
_0 = np.zeros((4, 4), dtype=complex)
_1 = np.zeros((4, 4), dtype=complex)

_array_ec = np.array([
    [_1, _0, _0, _0, _0, _0, _0, _0],
    [_0, _1, _0, _0, _0, _0, _0, _0],
    [_0, _0, _0, _0, _0, _0, _0, _0],
    [_0, _0, _0, _0, _0, _0, _0, _0],
    [_0, _0, _0, _0, _0, _0, _0, _0],
    [_0, _0, _0, _0, _0, _0, _0, _0],
    [_0, _0, _0, _0, _0, _0, _0, _0],
    [_0, _0, _0, _0, _0, _0, _0, _0],
])
_array_ev = np.array([
    [_0, _0, _0, _0, _0, _0, _0, _0],
    [_0, _0, _0, _0, _0, _0, _0, _0],
    [_0, _0, _1, _0, _0, _0, _0, _0],
    [_0, _0, _0, _1, _0, _0, _0, _0],
    [_0, _0, _0, _0, _1, _0, _0, _0],
    [_0, _0, _0, _0, _0, _1, _0, _0],
    [_0, _0, _0, _0, _0, _0, _0, _0],
    [_0, _0, _0, _0, _0, _0, _0, _0],
])
_array_es = np.array([
    [_0, _0, _0, _0, _0, _0, _0, _0],
    [_0, _0, _0, _0, _0, _0, _0, _0],
    [_0, _0, _0, _0, _0, _0, _0, _0],
    [_0, _0, _0, _0, _0, _0, _0, _0],
    [_0, _0, _0, _0, _0, _0, _0, _0],
    [_0, _0, _0, _0, _0, _0, _0, _0],
    [_0, _0, _0, _0, _0, _0, _1, _0],
    [_0, _0, _0, _0, _0, _0, _0, _1],
])
```
Вот что на самом деле имелось в виду.
Сравнивая эти матрицы с формулой из научной статьи сразу видно
на месте у нас единицы с нулями, или нет.
Код стал отражением предметной области.


## 2. Многоэтапное изменение мутабельного массива
Здесь ситуация аналогичная, только ещё запутаннее:
происходит два разных действия, заполнение части матрицы
и копирование заполненной части в другую часть с переворотом и сопряжением:
```Python
_array_p = np.zeros((8, 8, 4, 4), dtype=complex)
_array_p[0, 2] = -sqrt(1/2) * _pp
_array_p[0, 3] = sqrt(2/3) * _pz
_array_p[0, 4] = sqrt(1/6) * _pm
_array_p[0, 6] = -sqrt(1/3) * _pz
_array_p[0, 7] = -sqrt(1/3) * _pm
_array_p[1, 3] = -sqrt(1/6) * _pp
_array_p[1, 4] = sqrt(2/3) * _pz
_array_p[1, 5] = sqrt(1/2) * _pm
_array_p[1, 6] = -sqrt(1/3) * _pp
_array_p[1, 7] = sqrt(1/3) * _pz
_array_p[2:8, 0:2] = np.conj(_array_p[0:2, 2:8].transpose(1, 0, 3, 2))
```
Снова переходим к иммутабельным значениям и делаем код похожим
на исходные формулы:
```Python
_p_cv = 1 / sqrt(6) * np.array([
    [-sqrt(3) * _pp, 2 * _pz, _pm, _0],
    [_0, -_pp, 2 * _pz, sqrt(3) * _pm],
])
_p_cs = 1 / sqrt(3) * np.array([
    [-_pz, -_pm],
    [-_pp, _pz],
])
_conj = lambda a: np.conj(a).transpose(1, 0, 3, 2) #type: ignore
_zeros = lambda h, w: np.zeros((h, w, 4, 4)) #type: ignore
_array_p = np.array([
    [_zeros(2, 2), _p_cv, _p_cs],
    [_conj(_p_cv), _zeros(4, 4), _zeros(4, 2)],
    [_conj(_p_cs), _zeros(2, 4), _zeros(2, 2)],
])
```


## 3. Ошибка при оптимизации рекурсии
Код, где для хвостовой рекурсии используется мутабельное состояние:
```Python
def eval_unwrap(
        indices: dict[Axis, int],
        shape: tuple[int, ...],
        axes: tuple[WrapAxis, ...]) -> UnwrapData:
    data = UnwrapData((), ())
    _rec_eval_unwrap(indices, shape, axes, data)
    return data

def _rec_eval_unwrap(
        indices: dict[Axis, int],
        shape: tuple[int, ...],
        axes: tuple[WrapAxis, ...],
        data: UnwrapData) -> None:
    if len(axes) == 0:
        return
    if isinstance(axes[0], AxisMerge):
        merged_indices = tuple(indices[ax] for ax in axes[0].axes)
        size = reduce(mul, (shape[i] for i in merged_indices))
        data.transpose_indices += merged_indices
        data.reshape_sizes += (size,)
        _rec_eval_unwrap(indices, shape, axes[1:], data)
        return
    if isinstance(axes[0], NewAxis):
        data.reshape_sizes += (1,)
        _rec_eval_unwrap(indices, shape, axes[1:], data)
        return
    assert isinstance(axes[0], Axis)
    assert axes[0] in indices
    index = indices[axes[0]]
    data.transpose_indices += (index,)
    data.reshape_sizes += (shape[index],)
    _rec_eval_unwrap(indices, shape, axes[1:], data)
```
Теперь передаются иммутабельные значения, а результат возвращается функцией:
```Python
def eval_unwrap(
        indices: dict[Axis, int],
        shape: tuple[int, ...],
        axes: tuple[WrapAxis, ...]) -> UnwrapData:
    return _rec_eval_unwrap(indices, shape, axes, UnwrapData((), ()))

def _rec_eval_unwrap(
        indices: dict[Axis, int],
        shape: tuple[int, ...],
        axes: tuple[WrapAxis, ...],
        data: UnwrapData) -> UnwrapData:
    if len(axes) == 0:
        return data
    if isinstance(axes[0], AxisMerge):
        merged_indices = tuple(indices[ax] for ax in axes[0].axes)
        size = reduce(mul, (shape[i] for i in merged_indices))
        return _rec_eval_unwrap(indices, shape, axes[1:], UnwrapData(
            data.transpose_indices + merged_indices,
            data.reshape_sizes + (size,)))
    if isinstance(axes[0], NewAxis):
        return _rec_eval_unwrap(indices, shape, axes[1:], UnwrapData(
            data.transpose_indices,
            data.reshape_sizes + (1,)))
    assert isinstance(axes[0], Axis)
    assert axes[0] in indices
    index = indices[axes[0]]
    return _rec_eval_unwrap(indices, shape, axes[1:], UnwrapData(
        data.transpose_indices + (index,),
        data.reshape_sizes + (shape[index],)))
```
В таком коде сложнее забыть `return`, или упустить что-то,
в случае добавления новых полей к `UnwrapData`.


## Резюме
Благодаря занятиям в Высшей Школе Программирования
за прошедший год мой стиль кодирования заметно изменился.
Теперь я стараюсь везде использовать иммутабельные значения.
Из-за этого найти мутабельные состояния в моих
программах было непростой задачей.

Самым полезным было подумать, что делать с заполнением массивов в первых
двух вариантах.
При написании этого модуля мне казалось,
что императивный код более компактный, и поэтому его легче понять.
Однако, при выполении задания я вернулся к своему же коду примерно через месяц.
Понадобилось много усилий для понимания что там происходит.

При этом новый функциональный код выглядит как прямой перевод формул на Python,
и его гораздо легче проверять.
Сразу видно всю матрицу целиком и не нужно думать,
что там под каким индексом лежит.
