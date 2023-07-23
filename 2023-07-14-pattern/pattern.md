# Абстрагируем управляющие паттерны

## Единственный компонент
Игровое поле:
```Python
field = GameField(len(level[0]), len(level))
e = world.new_entity()
world.add_component(e, field)
...
field_entity = world.get_single_entity({GameField})
field: GameField = world.get_component(field_entity, GameField) #type: ignore
```
Размеры экрана:
```Python
screen = world.new_entity()
width, height = self.__screen.get_size()
world.add_component(screen, ScreenSize(width, height))
...
screen_size_entity = world.get_single_entity({ScreenSize})
screen_size: ScreenSize = world.get_component(screen_size_entity, ScreenSize) #type: ignore
```

В обоих случаях создаётся сущность для хранения ровно одного компонента.
Для того, чтобы находить такие сущности к АТД `World`
был даже добавлен отдельный запрос `get_single_entity`.

На уровне логики работа с сущностями и с данными - это разные вещи.
На уровне кода они смешались потому, что для упрощения хотелось свести всё
к ограниченному набору операций с сущностями и компонентами.

Тем не менее это усложнило интерфейс, так как появилась операция
`get_single_entity` предназначение которой неочевидно
вне контекста использования.
Таким образом, АТД `World` всё равно содержит методы, которые выходят за рамки
чистого ECS.

Лучше явно ввести на уровне кода глобальные компоненты, которые уже
присутствуют на уровне логики.
Наиболее изящный (на мой взгляд) способ сделать это -
ввести единственную глобальную сущность.
Это просто сводится к изменению сигнатуры метода `get_single_entity`.

Было:
```Python
class World(Status):
    ...
    # Get single entity that have all of `with_components`
    # PRE: such entity exists
    @status("OK", "NOT_FOUND")
    def get_single_entity(
            self,
            with_components: set[Type[Component]],
            ) -> Entity:
        ...
```
Стало:
```Python
class World(Status):
    ...
    # Get special entity to store global data
    def get_global_entity(self) -> Entity:
        ...
```
Теперь этот метод не требует входных данных и всегда выполняется успешно.

Новое игровое поле:
```Python
field = GameField(len(level[0]), len(level))
world.add_component(world.get_global_entity(), field)
...
field: GameField = world.get_component(world.get_global_entity(), GameField) #type: ignore
```
Новые размеры экрана:
```Python
width, height = self.__screen.get_size()
world.add_component(world.get_global_entity(), ScreenSize(width, height))
...
screen_size: ScreenSize = world.get_component(world.get_global_entity(), ScreenSize) #type: ignore
```

Итак, и для сохранения и для чтения глобальных данных
теперь нужно вдвое меньше кода.