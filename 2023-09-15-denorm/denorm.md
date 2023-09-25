# Как найти смысл данных в вашем проекте - 1

```Python
class World(Status):
    
    __global_entity: Entity
    __entities: dict[Entity, dict[Type[Component], Component]]

...

    # Get set of entities that have all of `with_components`
    # and none of `no_components`
    def get_entities(
            self,
            with_components: set[Type[Component]],
            no_components: set[Type[Component]]
            ) -> "EntitySet":
        ...
```
Доступ к сущностям, содержащим определённый набор компонентов,
требуется очень часто.
Для ускорения такого поиска можно продублировать связь между
сущностями и компонентами.
Самый простой способ - хранить множества (`set`) сущностей для каждого
типа компонентов:
```Python
class World(Status):
    
    __global_entity: Entity
    __entities: dict[Entity, dict[Type[Component], Component]]
    __component_types: dict[Type[Component], set[Entity]]

...

    # Get set of entities that have all of `with_components`
    # and none of `no_components`
    def get_entities(
            self,
            with_components: set[Type[Component]],
            no_components: set[Type[Component]]
            ) -> "EntitySet":
        ...
```
Тогда метод `get_entities` сможет использовать операции с множествами
для быстрого извлечения нужных компонентов.

У такой системы есть два недостатка.
Во-первых, при добавлении компонентов нужно обновлять не только поле
`__entities`, но и поле `__component_types`, что повышает хрупкость системы.
Во-вторых, в классе `World` теперь три поля, что нарушает
Object Calisthenics пункт 8:
"В классе должно быть не более двух полей (атрибутов)".

На уровне логики концепция глобальной сущности слабо связана фундаментальной
концепцией сущностей и компонентов.
Поэтому логично будет вынести `__entities` и `__component_types`
в отдельный АТД, который будет инкапсулировать всю работу с добавлением
и удалением компонентов.
Это, кстати, снизит хрупкость системы:
```Python
class EntityComponentPack(Status):
    __entities: dict[Entity, dict[Type[Component], Component]]
    __component_types: dict[Type[Component], set[Entity]]

    # Get set of entities that have all of `with_components`
    # and none of `no_components`
    def get_entities(
            self,
            with_components: set[Type[Component]],
            no_components: set[Type[Component]]
            ) -> "EntitySet":
        ...
    
    ...


class World(Status):
    
    __global_entity: Entity
    __ecp: EntityComponentPack

...

    # Get set of entities that have all of `with_components`
    # and none of `no_components`
    def get_entities(
            self,
            with_components: set[Type[Component]],
            no_components: set[Type[Component]]
            ) -> "EntitySet":
        return self.__ecp.get_entities(with_components, no_components)
```


## Резюме
Денормализация, на первый взгляд, портит систему, добавляя хрупкость
и требуя дополнительной работы для сохранения внутренней согласованности данных
(их соответствия спецификации).
Тем не менее, в данном конкретном случае эта операция как бы подсветила
то место в системе, где разная логика была смешана в одном АТД.

Класс `World` отвечал и за компоненты и за глобальную сущность.
Комбинированное применение денормализации и Object Calisthenics
улучшило архитектуру системы.
Теперь за компоненты и сущности отвечает `EntityComponentPack`,
а `World` отвечает за игровой мир.
По логике игры сущности делятся на два класса:
сущность самой игры / мира (глобальная) и сущности игровых объектов.

Разные уровни логики (реализация ECS и игровой мир) разнесены в разные АТД.
При этом композиция АТД соответствует взаимному расположению уровней логики:
детали реализации (`EntityComponentPack`)
внутри элемента предметной области (`World`).
Это прекрасно!
