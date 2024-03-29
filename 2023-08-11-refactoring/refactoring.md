# Рефакторинг

## 1. Массивы и тензоры
Библиотека NumPy очень хороша для вычислений, когда речь идёт об одномерных
(максимум - двумерных) массивах.
Работа с многомерными наборами данных, где разные размерности
(в терминах NumPy - "оси"/"axes")
обладают существенно разным смыслом в предметной области,
приводит к появлению страшных конструкций:
```Python
# [meshes, mesh, initials*origins*components]
y1 = np.array([
    integrate.solve_ivp(odeFunc, (t[0], t[-1]), y0, t_eval = t).y.T \
        for t in meshes])
# [meshes, mesh, initials, origins, components]
y2 = y1.reshape(len(meshes), meshes.shape[1], len(initials), len(origins), dim)
# [initials, origins, meshes, mesh, components]
y = y2.transpose(2, 3, 0, 1, 4)
```
Для манипуляций с осями был добавлен новый слой абстракции - тензоры.
Задача тензоров - предостатвить более удобный интерфейс по сравнению с
`reshape`, `transpose` и `newaxis`:
```Python
# интерпретируем первые две оси как meshes и r
# а третью ось разбиваем на три оси заданного размера
# (размер указывается в квадратных скобках)
tensor = Tensor(
    y1,
    ax_meshes,
    ax_r,
    ax_init[len(initials)] * ax_orig[len(origins)] * ax_comp[dim])
# создаём массив NumPy с заданным порядком осей для дальнейших вычислений
y = tensor.get_array(ax_init, ax_orig, ax_mesh, ax_r, ax_comp)
```
Вот пример с `newaxis`:
```Python
>>> a = np.arange(1, 4)
>>> a[np.newaxis] + 10 * a[:, np.newaxis]
array([[11, 12, 13], 
       [21, 22, 23], 
       [31, 32, 33]])
>>> Tensor(a, x).get_array(+y, x) + Tensor(10*a, y).get_array(y, +x)
array([[11, 12, 13],
       [21, 22, 23],
       [31, 32, 33]])
```

Массивы - это наборы данных для математических операций, которые используются
на самом низком уровне абстракции.
На более высоком уровне абстракции за логическую структуру данных отвечают тензоры.
То есть здесь введена новая граница для разделения на уровни абстракции.

В рамках данного проекта все непосредственные операции с осями массивов NumPy
(`reshape`, `transpose` и `newaxis`) запрещены по соглашению
(на уровне документации).
В коде (на уровне интерфейсов и типов) явного запрета нет.

В дальнейшем возможно расширение возможностей тензоров и вытеснение зависимости
от NumPy из всё большего количества модулей и уровней логики.


## 2. Классификация осей
Пусть мы получили массив линейно-независимых решений
системы дифференциальных уравнений
и хотим использовать метод матрицы рассеяния для вычисления их правильной
линейной комбинации.
На уровне логики это два разных раздела предметной области.

При решении системы дифуров достаточно различить независимые решения.
Для построения матриц рассеяния важно различать ещё и направления распространения.
Грубо говоря, добавляется дополнительная ось размерности 2 с координатами "лево"/"право".

[Раньше предлагалось](../2023-08-01-protective/protective.md)
различать оси по их типу с помощью *льготного наследования*.
При этом получается, что при переносе данных на новый этап расчётов нужно
поменять их оси, т.к. в разных разделах предметной области свои типы осей.

Тут важно провести границу:
оси - это часть данных, или часть их интерпретации?
Если информация об интерпретации - тип оси, то второй вариант,
если же она содержится только в классе-наследнике от `Tensor`,
то первый вариант.

Фактически, потомки класса `Tensor` всё равно хранят дополнительную служебную
информацию.
Поэтому, для упрощения системы было решено убрать служебную информацию из осей.
Однако, сейчас у тензоров очень удобный интерфейс для обёртывания (wrap)
массивов, где можно использовать унарный плюс для создания новых осей,
умножение для разбиения и слияния осей
и квадратные скобки для задания размерности при разбиении.
Возврат к конструкторам с кучей ключевых слов, задающих интерпретацию осей,
исключил бы эти удобства для специальных видов тензоров.

Решение - добавление новой операции (скобок), которая сначала использовалась
только для связывания строк и столбцов матриц друг с другом.
Теперь эта операция переносится из узкоспециализированного модуля
в основной модуль, где определены типы осей:
```Python
class Axis:
    ...
    
    def __call__(self, tag: Any) -> "TagAxis":
        return TagAxis(self, tag)

...

@final
class TagAxis(Axis):
    ...
    
    def __init__(self, axis: Axis, tag: Any) -> None:
        super().__init__(axis.name)
        self.__axis = axis
        self.__tag = tag

    @property
    def axis(self) -> Axis:
        return self.__axis
    
    @property
    def tag(self) -> Any:
        return self.__tag
```
То, что `TagAxis` - потомок `Axis` позволяет использовать все операции
(`+a`, `a[n] * b[m]`, ...) с такими осями.

В результате имеем следующую архитектуру.
Базовый класс `Tensor` отвечает только за структуру массива и все оси в нём
равноправны.
Потомки этого класса могут в конструкторе извлечь дополнительную информацию
из тегов осей и сохранить её отдельно.
Оси хранятся в программе только в чистом виде.
Дополнительная информация "навешивается" на них в виде тегов
только при передаче в конструктор.

Вот как создавались матрицы раньше:
```Python
class WaveAxis(Axis): ...
class WaveDirAxis(WaveAxis): ...
class ComponentAxis(Axis): ...
...
d = WaveDirAxis("d")
w = WaveAxis("w")
c1 = ComponentAxis("c1")
c2 = ComponentAxis("c2")
a1 = Axis("a1")
a2 = Axis("a2")
wm = WaveMatrices(
    np.zeros((2, 3, 3, 2, 4, 5)),
    d, w, c1, c2, a1, a2)
```
А теперь так:
```Python
class WA(Enum):
    DIR = auto()
    EXT = auto()
    COMP = auto()
...
d = Axis("d")
w = Axis("w")
c1 = Axis("c1")
c2 = Axis("c2")
a1 = Axis("a1")
a2 = Axis("a2")
wm = WaveMatrices(
    np.zeros((2, 3, 3, 2, 4, 5)),
    d(WA.DIR), w(WA.EXT), c1(WA.COMP), c2(WA.COMP), a1, a2)
```


## 3. Новый механизм задания базис
Новый механизм `TagAxis` можно использовать и для задания базисов,
которые у операторов привязаны к осям.

Раньше механизм указания базисов был частью интерфейса оператора.
```Python
class Operator(Tensor):
    __bases: dict[Axis, Basis]
    
    def __init__(
            self,
            array: NDArray[Any, Any],
            *axes: Axis | tuple[Axis, Basis],
            ) -> None:
        ...

    ...
```
Теперь мы перейдём к использованию более общего механизма.
```Python
class Operator(Tensor):
    __bases: dict[Axis, Basis]
    
    def __init__(
            self,
            array: NDArray[Any, Any],
            *axes: WrapAxis,
            ) -> None:
        ...
```

Здесь рефакторинг состоит в том, что на уровне логики отдельный механизм
связывания оси с дополнительными данными (базисом)
был упразднён в пользу нового и более общего механизма связывания - `TagAxis`.
В коде это отразилось на интерфейсе конструктора класса `Operator`:
Кортежи вида `(axis, basis)` он больше не принимает.


## Резюме
Для меня это упражнение было больше про работу на уровне логики,
чем на уровне кода.
Все три примера про эволюцию одного и того же кода,
которая привела к тому, что несколько подзадач были в итоге решены
с помощью одного универсального инструмента - осей.

Несмотря на то, что хранение данных в осях казалось удобным с точки зрения
реализации в коде,
это приводило к размазыванию данных между осями и тензорами.
Противоречие между удобством на уровне логики и кода
было решено в пользу логики.
Парадокс, но в итоге это привело к упрощению кода.
Упрощение интерфейса осей и базового класса тензоров
сделало их более абстрактными и универсальными.

Отдельным упражнением было реализовать оператор умножения осей так,
чтобы при разбиении одной большой оси на несколько в произведении
встречалось не более одной оси без явно указанного размера
(он определяется автоматически).
Это было сделано с помощью системы типов и проверяется линтером,
а не в рантайме.
Для меня это новый подход, который я раньше не применял в таком объёме.

Можно было сделать систему типов ещё более мощной и передать линтеру
проверку ещё ряда требований,
но в Python с этим довольно сложно.
