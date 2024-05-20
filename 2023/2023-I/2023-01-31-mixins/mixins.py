class Hero:
    pass


weapon_damage = {
    "": 2,
    "dagger": 5,
    "sword": 10,
    "pike": 15,
}


# Миксин
# Добавляет оружие и расчёт урона
class WeaponHolder:
    
    __weapon: str

    def __init__(self) -> None:
        super().__init__()  # super() - не родитель, а следующий в MRO
        self.__weapon = ""

    def set_weapon(self, weapon: str) -> None:
        self.__weapon = weapon

    def get_weapon(self) -> str:
        return self.__weapon

    def get_damage(self) -> int:
        return weapon_damage[self.__weapon]


# Миксин
# Добавляет любимое оружие и модифицирует расчёт урона
# Должен всегда идти перед WeaponHolder в списке базовых классов,
# иначе в super() не найдётся метода get_damage() 
class FavoriteWeaponDamageModifier:

    __favorite_weapon: str

    def __init__(self) -> None:
        super().__init__()  # super() - не родитель, а следующий в MRO
        self.__favorite_weapon = ""

    def set_favorite_weapon(self, favorite_weapon: str) -> None:
        self.__favorite_weapon = favorite_weapon

    def get_damage(self) -> int:
        damage = super().get_damage()  # super() - не родитель, а следующий в MRO
        if self.get_weapon() == self.__favorite_weapon:
            return damage * 2
        return damage


# Миксин
# Добавляет любимое оружие и модифицирует расчёт урона
# Должен всегда идти перед WeaponHolder в списке базовых классов
# иначе в super() не найдётся метода get_damage() 
class FactorWeaponDamageModifier:

    __factor: float

    def __init__(self) -> None:
        super().__init__()  # super() - не родитель, а следующий в MRO
        self.__factor = 1

    def set_weapon_damage_factor(self, factor: float) -> None:
        self.__factor = factor

    def get_damage(self) -> int:
        damage = super().get_damage()  # super() - не родитель, а следующий в MRO
        return int(damage * self.__factor)


# Два миксина действуют вместе
# Вызов метода get_damage:
# FavoriteWeaponDamageModifier -> WeaponHolder
class Warrior(FavoriteWeaponDamageModifier, WeaponHolder, Hero):
    
    def __init__(self) -> None:
        super().__init__()
        self.set_favorite_weapon("sword")

warrior = Warrior()
warrior.set_weapon("dagger")
print(warrior.get_damage()) # 5 - обычный урон
warrior.set_weapon("sword")
print(warrior.get_damage()) # 20 - двойной урон любимым оружием


# Два миксина действуют вместе
# Вызов метода get_damage:
# FactorWeaponDamageModifier -> WeaponHolder
class Shaman(FactorWeaponDamageModifier, WeaponHolder, Hero):
    
    def __init__(self) -> None:
        super().__init__()
        self.set_weapon_damage_factor(0.5)

shaman = Shaman()
shaman.set_weapon("dagger")
print(shaman.get_damage()) # 2 - половинный урон
shaman.set_weapon("sword")
print(shaman.get_damage()) # 5 - половинный урон


# Три миксина действуют вместе
# Вызов метода get_damage:
# FactorWeaponDamageModifier -> FavoriteWeaponDamageModifier -> WeaponHolder
class Veteran(FactorWeaponDamageModifier, FavoriteWeaponDamageModifier, WeaponHolder, Hero):
    
    def __init__(self) -> None:
        super().__init__()
        self.set_favorite_weapon("sword")
        self.set_weapon_damage_factor(1.5)

veteran = Veteran()
veteran.set_weapon("dagger")
print(veteran.get_damage()) # 7 - полуторный урон
veteran.set_weapon("sword")
print(veteran.get_damage()) # 30 - полуторный урон от двойного урона любимым оружием
