# Божественная линия кода

## 1
```C++
if (vkCreateSwapchainKHR(device, &createInfo, nullptr, &swapChain) != VK_SUCCESS) {
    throw std::runtime_error("failed to create swap chain!");
}
```
В одной строке меняется состояние и происходит проверка
было ли это действие успешным.
```C++
VkResult result = vkCreateSwapchainKHR(device, &createInfo, nullptr, &swapChain);
if (result != VK_SUCCESS) {
    throw std::runtime_error("failed to create swap chain!");
}
```
Теперь есть переменная `result`.
Что если в функции много таких блоков?
Создавать переменные с разными именами?

Во-первых, нечего плодить такие блоки, там подготовка не маленькая,
каждый такой вызов заслуживает отдельной функции.

Во-вторых, можно давать переменным осмысленные названия: `swap_chain_creation_result`.


## 2
```C++
if (vkCreateSemaphore(device, &semaphoreInfo, nullptr, &imageAvailableSemaphore) != VK_SUCCESS ||
        vkCreateSemaphore(device, &semaphoreInfo, nullptr, &renderFinishedSemaphore) != VK_SUCCESS ||
        vkCreateFence(device, &fenceInfo, nullptr, &inFlightFence) != VK_SUCCESS) {
    throw std::runtime_error("failed to create semaphores!");
}
```
Трижды божественная линия :)

Типовые действия можно вынести в отдельные функции:
```C++
VkSemaphore createSemaphore(VkDevice device) {
    VkSemaphoreCreateInfo semaphoreInfo{};
    semaphoreInfo.sType = VK_STRUCTURE_TYPE_SEMAPHORE_CREATE_INFO;
    VkSemaphore semaphore;
    VkResult result = vkCreateSemaphore(device, &semaphoreInfo, nullptr, &semaphore);
    if (result != VK_SUCCESS) {
        throw std::runtime_error("failed to create semaphore!");
    }
    return semaphore;
}

VkFence createSignaledFence(VkDevice device) {
    VkFenceCreateInfo fenceInfo{};
    fenceInfo.sType = VK_STRUCTURE_TYPE_FENCE_CREATE_INFO;
    fenceInfo.flags = VK_FENCE_CREATE_SIGNALED_BIT;
    VkFence fence;
    VkResult result = vkCreateFence(device, &fenceInfo, nullptr, &fence);
    if (result != VK_SUCCESS) {
        throw std::runtime_error("failed to create fence!");
    }
    return fence;
}

...
// Такой код намного легче понять:
imageAvailableSemaphore = createSemaphore(device);
renderFinishedSemaphore = createSemaphore(device);
inFlightFence = createSignaledFence(device);
```


## 3
```Python
result = np.zeros((n,) + a.shape[1:] + b.shape[1:], dtype = np.common_type(a, b))
```
Из-за того, что вычисление размерностей массива засунуты в вызов конструктора,
пришлось долго вспоминать, что же они означают.
```Python
a_item_shape = a.shape[1:]
b_item_shape = b.shape[1:]
product_item_shape = a_item_shape + b_item_shape
product_type = np.common_type(a, b)
result = np.zeros((product_items_count,) + product_item_shape, dtype = product_type)
```


## 4
```Python
return TransferMatrices(
    Tensor(result_array, row_suffix, col_suffix),
    row_dir = right_wave.dir_axis + row_suffix,
    col_dir = left_wave.dir_axis + col_suffix)
```
Одновременно вызывается конструктор и вычисляются два параметра для него.
И кстати, это привело к ошибке: параметры для `Tensor` заданы не правильно.
```Python
row_dir_axis = right_wave.dir_axis + row_suffix
col_dir_axis = left_wave.dir_axis + col_suffix
return TransferMatrices(
    Tensor(result_array, row_dir_axis, col_dir_axis),
    row_dir=row_dir_axis, col_dir=col_dir_axis)
```

## 5
```Python
test = (np.linalg.inv(waves(kr).reshape(12, 12)) @ waves(kl).reshape(12, 12)).reshape(2, 2, 3, 2, 2, 3)
```
Формально эту строку можно разбить так,
чтобы слияние осей массивов выполнялись отдельно:
```Python
right_waves = waves(kr)
right_matrix = right_waves.reshape(12, 12)
left_waves = waves(kl)
left_matrix = left_waves.reshape(12, 12)
test_matrix = (np.linalg.inv(right_matrix) @ left_matrix)
test = test_matrix.reshape(2, 2, 3, 2, 2, 3)
```
Но это всё равно не очень хорошо.
В моём проекте для аккуратной работы с осями массивов
есть специальная абстракция - класс `Tensor`:
```Python
right_tensor = Tensor(waves(kr), "c", "deriv", "dir", "a", "b")
left_tensor = Tensor(waves(kl), "c", "deriv", "dir", "a", "b")
right_matrix = right_tensor.get_array(merge("c", "deriv"), merge("dir", "a", "b"))
left_matrix = left_tensor.get_array(merge("c", "deriv"), merge("dir", "a", "b"))
test_matrix = (np.linalg.inv(right_matrix) @ left_matrix)
test = test_matrix.reshape(2, 2, 3, 2, 2, 3)
```
