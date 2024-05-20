# Истинное наследование
В игре есть 4 вида персонажей, каждый со своими особенностями.
Например, воин хорошо владеет любимым оружием,
а шаман принципиально не использует доспехи.

В результате, для каждого элемента игровой механики нужно переопределять
методы родительского класса `Hero` в некоторых классах-потомках:
[override.py](override.py).

В примере таких методов 3, но в реальной игре их было бы несколько десятков.
Недостаток этого кода в том, что каждый элемент игровой механики
размазан по 5 классам (родитель + 4 потомка).
Из-за этого при чтении кода трудно собрать в голове эту механику,
а при добавлении новых аспектов игры требуются правки в 5 местах.

С помощью паттерна Visitor каждый элемент логики игры
можно локализовать в отдельном классе: [visitor.py](visitor.py).

Теперь для добавления, например, обработки посещения города нужно создать класс
`TownActionsSelector` с 4 методами, а не вносить изменения в 5 классов.

С другой стороны, если мы захотим добавить другие виды персонажей,
то тогда придётся добавлять методы в каждый класс-посетитель.
Поэтому такая архитектура хороша только если набор видов пергонажей
гораздо реже подвергается изменениям, чем набор игровых механик.

Если же и то и другое одинаково нестабильно,
лучше использовать популярный в играх подход Entity-Component-System,
который уже ближе к ФП.
Черновой вариант:
```Python
class Entity:
    components: dict[type, object]
    ...

# оружие

class Weapon:
    ...

class WeaponDamageModifier:
    ...

class FavoriteWeaponDamageModifier(WeaponDamageModifier):
    ...

class FactorWeaponDamageModifier(WeaponDamageModifier):
    ...

def get_weapon_damage(hero: Entity) -> int:
    if Weapon not in hero.components:
        return 0
    damage = hero.components[Weapon].get_damage()
    if WeaponDamageModifier not in hero.components:
        return damage
    return hero.components[WeaponDamageModifier].modify(damage)

# броня

...

# персонажи

def new_warrior() -> Entity:
    warrior = Entity()
    warrior.components[Weapon] = Weapon()
    warrior.components[WeaponDamageModifier] = FavoriteWeaponDamageModifier("sword")
    warrior.components[Armor] = Armor()
    warrior.components[ArmorRaitingModifier] = NormalArmorRaitingModifier()
    ...
    return warrior

def new_shaman():
    shaman = Entity()
    shaman.components[Weapon] = Weapon()
    shaman.components[WeaponDamageModifier] = FactorWeaponDamageModifier(0.7)
    # брони нет вообще
    # зато есть магия
    shaman.components[Spells] = MasterSpells()
    ...
    return shaman
```

Теперь наш `Visitor` - это не класс, а функция,
которая "посещает" не разные типы персонажей,
а только свои "родные" компоненты,
из которых персонаж собирается как конструктор.

В отличие от классического [visitor.py](visitor.py),
часть знаний об оружии и броне снова перекочевала к персонажам.
Однако, здесь эти связи гораздо лучше локализованы,
чем в [override.py](override.py), и оформлены в декларативном стиле.
