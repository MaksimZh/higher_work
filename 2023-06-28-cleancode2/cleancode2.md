# Ясный код - 2

## 2.1 Класс слишком большой
```C++
class HelloTriangleApplication {
public:
    void run() {
        initWindow();
        initVulkan();
        mainLoop();
        cleanup();
    }

private:
    GLFWwindow* window;

    VkInstance instance;
    VkDebugUtilsMessengerEXT debugMessenger;
    VkSurfaceKHR surface;

    VkPhysicalDevice physicalDevice = VK_NULL_HANDLE;
    VkDevice device;

    VkQueue graphicsQueue;
    VkQueue presentQueue;

    VkSwapchainKHR swapChain;
    std::vector<VkImage> swapChainImages;
    VkFormat swapChainImageFormat;
    VkExtent2D swapChainExtent;
    std::vector<VkImageView> swapChainImageViews;
    std::vector<VkFramebuffer> swapChainFramebuffers;

    VkRenderPass renderPass;
    VkPipelineLayout pipelineLayout;
    VkPipeline graphicsPipeline;

    VkCommandPool commandPool;
    std::vector<VkCommandBuffer> commandBuffers;

    std::vector<VkSemaphore> imageAvailableSemaphores;
    std::vector<VkSemaphore> renderFinishedSemaphores;
    std::vector<VkFence> inFlightFences;
    uint32_t currentFrame = 0;

    bool framebufferResized = false;

    ... // ещё более 800 строк кода
};
```
Этот учебный пример рос постепенно, но уже с самого начала напрашивался
вынос обёрток для его полей в отдельные классы и использование RAII.


## 2.2 Класс слишком маленький или делает слишком мало
```Python
@final
class WaveAxes:
    __dir: str
    __extra: set[str]

    def __init__(self, dir: str, extra: set[str]) -> None:
        assert dir not in extra
        self.__dir = dir
        self.__extra = extra

    @property
    def direction(self) -> str:
        return self.__dir

    @property
    def extra(self) -> set[str]:
        return self.__extra

    @property
    def all(self) -> set[str]:
        return {self.__dir} | self.__extra


@final
class WaveMatrixAxes:
    __wave: WaveAxes
    __component: set[str]

    def __init__(self, wave: WaveAxes, components: set[str]) -> None:
        assert len(wave.all & components) == 0
        self.__wave = wave
        self.__component = components

    @property
    def wave(self) -> WaveAxes:
        return self.__wave

    @property
    def component(self) -> set[str]:
        return self.__component

    @property
    def all(self) -> set[str]:
        return self.__wave.all | self.__component
```
Фактически, это просто группировка строковых значений с дополнительной функцией,
которая их все упаковывает в одно множество.
Такая функция, правда, в проекте уже есть: `to_str_set`.

Вместо того, чтобы создавать вручную два класса, и потом тестировать их,
воспользуемся средствами стандартной библиотеки и уже готовой функцией `to_str_set`:
```Python
@final
class WaveAxes(NamedTuple):
    direction: str
    extra: set[str]

@final
class WaveMatrixAxes(NamedTuple):
    wave: WaveAxes
    component: set[str]
```


## 2.3 В классе есть метод, который выглядит более подходящим для другого класса
```Python
class BandHamiltonian:
    ...
    
    @property
    def operator(self) -> Operator: ...
    
    @property
    def band_axes(self) -> tuple[str, str]: ...

    @property
    def valence_band_size(self) -> int: ...
```
Вроде бы логично хранить информацию о физическом смысле
определённых осей (размерностей) массива в классе вместе с этим массивом.
Однако, для этого уже есть более общий класс `Operator`,
который хранит ссылки на информацию о некоторых осях.
Вот из этой информации и нужно получать `band_axes` и `valence_band_size`.

Тогда единственной функцией класса `Hamiltonian` будет убедиться, что
оператор имеет правильные оси.
Поскольку объекты обоих классов задуманы как иммутабельные, это достаточно
сделать один раз - в конструкторе.

## 2.4. Класс хранит данные, которые загоняются в него в множестве разных мест в программе
```Python
class World:
    ...

    def add_entity(self, entity: Entity) -> None: ...
    def add_component(self, entity: Entity, component: Component) -> None: ...
    def remove_entity(self, entity: Entity) -> None: ...
    def remove_component(self, entity: Entity, component_type: Type[Component]) -> None: ...

    def is_empty(self) -> bool: ...
    def has_entity(self, entity: Entity) -> bool: ...
    def new_entity(self) -> Entity: ...
    def has_component(self, entity: Entity, component_type: Type[Component]) -> bool: ...
    def get_component(self, entity: Entity, component_type: Type[Component]) -> Component: ...
    def get_entities(self, with_components: set[Type[Component]], no_components: set[Type[Component]]) -> "EntitySet": ...    
    def get_single_entity(self, with_components: set[Type[Component]]) -> Entity: ...
```
Этот класс - хранилище сущностей и компонентов в игре.

Фактически это глобальное состояние с огромным количеством степеней свободы.

Даже в C и ассемблере память лучше защищена от ошибок работы с состояниями,
чем объект класса `World`.


## 2.5. Класс зависит от деталей реализации других классов
Жизненное :)
```Python
class Voenkomat:
    __main_storage: dict[Name, PersonalFile]
    __medical_dep_storage: dict[Name, PersonalFile]

    def get_personal_file(name: Name, storage: Literal["main", "medical"] = "main") -> PersonalFile:
        if storage == "medical":
            return self.__medical_dep_storage[name]
        return self.__main_storage[name]

class Citizen:
    __name: Name
    __health_category: HealthCategory

    def checkout(voenkomat: Voenkomat) -> None:
        storage = "main" if self.__health_category == HealthCategory.OK else "medical"
        personal_file = voenkomat.get_personal_file(self.name, storage)
        ...
```


## 2.6. Приведение типов вниз по иерархии
```Python
class World(Status):
    ...
    
    __entities: dict[Entity, dict[Type[Component], Component]]

    ...

    @status("OK", "NO_ENTITY", "NO_COMPONENT")
    def get_component(self, entity: Entity, component_type: Type[Component]) -> Component:
        if not self.has_entity(entity):
            self._set_status("get_component", "NO_ENTITY")
            return Component()
        if not self.has_component(entity, component_type):
            self._set_status("get_component", "NO_COMPONENT")
            return Component()
        self._set_status("get_component", "OK")
        return self.__entities[entity][component_type]
```
Все компоненты свалены в хранилище под общим родительским типом `Component`.
Поэтому приходится делать так:
```Python
position: FieldPosition = world.get_component(hero, FieldPosition) #type: ignore
step: Step = world.get_component(hero, Step) #type: ignore
```
Проблема в том, что здесь типы - это ключи хранилища,
и нет проверки типа, например, через `isinstance`.
То есть тип не проверяется ни линтером, ни в рантайме,
пока не нарвёмся на несуществующий атрибут.
Это в лучшем случае. В худшем - будем работать не с тем типом, который ожидали.


## 2.7. Требуется создавать классы-наследники для нескольких классов одновременно
```Python
class ODESystem(ABC):

    @abstractmethod
    def get_validity_segment(self) -> tuple[float, float]:
        assert False

    @abstractmethod
    def get_dimension(self) -> int:
        assert False

class PolynomialODESystem(ODESystem):

    def get_validity_segment(self) -> tuple[float, float]:
        ...

    def get_dimension(self) -> int:
        ...

    # Возвращает многочлены для вычисления коэффициентов
    def get_ode_coefs_poly(self) -> Any:
        ...

class InterpolatedODESystem(ODESystem):

    def get_validity_segment(self) -> tuple[float, float]:
        ...

    def get_dimension(self) -> int:
        ...

    # Вычисляет коэффициенты в заданной точке
    def eval_ode_coefs(self, x: float) -> Any:
        ...

# Ради этого солвера нужны коэффициенты в виде многочленов
class FrobeniusSolver:
    ...

    def __init__(self, ode: PolynomialODESystem):
        ...
    
    def solve(self, x0: float) -> PolynomialSolution:
        ...

class EulerSolver(ABC):
    ...

    @abstractmethod
    def solve(self, xa: float, xb: float) -> Solution:
        pass

# Нужно по-разному вычислять коэффициенты уравнений

class PolynomialEulerSolver(EulerSolver):
    ...

    def __init__(self, ode: PolynomialODESystem):
        ...

    def solve(self, xa: float, xb: float) -> Solution:
        ...
        poly = self.__ode.get_ode_coefs_poly()
        c = poly.eval(x)
        ...


class InterpolatedEulerSolver(EulerSolver):
    ...

    def __init__(self, ode: InterpolatedODESystem):
        ...

    def solve(self, xa: float, xb: float) -> Solution:
        ...
        c = self.__ode.eval_ode_coefs(x)
        ...
```

Здесь лучше вынести метод `eval_ode_coefs` в родительский класс `ODESystem`.
Тогда классы-наследники `EulerSolver` вообще не понадобятся:
```Python
class EulerSolver:
    ...

    def __init__(self, ode: ODESystem):
        ...

    def solve(self, xa: float, xb: float) -> Solution:
        ...
        c = self.__ode.eval_ode_coefs(x)
        ...
```


## 2.8. Дочерние классы не используют или переопределяют методы и атрибуты родительских классов
```Python
```


## 3.1. Одна модификация требует внесения изменений в несколько классов


## 3.2. Использование сложных паттернов проектирования
