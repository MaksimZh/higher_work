# Избавляемся от условных инструкций

## 1. Размышления по теории
При использовании условных инструкций сложность кода
(количество возможных путей) растёт экспоненциально.
Как быть?
Есть два способа уменьшить количество if-ов.

Первый - переместить код туда,
где результат вычисления условия уже известен.
Например, если функция получает на вход какой-то флаг,
лучше сделать две функции и вызвать ту из них, которая в этом месте нужна.

Второй - изменить логику кода так,
чтобы проверки были не нужны.
Например, вместо проверок выхода за границы
лучше использовать sentinel-value.
Пусть у нас есть игровое поле, состоящее из клеток.
Можно каждый раз проверять не пытается ли игрок выйти за пределы поля,
а можно окружить всё поле стенами.
Вместо явной проверки стена / не стена лучше использовать
single/multiple dispatch (виртуальные методы, например).

Только написать if проще.
Это идёт ещё со времён возникновения структурного программирования.
Тогда это был настоящий прорыв - if вместо goto
(подозреваю, что скорее вместо JNZ, JNE и т.п.).
После этого оператор goto устарел.
Теперь, похоже, устарел if.

## 2. Работа с кодом

### 2.1. Перенаправление волн
```Python
def plane_wave(
        h: BandHamiltonian, energy: Tensor, z: Tensor,
        redirect: bool = False
        ) -> PartialWaveSolutionPiece:
    ...
    if redirect:
        raw_w[:, :, 0, :1], raw_w[:, :, 1, :1] = \
            raw_w[:, :, 1, :1].copy(), raw_w[:, :, 0, :1].copy()
    ...
```
Сегодня хочется перенаправить одну волну, завтра - две.
Лучше сразу сделать управляемое количество,
а ноль - автоматически поведёт себя как `False`:
```Python
def plane_wave(
        h: BandHamiltonian, energy: Tensor, z: Tensor,
        redirect: int = 0
        ) -> PartialWaveSolutionPiece:
    ...
    raw_w[:, :, 0, :redirect], raw_w[:, :, 1, :redirect] = \
        raw_w[:, :, 1, :redirect].copy(), raw_w[:, :, 0, :redirect].copy()
    ...
```


### 2.2. Граничные условия
```Python
def _make_bound_waves(
        waves: SequenceTensor[PartialWaveSolutionPiece],
        bound_mx: Optional[PiecesMatchTensor] = None,
        ) -> LeftRightPiecesWaveMatrixTensor:
    ...
    simple_bounds = ...
    if bound_mx is None:
        return simple_bounds
    complex_bounds = ...
    return complex_bounds
```
На самом деле это костыль.
По логике приложения, эта функция всегда должна возвращать `simple_bounds`,
а `complex_bounds` должно вычисляться в другом месте.

Костыль понадобился, потому что срочно нужно было кое-что посчитать,
а новая версия программы ещё не дозрела до этих расчётов.
Вот и пришлось делать мини-апгрейд в старой версии.
В новой версии просто будет два класса,
один из которых - родитель - использует `simple_bounds`,
а второй - наследник - `complex_bounds`.


### 2.3. Словарь множеств
```Python
if i not in result:
    result[i] = set()
result[i].add(k)
```
Забавно, что проверка принадлежности ключа к словарю
происходит и в третьей строке, только внутри словаря.
А ещё есть метод `get`, в котором эта проверка также есть.
И всё это можно сделать в одну строку,
ещё и не полагаясь на мутабельность значений в словаре:
```Python
result[i] = result.get(i, set()) | {k}
```


### 2.4. Параметр Шрёдингера
```Python
class UnitaryPowerODES:
    ...
    
    def __init__(
            self,
            coefs: SquareMatrixTensor,
            powers: Optional[Tensor] = None) -> None:
        if not powers:
            self.__init_pow0(coefs)
            return
        self.__init_pow(coefs, powers)

    def __init_pow0(self, coefs: SquareMatrixTensor) -> None:
        ...

    def __init_pow(self, coefs: SquareMatrixTensor, powers: Tensor) -> None:
        ...
```
Это классический случай для перегрузки функций.
Только в Python это не работает, там конструктор один...
Или нет?
Используем multiple dispatch:
```Python
from multimethod import multimethod

class UnitaryPowerODES:
    ...
    
    @multimethod
    def __init__(self, coefs: SquareMatrixTensor) -> None:
        ...


    @multimethod
    def __init__(self, coefs: SquareMatrixTensor, powers: Tensor) -> None:
        ...
```


### 2.5. Одни равнее других
```Python
class Wrap[T]:
    ...
    def __eq__(self, other: object) -> bool:
        if not (type(other) == type(self)):
            return False
        return self.__target == other.__target
```
Подобные условия - следствие неявной динамической типизации в Python.
Правда, при такой простой процедуре сравнения писать отдельный `if`
не стоило.
```Python
class Wrap[T]:
    ...
    def __eq__(self, other: object) -> bool:
        return type(other) == type(self) and \
            self.__target == other.__target
```


### Выводы по работе с кодом
Думал, что смогу удалить любой `if`, но нет.
Были моменты, где я не смог понять какой должна быть "безусловная" логика.
Например, краевые случаи в математических выражениях,
вроде тензора нулевого ранга.
Тут был бы очень полезен какой-нибудь multiple dispatch по значению.
Может, стоит копать в сторону новой фичи Python - pattern matching.


## Общие выводы
Большая часть алгоритмов, обучение программированию в школе и университете
(кроме специализации Computer Science, наверное)
да и многие языки программирования
поощряют использование оператора `if`.
Вот если бы он был чем-то неудобным,
(вроде меток и `goto`, которыми я не пользовался со времён изучения Pascal в школе)
тогда писать его было бы ленивее, чем думать над "безусловной" логикой.

Пока же придётся себя искусственно ограничивать.
Оператор `else` уже удалось искоренить, как и вложенные `if`.
Теперь пора выходить на другой уровень чистоты кода.
