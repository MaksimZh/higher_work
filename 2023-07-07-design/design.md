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
