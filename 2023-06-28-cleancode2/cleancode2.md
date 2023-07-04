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
