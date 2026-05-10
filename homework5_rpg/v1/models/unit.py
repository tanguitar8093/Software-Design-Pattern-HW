from .state import State

class Unit:
    def __init__(self, name, hp, mp, str_, player):
        self.name = name
        self.hp = hp
        self.mp = mp
        self.str = str_
        self.state = State()
        self.player = player
        self.skills = ["BasicAttack", "Waterball", "Fireball", "SelfHealing", "Petrochemical", "Poison", "Summon", "SelfExplosion", "Cheerup", "Curse", "OnePunch"]
        self.is_dead = False
        self.troop = None

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.is_dead = True
            print(f"{self.name} died.")
