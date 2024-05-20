# Ясный код

## 1.1. Методы, которые используются только в тестах
```Python
class ValueNode:

    __input: Optional["ProcedureNode"]
    __outputs: set["ProcedureNode"]

    ...

    def get_input(self) -> Optional["ProcedureNode"]:
        return self.__input

    def get_outputs(self) -> set["ProcedureNode"]:
        return self.__outputs.copy()


class ProcedureNode:

    __inputs: dict[str, ValueNode]
    __outputs: dict[str, ValueNode]

    ...

    def get_inputs(self) -> dict[str, "ValueNode"]:
        return self.__inputs.copy()

    def get_outputs(self) -> dict[str, "ValueNode"]:
        return self.__outputs.copy()
```

Запросы `get_...` использовались только в тестах, потому что алгоритмы,
работающие с графом этих узлов, были распределены между методами внутри узлов.
Эти методы обращались к полям класса напрямую, поэтому запросы использовались
только в тестах, чтобы убедиться, что узлы связаны правильно.

Сначала такая распределённая реализация алгоритмов казалась хорошим решением,
так как задача разбивалась на подзадачи.
Однако, тут есть проблемы сразу на всех уровнях:
  - Во **время выполнения** при вызове метода одного из узлов происходят вызовы
    методов соседних узлов и т.д.
    В результате, сбой в работе узла на одном конце графа нарушает работу узла
    на другом конце.
    Отлаживать такое - врагу не пожелаешь.
  - На **уровне реализации** очень сложно собрать в голове код решения задачи,
    когда решения подзадач разбросаны по методам в разных классах.
    Разделённая реализация не отображает в коде единую логику алгоритма.
    И да, появляются *методы, которые используются только в тестах*.
  - На **уровне логики** оказалось очень сложно (если вообще возможно) построить
    чёткие математические формулировки пред- и постусловий методов.
    Предусловия вида "обновление входных узлов будет успешным",
    и постусловия вида "для выходных узлов вызван метод `invalidate`" -
    плохо поддаются верификации и дают мало информации о состоянии узла.
    Получается, что на уровне логики каждый объект содержит в себе весь граф,
    то есть, декомпозиция задачи не состоялась.

В новом коде в узлах осталась только логика связей и состояний самих узлов.
Теперь запросы связей используются внешними функциями, а не только тестами.


## 1.2. Цепочки методов
Вот другой срез кода из предыдущего примера:
```Python
class ValueNode:

    __input: Optional["ProcedureNode"]
    __outputs: set["ProcedureNode"]

    ...
    
    def put(self, value: Any) -> None:
        ...
        for output in self.__outputs:
            output.invalidate(self)
    
    def invalidate(self) -> None:
        ...
        for output in self.__outputs:
            output.invalidate(self)
    
    def validate(self) -> None:
        ...
        self.__input.validate()
        ...


class ProcedureNode:

    __inputs: dict[str, ValueNode]
    __outputs: dict[str, ValueNode]

    ...

    def invalidate(self, input: ValueNode) -> None:
        ...
        for output in self.__outputs.values():
            output.invalidate()

    def validate(self) -> None:
        ...
        for input in self.__inputs.values():
            input.validate()
        ...
        for name, output in self.__outputs.items():
            ...
            output.put(value)
            ...
```

Это больше, чем просто цепочка методов,
ЭТО распространяется на множество объектов.
Команды `validate` и `invalidate` вызывают аналогичные команды у соседних узлов
и далее, возможно, на всю глубину графа.

О недостатках такого решения написано выше.
Интересно, что это другое следствие той же самой ошибки на уровне логики.
Вывел для себя правило:
> Если логика решения плохо поддаётся математической формализации,
> нужно пересмотреть решение.

Поскольку источник проблемы тот же, то и лекарство то же -
вынести алгоритмы из классов узлов.


## 1.3. У метода слишком большой список параметров
```Python
class Simulator(Procedure):
    
    ...

    def __add_input(self,
            proc: ProcedureNode,
            slot_name: str,
            value: ValueNode
            ) -> None:
        ...

    def __add_output(self,
            proc: ProcedureNode,
            slot_name: str,
            value: ValueNode
            ) -> None:
        ...

```
Эти методы так выглядят из-за того, что связи в графе именованные,
и имена хранятся в одном из типов узлов.
Вообще, отдельные методы понадобились только потому, что нужно проверить,
есть ли у процедуры такой слот, подходит ли его тип и т.д.

Решение - вынести слоты в отдельные узлы, которые создаются на основе
информации о процедуре,
Они автоматически будут иметь правильные имена и типы.
Тогда параметр `slot_name` больше не нужен.
Также не нужны узлы-значения, потому что слоты связываются напрямую:
```Python
class Simulator(Procedure):
    
    ...

    def __link_slots(self,
            output: OutputNode,
            input: InputNode
            ) -> None:
        ...

```


# 1.4. Странные решения
```Python
class BulkHamiltonian:
    ...
    __data: NDArray[Shape["*, *, 4, 4"], Complex]
    ...

    def __init__(self, size: int, valence_size: int) -> None:
        ...

    @property
    def tensor(self) -> NDArray[Shape["*, *, 4, 4"], Complex]:
        return self.__data

    def __getitem__(self, indices: tuple[int, int]) -> NDArray[Shape["4, 4"], Complex]:
        ...
    
    def __setitem__(self, indices: tuple[int, int],
            value: list[list[complex]] | NDArray[Shape["4, 4"], Complex]) -> None:
        ...
```
Есть прямой доступ к данным, и есть методы чтения и записи по элементам.

По идее, после создания гамильтониан вообще не должен меняться,
и использовать его удобнее целиком как тензор,
чтобы была доступна вся мощь `NumPy`.
При этом нигде кроме тестов `__getitem__` не используется,
а все проверки, которые делает `__setitem__` можно перенести в конструктор.
```Python
class BulkHamiltonian:
    Tensor = NDArray[Shape["*, *, 4, 4"], Complex]
    
    ...
    __data: Tensor
    ...

    def __init__(self, tensor: Tensor, valence_size: int) -> None:
        ...

    def get_tensor(self) -> Tensor:
        return self.__data
```


# 1.5. Чрезмерный результат
```Python
class Procedure(Status):
    def get_input_slots(self) -> dict[str, type]:
        ...

...

if not _type_fits(input.get_type(), self.__proc.get_input_slots()[slot]):
    ...
```
Когда нам нужен только тип только одного слота, мы получаем их все.

Решение - добавить метод, для получения типа одного слота:

```Python
class Procedure(Status):
    def get_input_slots(self) -> dict[str, type]:
        ...

    def get_input_type(self, slot: str) -> type:
        ...

...

if not _type_fits(input.get_type(), self.__proc.get_input_type(slot)):
    ...
```
