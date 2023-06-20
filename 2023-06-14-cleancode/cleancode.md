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
Подумав над этим кодом понял, что этот функционал вообще не нужен,
потому что операция сравнения требуется только для имён осей при поиске
в словарях, например.
Вместо `Axis` удобнее напрямую использовать `str`,
а для `NewAxis` имя вообще не обязательно.
```Python
# Вспомогательный класс, используемый только при вызове конструктора тензора
# Минимальная необходимая реализация
@dataclass
class Axis:
    name: str
    kind: AxisKind

# Вспомогательный класс, используемый только при запросе данных из тензора
# Реализация вообще не нужна
class NewAxis:
    pass
```
```Python
...
def test_array_new(self):
    src = np.arange(1, 25).reshape(2, 3, 4)
    t = Tensor(
        src,
        Axis("a", AxisKind.INVARIANT),
        Axis("b", AxisKind.COVARIANT),
        Axis("c", AxisKind.CONTRAVARIANT))
    np.testing.assert_allclose(
        t.get_array("a", "b", "c", new("d")),
        src[:, :, :, np.newaxis])
    np.testing.assert_allclose(
        t.get_array("a", "b", new("d"), "c"),
        src[:, :, np.newaxis, :])
    np.testing.assert_allclose(
        t.get_array(new("d"), "a", "b", "c"),
        src[np.newaxis, :, :, :])
    np.testing.assert_allclose(
        t.get_array(new("d"), "a", new("e"), "b", "c", new("f")),
        src[np.newaxis, :, np.newaxis, :, :, np.newaxis])
...
```

## 1.2 Цепочки методов
```C++
...
class HelloTriangleApplication {
public:
    void run() {
        initWindow();
        initVulkan();
        mainLoop();
        cleanup();
    }
...
    void initVulkan() {
        createInstance();
        ...
    }
...
    void createInstance() {
        ...
    }
...
private:
    GLFWwindow* window;
    VkInstance instance;
...
```
Цепочка возникает потому, что весь низкоуровневый код свален в один класс,
и его надо хоть как-то структурировать.

Решение - инкапсулировать низкоуровневые сущности Vulkan и использовать RAII.
Тогда композиция классов сама обеспечит правильный порядок вызова конструкторов
и деструкторов.
```C++
class Window {
public:
    Window() {
        ...
    }

    ~Window() {
        ...
    }

    ...

private:
    GLFWwindow* window;
};

class Vulkan {
public:
    Vulkan() {
        ...
    }

    ~Vulkan() {
        vkDestroyInstance(instance, nullptr);
    }

private:
    VkInstance instance;
};


class HelloTriangleApplication {
public:
    void run() {
        mainLoop();
    }

private:
    Window window;
    VkInstance instance;
...
};
```
