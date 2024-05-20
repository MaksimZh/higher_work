from abc import ABC, abstractmethod

armor_rating = {
    "": 0,
    "chainmail": 10,
    "platemail": 20,
}

weapon_damage = {
    "": 2,
    "dagger": 5,
    "sword": 10,
    "pike": 15,
}


class Hero(ABC):
    weapon: str
    armor: str

    @abstractmethod
    def accept(self, visitor: "Visitor") -> None:
        pass


class Warrior(Hero):
    favorite_weapon: str

    def accept(self, visitor: "Visitor") -> None:
        visitor.visit_warrior(self)


class Thief(Hero):

    def accept(self, visitor: "Visitor") -> None:
        visitor.visit_thief(self)


class Bard(Hero):

    def accept(self, visitor: "Visitor") -> None:
        visitor.visit_bard(self)


class Shaman(Hero):

    def accept(self, visitor: "Visitor") -> None:
        visitor.visit_shaman(self)


class Visitor(ABC):
        
    @abstractmethod
    def visit_warrior(self, warrior: Warrior) -> None:
        pass

    @abstractmethod
    def visit_thief(self, thief: Thief) -> None:
        pass

    @abstractmethod
    def visit_bard(self, bard: Bard) -> None:
        pass

    @abstractmethod
    def visit_shaman(self, shaman: Shaman) -> None:
        pass


class WeaponDamageCalculator(Visitor):

    damage: int

    def visit_warrior(self, warrior: Warrior) -> None:
        if warrior.weapon == warrior.favorite_weapon:
            self.damage = int(weapon_damage[warrior.weapon] * 1.5)
            return
        self.damage = weapon_damage[warrior.weapon]

    def visit_thief(self, thief: Thief) -> None:
        if thief.weapon == "dagger":
            self.damage = 10
            return
        self.damage = weapon_damage[thief.weapon]

    def visit_bard(self, bard: Bard) -> None:
        self.damage = int(weapon_damage[bard.weapon] * 0.8)

    def visit_shaman(self, shaman: Shaman) -> None:
        self.damage = int(weapon_damage[shaman.weapon] * 0.7)


class ArmorRatingCalculator(Visitor):

    rating: int

    def visit_default(self, hero: Hero) -> None:
        self.rating = armor_rating[hero.armor]

    def visit_warrior(self, warrior: Warrior) -> None:
        self.visit_default(warrior)

    def visit_thief(self, thief: Thief) -> None:
        self.visit_default(thief)

    def visit_bard(self, bard: Bard) -> None:
        self.visit_default(bard)

    def visit_shaman(self, shaman: Shaman) -> None:
        self.rating = 0


class TavernActionsSelector(Visitor):

    actions: list[str]
    common_actions = ["eat", "drink"]

    def visit_warrior(self, warrior: Warrior) -> None:
        self.actions = self.common_actions + ["brawl"]

    def visit_thief(self, thief: Thief) -> None:
        self.actions = self.common_actions + ["steal"]

    def visit_bard(self, bard: Bard) -> None:
        self.actions = self.common_actions + ["sing"]

    def visit_shaman(self, shaman: Shaman) -> None:
        self.actions = self.common_actions + ["meditate"]
