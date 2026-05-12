from __future__ import annotations
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from models.actions.action import Action

class Unit:
    def __init__(self, name: str, hp: int, mp: int, str_: int, is_hero: bool = False):
        self.name = name
        self.hp = hp
        self.mp = mp
        self.str = str_
        self.is_hero = is_hero
        
        from models.states.normal_state import NormalState
        from models.strategies.decision_strategy import DecisionStrategy
        self.current_state = NormalState()
        self.strategy: DecisionStrategy | None = None
        self.skills: List[Action] = []
        self.observers = []
        self.troop: List[Unit] = []
        self.enemy_troop: List[Unit] = []

    def attack(self, target: Unit):
        self.cause_damage(target, self.str)

    def cause_damage(self, target: Unit, amount: int):
        from models.states.cheered_up_state import CheeredUpState
        bonus = 0
        if isinstance(self.current_state, CheeredUpState):
            bonus = 50
        print(f"[{self.troop_id}]{self.name} 對 [{target.troop_id}]{target.name} 造成 {amount + bonus} 點傷害。")
        target.take_damage(amount + bonus)

    def take_damage(self, amt: int):
        if self.hp <= 0: return
        self.hp -= amt
        if self.hp <= 0:
            self.hp = 0
            print(f"[{self.troop_id}]{self.name} 死亡。")
            self.notify()

    def heal(self, amt: int):
        if self.hp > 0:
            self.hp += amt

    def change_state(self, new_state):
        self.current_state = new_state

    def attach(self, obs):
        if obs not in self.observers:
            self.observers.append(obs)

    def notify(self):
        for obs in self.observers:
            obs.on_unit_death(self)
