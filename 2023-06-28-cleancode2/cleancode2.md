# Ясный код - 2

# 2.1 Класс слишком большой
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


# 2.2 Класс слишком маленький


# 2.3 В классе есть метод, который выглядит более подходящим для другого класса
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
