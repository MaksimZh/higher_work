# Пишем безошибочный код

## 1. Выводы по изучению материала
Для полноценного использования программирования, ориентированного на типы
нужно, на мой взгляд, две вещи.

Первое - типы должны быть объектами первого класса.
Это буквально означает возможность проводить вычисления с типами так же,
как мы это делаем, например, с целыми числами или строками.
Тогда не нужны будут никакие шаблоны, дженерики и прочие костыли,
потому что будет достаточно функций
для которых входными и выходными данными являются типы.

Второе - агрессивные вычисления во время компиляции.
Всё, что можно вычислить на основе кода программы до её запуска
должно быть вычислено компилятором.
В первую очередь это касается типов данных, которые (согласно первому пункту)
именно вычисляются, а не выводятся.
Если типы "выводятся", то это какая-то странная для компьютера операция,
так и хочется это всё на человека свалить - пусть он думает.
А вот вычислять компьютер хорошо умеет - для того и создавался.

Когда выполнены эти два пункта, то при каждом вызове метода мы точно знаем
множество возможных конечных состояний-типов.
Если в этом множестве несколько элементов,
то это действительно определяется
данными, доступными только при выполнении программы.
Тогда нужно рассматривать все возможные варианты,
а не обвешивать код assert-ами и type-ignor-ами,
как это приходится делать с современными линтерами в Python.


## 2. Реальный код

## 2.1. Решения и компоненты
```Python
class WaveAxisKind(Enum):
    SOL = auto()
    COMP = auto()
    
    def __rshift__(self, other: Axis) -> "_LinkWaveAxisKind":
        if self != self.SOL:
            return NotImplemented
        return _LinkWaveAxisKind(self, other)
```
Операция `>>` существует только для одного из двух значений этого типа данных.
Это уж совсем точно разные типы данных, раз у них даже наборы операторов разные:
```Python
class _WaveMarker:
    def __rshift__(self, other: Axis) -> "_LinkWaveMarker":
        return _LinkWaveMarker(other)

class _CompMarker:
    pass
```
Вообще-то, линтер ловил ошибки и с первой версией кода,
но теперь это как-то надёжнее стало.
Всё-таки непонятно, насколько линтер "агрессивен" в плане работы со значениями,
а вот с типами должен работать хорошо.


## 2.2. Столбцы и строки матриц
```Python
class MatrixAxisKind(Enum):
    COL = auto()
    ROW = auto()

    def __add__(self, other: MatrixGroupKey) -> "_KeyMatrixAxisKind":
        return _KeyMatrixAxisKind(self, other)
    
    def __rshift__(self, other: Axis) -> "_LinkMatrixAxisKind":
        if self != ROW:
            return NotImplemented
        return _LinkMatrixAxisKind(self, other)
```
Снова та же ситуация, и решение то же:
```Python
class _ColMarker:
    def __add__(self, other: MatrixGroupKey) -> "_KeyColMarker":
        return _KeyColMarker(other)


class _RowMarker:
    def __add__(self, other: MatrixGroupKey) -> "_KeyRowMarker":
        return _KeyRowMarker(other)
    
    def __rshift__(self, other: Axis) -> "_LinkRowMarker":
        return _LinkRowMarker(other)
```


## 2.3 Параметры осей тензоров
```Python
class Tensor(_BasicTensor):

    @staticmethod
    def prepare_params(
            uid: int, param_axes: tuple[ParamAxis, ...]
            ) -> tuple[ParamAxis, ...]:
        """
        This method is called for each class in current class MRO
        in direct order (from child to parent classes).
        
        This method should convert user axis parameters to internal parameters
        and prepare new user parameters to be processed by parent classes.

        The internal parameters must be sufficient to completely setup
        the class instance within `post_init` method provided all parent
        classes are setup correctly;

        If the internal parameters differ from user-friendly parameters,
        then they must:
          - indicate (if found by this method) that the parameterized axis
            is taken from another tensor's `param_axes` property and thus has
            internal parameters for all parent classes (so all parent classes
            will also be setup correctly);
          - be not a part of public interface in any way, i.e. they are
            not supposed to be set or read by user or any child/parent classes
            (only user parameters should be used to communicate with parent
            classes);
          - be dropped/modified by this method in favor of user parameters.
            if there is any conflict.

        The unique instance identifier can be used to form internal parameters
        different for any existing instances if needed.
        """
        return param_axes
    
    @property
    def param_axes(self) -> dict[Axis, ParamAxis]:
        ...

    ...
```
Судя по описанию того, что должно происходить с `param_axes`,
тут напрашиваются специализированный АТД, а не кортеж, как сейчас.
Причём тут возможны два состояния.

Первое - это параметры на этапе создания тензора (`InputAxisParams`),
когда возможно их изменение, и нужно различать,
какие параметры пришли от пользователя (или классов-потомков),
а какие уже готовы для завершающего этапа инициализации.
Изменять параметры, конечно, не будем.
Игры с состояниями на этапе инициализации объектов, особенно в Python -
опасный путь.
Под "изменением" понимается создание нового экземпляра класса.

Второе - это параметры, которые хранятся внутри тензора (`AxisParams`)
и доступны при завершении инициализации и для создания новых тензоров
с похожей структурой осей.
```Python
class Tensor(_BasicTensor):

    @staticmethod
    def prepare_params(uid: int, params: InputAxisParams) -> InputAxisParams:
        """
        This method is called for each class in current class MRO
        in direct order (from child to parent classes).
        
        This method should convert user axis parameters to internal parameters
        and prepare new user parameters to be processed by parent classes.

        The internal parameters must be sufficient to completely setup
        the class instance within `post_init` method provided all parent
        classes are setup correctly;

        The unique instance identifier can be used to form internal parameters
        different for any existing instances if needed.
        """
        return param_axes

    @property
    def params(self) -> AxisParams:
        ...

    ...
```
В качестве бонуса: теперь можно дополнить типы `AxisParams` и `InputAxisParams`
всякими удобными методами для извлечения параметров.
Тем более, эти методы уже есть в виде отдельных функций для работы с
кортежами `ParamAxis`.


## Выводы по практике
В последнее время я полюбил функциональное программирование и стараюсь
избегать явных состояний.
Поэтому было сложно найти код для этого задания.
То, как была организована обработка параметров осей тензоров (пункт 2.3)
меня не удовлетворяла.
Эту часть я переписывал несколько раз.
Похоже, теперь, наконец, найдено достаточно изящное решение, основанное
на явном разделении разных подходов к этим параметрам через разные типы.
Ещё больше деталей можно спрятать за красивым и абстрактным интерфейсом.
Это сделает их изменение безопасным, и поможет мне примирится
с рядом несовершенств (потом ведь можно будет всё поправить).


## Общие выводы
Вывел для себя правило.
Если данные начинают обрастать кучей "удобных" функций
и рекомендациями по работе с ними в комментариях,
если есть ощущение, что происходят какие-то сложные операции,
то это признак того, что нужно вводить новые типы данных и прятать
все сложности за интерфейсом.
Когда у нетривиальной последовательности операций
есть чёткий смысл в предметной области (например),
то это одна новая операция, и её нужно сделать тривиальной.
