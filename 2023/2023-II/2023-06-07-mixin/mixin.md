# Миксины в Python

В Python миксины наследуются как обычные родительские классы:
```Python
class Child(MixinA, MixinB, Parent):
    ...
```
Отличие в том, что миксины не отражают какую-то сущность предметной области,
или реализации.
Вместо этого они реализуют некоторое свойство, общее для нескольких сущностей.

На уровне логики можно сказать, что `Child` *является* `Parent` но при этом
`Child` *не является* ни `MixinA` ни `MixinB`.
Скорее `Child` *имеет* `MixinA` и `MixinB`.
Отличие от композиции в том, что `Child` не оперирует миксинами
как внутренними сущностями (особенно если они не имеют своего состояния).
Наоборот, миксины могут получить доступ к состоянию `Child`,
добавляя новый функционал.

Если миксины просто добавляют новые методы, то порядок наследования не важен.

Если они переопределяют методы друг-друга или родительских классов,
то нужно учитывать [MRO](https://habr.com/ru/post/62203/)
(method resolution order).


## Пример 1: одиночный миксин
Конечно, это лучше делать через геометрические шейдеры, но...

Пусть у нас есть какие-то геометрические фигуры, которые нужно отображать
в виде набора треугольников.
Чтобы не перегружать сами фигуры, пусть они просто выдают точки внешней границы,
а формированием треугольников займётся миксин:
```Python
class Shape:
    ...
    def get_border_points(self) -> list[Point]:
        ...

class FillTriangleMixin:

    def __init__(self) -> None:
        # у миксина нет родителя
        # так вызывается конструктор следующего класса в MRO
        super().__init__()

    def get_triangles(self) -> list[ColoredTriangle]:
        # Используем запрос того класса, к которому добавлен миксин
        border_points = self.get_border_points()
        # Теперь обрабатываем полученную информацию и возвращаем результат
        return self.__triangulate(border_points)

    @staticmethod
    def __triangulate(border_points: list[Point]) -> list[Triangle]:
        ...

class VisibleShape(FillTriangleMixin, Shape):
    ...

...
s = VisibleShape(...)
...
# Вызываем метод, который добавлен с помощью миксина
render(s.get_colored_triangles())
```


## Пример 2: комбинация миксинов
Теперь пусть точки фигуры - это опорные узлы кубической кривой Безье.
```Python
class BezierMixin:
    
    def get_border_points(self) -> list[Point]:
        # Вызываем не этот метод, а метод следующего класса в MRO
        base_points = super().get_border_points()
        # Обрабатываем полученную информацию и возвращаем результат
        return self.__calc_bezier_points(base_points)

    @staticmethod
    def __calc_bezier_points(base_points: list[Point]) -> list[Point]:
        ...

# Порядок наследования не важен
# Всё равно FillTriangleMixin вызовет get_border_points класса-потомка
class VisibleBezierShape(FillTriangleMixin, BezierMixin, Shape):
    ...
```


## Пример 3: взаимодействие миксинов
Теперь мы добавим ещё один миксин, который подготовит опорные точки кривой Безье
так, чтобы у исходной фигуры были скруглённые углы.

Здесь важен порядок наследования, чтобы сначала обработать углы, и затем получить
кривую Безье, а не наоборот.
```Python
class RoundCornerMixin:
    
    def get_border_points(self) -> list[Point]:
        # Вызываем не этот метод, а метод следующего класса в MRO
        border_points = super().get_border_points()
        # Обрабатываем полученную информацию и возвращаем результат
        return self.__calc_base_points(border_points)

    @staticmethod
    def __calc_base_points(border_points: list[Point]) -> list[Point]:
        ...

# Порядок наследования важен!
# BezierMixin вызовет RoundCornerMixin.get_border_points
# RoundCornerMixin вызовет Shape.get_border_points
class VisibleRoundCornerShape(FillTriangleMixin, BezierMixin, RoundCornerMixin, Shape):
    ...
```
