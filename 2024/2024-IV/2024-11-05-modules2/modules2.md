# Модули важнее всего-2

## 1. Теория
Прочитал статью
[F-bounded quantification for object-oriented programming](https://www.researchgate.net/publication/239572610_F-bounded_quantification_for_object-oriented_programming).
Это отличная иллюстрация того,
как важна практика при освоении чего-то нового.
Органично встроенные в статью практические примеры сделали её понятной
даже для тех, кто не является специалистом в теории типов.

Что такое **ограниченный полиморфизм** (bounded polymorphism)?
Это когда выбор полиморфного типа `T` (тип-аргумента, заранее неизвестного)
ограничивается на основе некоторого правила (`Bound`):

```
func[T: Bound](t: T, ...) -> ...
```

Что такое **F-ограниченный полиморфизм** (F-bounded polymorphism)?
Это когда выбор полиморфного типа `T`
ограничивается на основе некоторого правила (`FBound`),
зависящего от этого же типа `T` как от аргумента:
```
func[T: FBound[T]](t: T, ...) -> ...
```

Такая штука может пригодиться, если правило содержит внутри тип,
к которому применяется.
Это встречается довольно часто,
например, если операции сравнения и копирования оформлены как методы `T`,
то они принимают и возвращают `T` соответственно:
```
T {
    equal: T -> Bool
    copy: Void -> T
}
```

Тип нулевого аргумента метода (в Python известного как `self`)
здесь пропущен.

Пусть в функции `func` нам нужны методы `t.equal` и `t.copy`.
Если мы используем ограниченный полиморфизм,
то потерпим фиаско на уровне теории типов:

```
Bound {
    equal: Bound -> Bool
    copy: Void -> Bound
}

func[T: Bound](t: T, ...) -> ...
```

Всё бы хорошо, но `t.copy` для любого `T` вернёт `Bound` вместо `T`,
и это должно привести к ошибке компиляции,
если требуется результат типа `T`.
С `t.equal` ситуация и того хуже:
этот метод принимает любой аргумент типа `Bound`,
из-за чего статический анализ может пропустить ошибочную передачу
аргумента отличного от `T` типа,
который тоже является подтипом `Bound`.

Надо так:

```
FBound[T] = T {
    equal: T -> Bool
    copy: Void -> T
}

func[T: FBound[T]](t: T, ...) -> ...
```

Здесь типы аргументов и возвращаемых значений **вычисляются**
при подстановке конкретного `T`.


## 2. Практика
Основным рабочим языком для меня пока является Python,
и он не поддерживает F-ограниченный полиморфизм напрямую:

```Python
class Bound[T]:
    def equal(self, t: T) -> bool:
        ...
    def copy(self) -> T:
        ...

# Type of "T" could not be determined because it refers to itself
def func[T: Bound[T]](t: T) -> T:
    return t
```

Программа запустится, конечно, но линтер будет ругаться.

Мы его всё-равно перехитрим:

```Python
class Bound:
    def equal[T](self: T, t: T) -> bool:
        ...
    def copy[T](self: T) -> T:
        ...

def func[T: Bound](t: T) -> T:
    return t
```

Это не совсем классическая форма F-ограниченного полиморфизма,
потому что в правиле нет явного аргумента `T`.
Тем не менее, это именно он, потому что `Bound` устроен так,
что в нём присутствует неявный аргумент `T` и его привязка к типу `self`.

Оказывается, я и раньше этот приём использовал, вот пример:

```Python
class Taggable[P]:
    ...

    def __call__[T](self: T, *args: P) -> Parameterized[T, P]:
        return Parameterized(self, set(args))
```

Применение оператора круглых скобок к любому экземпляру класса `Foo`,
являющегося подклассом `Taggable`,
вернёт именно конкретный `Parameterized[Foo, P]`,
а не абстрактный `Parameterized[Taggable[P], P]`.

Для чистоты эксперимента можно сделать так,
чтобы "подтип" определялся не на основе наследования,
а по сигнатурам методов:

```Python
from typing import Protocol

class Bound(Protocol):
    def equal[T](self: T, t: T) -> bool:
        ...
    def copy[T](self: T) -> T:
        ...


def func[T: Bound](t: T) -> T:
    return t


class Foo:
    def equal(self, t: "Foo") -> bool:
        ...
    def copy(self) -> "Foo":
        ...

func(Foo())
```


## Выводы
Оказывается, я открыл F-ограниченный полиморфизм в тот момент,
когда мне понадобилось, чтобы методы класса-родителя явно
(на уровне статического анализа)
возвращали и принимали аргументы конкретных типов,
являющихся производными класса-потомка.
Даже получилось реализовать это в Python,
в котором изначально типы не считались такими уж важными.

Это инверсия зависимостей на математических стероидах.
Классический подход:
вместо зависимости `func` от конкретного `T`,
и `func` и `T` зависят от одного и того же "интерфейса" `Bound`.
То есть, `Bound` должен быть известен (зафиксирован)
в момент проектирования `T`, `T` зависит от `Bound`.
```
   Bound
  /    \
func    T
```

Продвинутый подход:
`func` зависит от `Bound`, который, так же как и `T`,
воплощает некоторую абстракцию.
Возможно, что `T` проектировался с учётом этой абстракции,
а возможно - нет, потому что она могла родиться позже,
при проектировании новых частей проекта.

Вот, что мы имеем на уровне логики:

```
  <Abstraction>
    /      \
 Bound      T
  /
func
```

А вот уровень кода:

```
module1 : module2
        :
Bound   :   T
  |     :
func    :
        :
```

Мы получили полностью независимые модули.
Даже если у нас нет возможности модифицировать `module2` и `T`,
мы всё равно можем связать `T` с `Bound`
в рамках логики нашей программы.
Это работает, даже если при проектировании `T` логика
(и команда разработчиков) совсем другая,
создавался он для других целей и даже не подозревал про `Bound`.
Это случай одной реализации нескольких интерфейсов.

Кто знает, может при создании первых прототипов автомобилей
кто-то использовал в коробке передач шестерни из старых часов,
сделанных ещё до открытия парового двигателя.
Реализация старая, а логика использования новая.

Хорошо бы, конечно, где-то добавить тест на то,
что `T` соответствует `Bound`.
Это важно чтобы логика была отражена в коде,
в частности, для быстрой диагностики нежелательных изменений `T`.

Вот такая "инверсия зависимостей" происходит при написании кода:
```
    <Abstraction>  ----
      /    \           |
  Bound     T          | dependency inversion
  /   \    /           |
func   test <----------
```