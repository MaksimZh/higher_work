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


## Перебор сущностей
Вот как происходит отрисовка спрайтов:
```Python
entities = world.get_entities({Sprite, ScreenPosition}, set())
while not entities.is_empty():
    e = entities.get_entity()
    sprite: Sprite = world.get_component(e, Sprite) #type: ignore
    pos: ScreenPosition = world.get_component(e, ScreenPosition) #type: ignore
    self.__screen.blit(sprite.source, (pos.x, pos.y), sprite.rect)
    entities.remove_entity(e)
```
Такой код часто встречается.
Перенесём цикл в класс `World`:
```Python
class World(Status):
    ...
    # Apply function to components of each entity
    # that have all of `with_components`
    # and none of `no_components`
    def process_entities(
            self,
            with_components: set[Type[Component]],
            no_components: set[Type[Component]],
            process: ProcessFunc
            ) -> None:
        entities = self.get_entities(with_components, no_components)
        while not entities.is_empty():
            e = entities.get_entity()
            self.__entities[e] = process(self.__entities[e])
            entities.remove_entity(e)
    ...
```
Тело цикла передаётся в виде функции, плюс мы сами извлекаем компоненты
и передаём в эту функцию не весь мир, а только компоненты обрабатываемой сущности.

Функция должна рассматривать эти компоненты как иммутабельные данные
и вернуть новый набор компонентов.
Программа стала чуть более функциональной и чуть менее императивной.
Как правило это хорошо.

Вот как теперь происходит рисование:
```Python
    world.process_entities({Sprite, ScreenPosition}, set(), self.__draw)
...

def __draw(self, components: ComponentDict) -> ComponentDict:
    sprite: Sprite = components[Sprite] #type: ignore
    pos: ScreenPosition = components[ScreenPosition] #type: ignore
    self.__screen.blit(sprite.source, (pos.x, pos.y), sprite.rect)
    return components
```

А вот что изменилось в управлении героем:

Было:
```Python
def run(self, world: World, frame_time: Timems) -> None:
    heroes = world.get_entities({Command, FieldPosition}, set())
    if heroes.is_empty():
        return
    hero = heroes.get_entity()
    command: Command = world.get_component(hero, Command) #type: ignore
    if command.single:
        world.remove_component(hero, Command)
    if world.has_component(hero, FieldMotion):
        return
    if world.has_component(hero, Step):
        return
    world.add_component(hero, Step(command.direction))
```

Стало:
```Python
def run(self, world: World, frame_time: Timems) -> None:
    world.process_entities({Command, FieldPosition}, set(), self.__process)

def __process(self, components: ComponentDict) -> ComponentDict:
    command: Command = components[Command] #type: ignore
    if command.single:
        del components[Command]
    if FieldMotion in components or Step in components:
        return components
    components[Step] = Step(command.direction)
    return components
```
Больше не нужен код для извлечения сущности героя из мира "вручную"
и проверка на успех этого мероприятия.


## Направление действия
При движении:
```Python
field: GameField = world.get_component(world.get_global_entity(), GameField) #type: ignore
if world.is_status("get_component", "NO_COMPONENT"):
    return
heroes = world.get_entities({Step, FieldPosition}, set())
if heroes.is_empty():
    return
hero = heroes.get_entity()
if world.has_component(hero, FieldMotion):
    return
position: FieldPosition = world.get_component(hero, FieldPosition) #type: ignore
step: Step = world.get_component(hero, Step) #type: ignore
target_position = calc_target(position, step.direction)
if field.is_cell_empty(target_position.x, target_position.y):
    world.add_component(hero, FieldMotion(step.direction, 0))
    return
```

При поглощении объекта:
```Python
field: GameField = world.get_component(world.get_global_entity(), GameField) #type: ignore
if world.is_status("get_component", "NO_COMPONENT"):
    return
heroes = world.get_entities({Step, FieldPosition}, set())
if heroes.is_empty():
    return
hero = heroes.get_entity()
if world.has_component(hero, FieldMotion):
    return
position: FieldPosition = world.get_component(hero, FieldPosition) #type: ignore
step: Step = world.get_component(hero, Step) #type: ignore
target_position = calc_target(position, step.direction)
if not field.is_cell_obstacle(target_position.x, target_position.y):
    return
target = field.get_cell_entity(target_position.x, target_position.y)
if not world.has_component(target, Consumable):
    return
world.add_component(hero, FieldMotion(step.direction, 0))
world.add_component(target, Consumed())
```

При выходе с уровня:
```Python
field: GameField = world.get_component(world.get_global_entity(), GameField) #type: ignore
if world.is_status("get_component", "NO_COMPONENT"):
    return
heroes = world.get_entities({Step, FieldPosition}, set())
if heroes.is_empty():
    return
hero = heroes.get_entity()
if world.has_component(hero, FieldMotion):
    return
position: FieldPosition = world.get_component(hero, FieldPosition) #type: ignore
step: Step = world.get_component(hero, Step) #type: ignore
target_position = calc_target(position, step.direction)
if not field.is_cell_obstacle(target_position.x, target_position.y):
    return
target = field.get_cell_entity(target_position.x, target_position.y)
if not world.has_component(target, Exit):
    return
self.__end = True
```

Общий паттерн: найти соседнюю сущность и предпринять определённые действия
в зависимости от того, есть ли она и что это.
Для этого нужно ещё и найти глобальный компонент `GameField`.

Решение - вынести поиск и проверку цели в отдельную систему.
Тогда получаем следующее:

При движении:
```Python
def process(components: ComponentDict) -> ComponentDict:
    step: Step = components[Step] #type: ignore
    components[FieldMotion] = FieldMotion(step.direction, 0)
    return components

world.process_entities(
    with_components={Step, FieldPosition, EmptyTarget},
    no_components={FieldMotion},
    process=process)
```

При поглощении объекта:
```Python
def process(components: ComponentDict) -> ComponentDict:
    step: Step = components[Step] #type: ignore
    target_component: Target = components[Target] #type: ignore
    target = target_component.target
    if not world.has_component(target, Consumable):
        components[FieldMotion] = FieldMotion(step.direction, 0)
        world.add_component(target, Consumed())
    return components

world.process_entities(
    with_components={Step, FieldPosition, Target},
    no_components={FieldMotion},
    process=process)
```
Здесь, напрашивается паттерн для обработки пары объектов.

При выходе с уровня:
```Python
def process(components: ComponentDict) -> ComponentDict:
    target_component: Target = components[Target] #type: ignore
    target = target_component.target
    if world.has_component(target, Exit):
        self.__end = True
    return components

world.process_entities(
    with_components={Step, FieldPosition, Target},
    no_components={FieldMotion},
    process=process)
```


# Выводы
Подход ECS очень гибкий, но очень низкоуровневый, и подразумевает работу
с глобальным мутабельным состоянием.

Из-за низкоуровневости возникает много повторяющихся конструкций в коде.
При выполнении этого задания часть из них была заменена на более простые
и наглядные конструкции.

При этом в двух случаях применены функции высшего порядка, что делает код
более функциональным.
При этом работа с глобальным состоянием локализуется в более низкоуровневых
модулях.

В последнем задании, например, куча проверок просто сводится к передаче
параметров фильтров `(with_components=..., no_components=...)`.

Вероятно при увеличении знаний по ФП можно вообще обернуть всё ECS
в функциональный интерфейс и сделать логику игры декларативной.
