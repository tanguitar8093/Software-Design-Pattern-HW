from typing import List
from models.observers.observers import DeathObserver

class Unit:
    def __init__(self, name: str, hp: int, mp: int, str_: int, is_hero: bool = False):
        self.name = name
        self.hp = hp
        self.mp = mp
        self.str = str_
        self.current_state = None  # to be initialized
        self.strategy = None
        self.skills = []
        self.observers: List[DeathObserver] = []
        self.is_hero = is_hero
        self.troop = None

    def take_damage(self, amt: int):
        self.hp -= amt
        if self.hp <= 0:
            self.hp = 0
            self.notify()

    def change_state(self, new_state):
        self.current_state = new_state
        self.current_state.on_round_begin(self)

    def attach(self, obs: DeathObserver):
        if obs not in self.observers:
            self.observers.append(obs)

    def notify(self):
        for obs in self.observers:
            obs.on_unit_death(self)
