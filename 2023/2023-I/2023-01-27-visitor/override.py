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


class Hero:
    weapon: str
    armor: str

    def get_weapon_damage(self) -> int:
        return weapon_damage[self.weapon]

    def get_armor_rating(self) -> int:
        return armor_rating[self.armor]

    def visit_tavern(self) -> list[str]:
        return ["eat", "drink"]


class Warrior(Hero):
    favorite_weapon: str

    def get_weapon_damage(self) -> int:
        if self.weapon == self.favorite_weapon:
            return int(weapon_damage[self.weapon] * 1.5)
        return weapon_damage[self.weapon]

    def visit_tavern(self) -> list[str]:
        return super().visit_tavern() + ["brawl"]


class Thief(Hero):

    def get_weapon_damage(self) -> int:
        if self.weapon == "dagger":
            return 10
        return weapon_damage[self.weapon]

    def visit_tavern(self) -> list[str]:
        return super().visit_tavern() + ["steal"]


class Bard(Hero):

    def get_weapon_damage(self) -> int:
        return int(weapon_damage[self.weapon] * 0.8)

    def visit_tavern(self) -> list[str]:
        return super().visit_tavern() + ["sing"]


class Shaman(Hero):

    def get_weapon_damage(self) -> int:
        return int(weapon_damage[self.weapon] * 0.7)

    def get_armor_rating(self) -> int:
        return 0

    def visit_tavern(self) -> list[str]:
        return super().visit_tavern() + ["meditate"]
