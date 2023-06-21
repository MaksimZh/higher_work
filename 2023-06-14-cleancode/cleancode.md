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


## 1.3 У метода слишком большой список параметров
```Python
def wave(l, k, r, rRef, deriv = 0):
    if deriv == 0:
        rk = np.real(k)
        ik = np.abs(np.imag(k))
        kc = np.abs(rk) > ik
        kcr = np.logical_and(kc, rk > 0)
        kci = np.logical_and(kc, rk < 0)
        kr = k * r
        krRef = k * rRef
        krRef[kc] = 0
        w = np.sqrt(np.pi / ((2 + 0j) * kr)) \
            * sp.hankel1e(l + 1/2, kr) * np.exp(1j * (kr - krRef))
        w[kcr] = 1j * np.imag(w[kcr])
        w[kci] = np.real(w[kci])
        return w
    elif deriv == 1:
        return (l / r) * wave(l, k, r, rRef) - k * wave(l + 1, k, r, rRef)
    else:
        assert(False)
```
Много параметров, использование `elif` и `else`,
производные высокого порядка не нужны,
но можно запросить и нарваться на `assert`.

Используем функции высокого порядка:
```Python
def scaled_spherical_wave(k, rRef):
    rk = np.real(k)
    ik = np.abs(np.imag(k))
    kc = np.abs(rk) > ik
    kcr = np.logical_and(kc, rk > 0)
    kci = np.logical_and(kc, rk < 0)
    krRef = k * rRef
    krRef[kc] = 0

    def wave(l, r):
        kr = k * r
        w = np.sqrt(np.pi / ((2 + 0j) * kr)) \
            * sp.hankel1e(l + 1/2, kr) * np.exp(1j * (kr - krRef))
        w[kcr] = 1j * np.imag(w[kcr])
        w[kci] = np.real(w[kci])
        return w
    
    def deriv(l, r):
        return (l / r) * wave(l, r) - k * wave(l + 1, r)
    
    return wave, deriv
```
Больше нет `else` и с производной всё проще.


## 1.4 Несколько методов используются для решения одной и той же проблемы.
```Python
class FuncSpec:
    ...

    def get_input_ids(self) -> list[str]:
        return self.__input_ids
    
    def get_output_ids(self) -> list[str]:
        return self.__output_ids

    def get_input_spec(self) -> dict[str, type]:
        return self.__input_spec
    
    def get_output_spec(self) -> dict[str, type]:
        return self.__output_spec
```
Одна пара запросов возвращает ключи словаря, а другая - сами словари.

Разница всё же есть, поскольку нам важен порядок аргументов в функции,
поэтому в первых двух методах возвращаются именно списки, а не множества.

Однако, в коде уживаются вот такие конструкции:
```Python
if id in self.__spec.get_input_ids():
    ...
...
if not id in self.__spec.get_input_spec():
    ...
```
Для проверки принадлежности идентификатора списку аргументов
используются два разных метода.
И кстати, использование `get_input_spec` -
это уже и пункт 1.5 - чрезмерный результат.

Источник проблемы - недостаточная инкапсуляция `FuncSpec`.
Проверка того, что идентификатор принадлежит списку аргументов должна быть
именно в этом классе.

Парадокс, но для улучшения согласованности нужно **добавить** методы:
```Python
class FuncSpec:
    ...

    def get_input_ids(self) -> list[str]:
        return self.__input_ids
    
    def get_output_ids(self) -> list[str]:
        return self.__output_ids

    def get_input_spec(self) -> dict[str, type]:
        return self.__input_spec
    
    def get_output_spec(self) -> dict[str, type]:
        return self.__output_spec

    def has_input(self, id: str) -> bool:
        return id in self.__input_spec

    def has_output(self, id: str) -> bool:
        return id in self.__output_spec
```


## 1.5 Чрезмерный результат
```Python
def scaled_spherical_wave(k, rRef):
    rk = np.real(k)
    ik = np.abs(np.imag(k))
    kc = np.abs(rk) > ik
    kcr = np.logical_and(kc, rk > 0)
    kci = np.logical_and(kc, rk < 0)
    krRef = k * rRef
    krRef[kc] = 0

    def wave(l, r):
        kr = k * r
        w = np.sqrt(np.pi / ((2 + 0j) * kr)) \
            * sp.hankel1e(l + 1/2, kr) * np.exp(1j * (kr - krRef))
        w[kcr] = 1j * np.imag(w[kcr])
        w[kci] = np.real(w[kci])
        return w
    
    def deriv(l, r):
        return (l / r) * wave(l, r) - k * wave(l + 1, r)
    
    return wave, deriv
```
Возвращаем производную, а она нужна не всегда.

Сделаем две функции.
В качестве бонуса - у возвращаемых функций теперь ещё меньше параметров.
```Python
def scaled_spherical_wave(l, k, rRef):
    rk = np.real(k)
    ik = np.abs(np.imag(k))
    kc = np.abs(rk) > ik
    kcr = np.logical_and(kc, rk > 0)
    kci = np.logical_and(kc, rk < 0)
    krRef = k * rRef
    krRef[kc] = 0

    def wave(r):
        kr = k * r
        w = np.sqrt(np.pi / ((2 + 0j) * kr)) \
            * sp.hankel1e(l + 1/2, kr) * np.exp(1j * (kr - krRef))
        w[kcr] = 1j * np.imag(w[kcr])
        w[kci] = np.real(w[kci])
        return w
    
    return wave

def scaled_spherical_wave_deriv(l, k, rRef):

    wave0 = scaled_spherical_wave(l, k, rRef)
    wave1 = scaled_spherical_wave(l + 1, k, rRef)
    
    def deriv(r):
        return (l / r) * wave0(r) - k * wave1(r)
    
    return deriv
```
