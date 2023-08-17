# Рефакторинг

# 1. Операторы и базисы
```Python
class Operator(Tensor):
    __bases: dict[Axis, Basis]
    
    def __init__(
            self,
            array: NDArray[Any, Any],
            *axes: Axis | tuple[Axis, Basis],
            ) -> None:
        axis_names, bases = self.__parse_axes(*axes)
        super().__init__(array, *axis_names)
        self.__bases = bases
    
    ...
```

