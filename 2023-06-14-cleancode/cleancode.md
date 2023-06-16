# 1. Ясный код - уровень реализации

## 1.1 Методы, которые используются только в тестах
```Python
class _BaseAxis:
    __name: str
    
    def __init__(self, name: str) -> None:
        self.__name = name

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return False
        return self.__name == other.__name

    def __str__(self) -> str:
        return f"{type(self).__name__}('{self.__name}')"

    @property
    def name(self) -> str:
        return self.__name

class Axis(_BaseAxis):
    def __init__(self, name: str) -> None:
        super().__init__(name)

class NewAxis(_BaseAxis):
    def __init__(self, name: str) -> None:
        super().__init__(name)
```
```Python
class Test_Axis(unittest.TestCase):

    def test_simple(self):
        a = Axis("x")
        self.assertEqual(a, Axis("x"))
        self.assertNotEqual(a, NewAxis("x"))
        self.assertEqual(str(a), "Axis('x')")
        self.assertEqual(a.name, "x")
    ...
```
