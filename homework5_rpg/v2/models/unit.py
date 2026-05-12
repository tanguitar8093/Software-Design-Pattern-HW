from .state import NormalState

class Unit:
    def __init__(self, name, hp, mp, str_, player):
        self.name = name
        self.hp = hp
        self.mp = mp
        self.str = str_
        self.state = NormalState()
        self.player = player
        self.is_dead = False
        self.troop = None
        self.skills = []
        self.observers = []

    def set_state(self, new_state):
        self.state = new_state

    def take_damage(self, amount):
        if self.is_dead: return
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            self.is_dead = True
            print(f"{self.name} died.")
            self.notify_death()

    def attach_death_observer(self, observer):
        if observer not in self.observers:
            self.observers.append(observer)

    def notify_death(self):
        for obs in self.observers:
            obs.on_target_dead(self, self.mp)
        self.mp = 0
