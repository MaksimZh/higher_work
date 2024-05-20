# Правила простого проектного дизайна


## Запрет ошибочного поведения на уровне интерфейса - 1
Можно передать любую строку, что может привести к ошибке:
```Python
class RobotCleaner:
    ...
    def select_device(self, name: str) -> None: ...
```
Можно передать только значение типа `Device`,
любое из которых является допустимым:
```Python
class Device(Enum):
    WATER = "water"
    SOAP = "soap"
    BRUSH = "brush"

class RobotCleaner:
    ...
    def select_device(self, device: Device) -> None: ...
```


## Запрет ошибочного поведения на уровне интерфейса - 2
```Python
class Entity(int):
    pass

class World(Status):
    
    ...

    @status("OK", "ALREADY_EXISTS")
    def add_entity(self, entity: Entity) -> None:
        ...
    
    @status("OK", "NO_ENTITY")
    def remove_entity(self, entity: Entity) -> None:
        ...

    def is_empty(self) -> bool:
        ...
    
    def has_entity(self, entity: Entity) -> bool:
        ...

    def new_entity(self) -> Entity:
        ...
    
    ...
```
Для добавления новой сущности нужно делать так:
```Python
e = world.new_entity()
world.add_entity(e)
```
Минусы такого подхода:
  - для создания новой сущности нужно вызывать два метода в определённом порядке;
  - сущности нужно вручную удалять из мира;
  - сущность может не принадлежать миру, и при работе с ней нужно это проверять;

Решение следующее:
будем считать, что мир содержит все сущности и они неуничтожимы.
Тогда в начале игры все сущности "чистые", т.е. без компонентов, и никак себя
не проявляют.
Поэтому, для удаления объекта из игры достаточно очистить сущность от компонентов.

Для большей уверенности мы запретим создавать сущности вручную.
Для этого есть [разные варианты](https://stackoverflow.com/questions/8212053/private-constructor-in-python).
```Python
class NoPublicConstructor(type):
    ...

class Entity(metaclass=NoPublicConstructor):
    
    # Этот метод можно вызывать только из этого модуля, из класса `World`
    @classmethod
    def _create(cls) -> "Entity":
        ...


class World(Status):
    
    ...

    def clean_entity(self, entity: Entity) -> None:
        ...

    def new_entity(self) -> Entity:
        ...

    ...
```
У оставшихся методов нет статусов (декораторов `@status`).
То есть они всегда выполняются успешно.
Ошибочное поведение запрещено на уровне интерфейса.


## Передача конструктору обязательных аргументов - 1
В этой версии приходится добавлять возможность низкоуровневой настройки
для задания начального состояния робота:
```Python
class RobotCleaner:
    def __init__(self) -> None:
        ...

    def get_device(self) -> Device: ...
    def get_location(self) -> Location: ...
    def get_angle(self) -> Angle: ...

    def set_location(self, location: Location) -> None: ...
    def set_angle(self, angle: Angle) -> None: ...
    def set_device(self, device: Device) -> None: ...

    def move(self, distance: Distance) -> None: ...
    def turn(self, angle_degrees: int) -> None: ...
    def select_device(self, device: Device) -> None: ...
```
Теперь начальное состояние передаётся в конструктор и не нужны лишние команды:
```Python
class RobotCleaner:
    def __init__(self, location: Location, angle: Angle, device: Device) -> None:
        ...

    def get_device(self) -> Device: ...
    def get_location(self) -> Location: ...
    def get_angle(self) -> Angle: ...

    def move(self, distance: Distance) -> None: ...
    def turn(self, angle_degrees: int) -> None: ...
    def select_device(self, device: Device) -> None: ...
```


## Передача конструктору обязательных аргументов - 2
Метод `__setitem__` нужен только для заполнения матрицы гамильтониана.
В дальнейшем с ним предполагается работать как с иммутабельным значением.
```Python
class BulkHamiltonian:

    def __init__(self, size: int, valence_size: int) -> None: ...

    ...

    @property
    def tensor(self) -> NDArray[Shape["*, *, 4, 4"], Complex]: ...

    def __getitem__(self, indices: tuple[int, int]) -> NDArray[Shape["4, 4"], Complex]:
        ...
    
    def __setitem__(
            self,
            indices: tuple[int, int],
            value: list[list[complex]] | NDArray[Shape["4, 4"], Complex]
            ) -> None:
        ...
```
Тогда лучше сконструировать матрицу заранее и передать её в конструктор.
Это упрощает интерфейс и запрещает изменение значения в дальнейшем:
```Python
class BulkHamiltonian:

    def __init__(self, tensor: NDArray[Shape["*, *, 4, 4"], Complex], valence_size: int) -> None: ...

    ...

    @property
    def tensor(self) -> NDArray[Shape["*, *, 4, 4"], Complex]: ...

    def __getitem__(self, indices: tuple[int, int]) -> NDArray[Shape["4, 4"], Complex]:
        ...
```


## Избегание увлечения примитивными типами данных - 1
```Python
class Temperature:
    __kelvins: float

    def __init__(self, kelvins: float) -> None:
        self.__kelvins = kelvins

    @property
    def kelvins(self) -> float:
        return self.__kelvins
```
Хороший способ не забыть в чём меряется температура.


## Избегание увлечения примитивными типами данных - 2
```Python
class Tensor:
    ...
    
    def __init__(self, array: NDArray[Any, Any], *axes: str) -> None:
        ...

    ...
    
    def get_array(self, *axes: str | NewAxis | AxisMerge) -> NDArray[Any, Any]:
        ...
```
Обёртка вокруг массивов NumPy с именованными осями (измерениями),
которая делает удобными перестановку, добавление и объединение осей.

Раньше в коде встречалось такое:
```Python
# [meshes, mesh, initials, origins, dim]
# [initials, origins, meshes, mesh, dim]
y = x.transpose(2, 3, 0, 1, 4)
```
Теперь транспонирование будет более наглядным и не нуждается в комментариях:
```Python
t = Tensor(x, "meshes", "mesh", "initials", "origins", "dim")
y = x.get_array("initials", "origins", "meshes", "mesh", "dim")
```
