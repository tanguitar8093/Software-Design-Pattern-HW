from __future__ import annotations
from typing import List
from models.actions.action import Action
from models.unit import Unit 
from models.observers.summoner_trait import SummonerTrait
class Summon(Action):
    def __init__(self):
        super().__init__("召喚", 150, 0, "none")
    def execute(self, actor: Unit, targets: List[Unit]):
        slime = Unit("Slime", 100, 0, 50, actor.is_hero)
        slime.troop = actor.troop
        slime.enemy_troop = actor.enemy_troop
        slime.attach(SummonerTrait(actor))
        # Add a BasicAttack to slime
        from models.actions.basic_attack import BasicAttack
        slime.skills.append(BasicAttack())
        from models.strategies.ai_strategy import AIStrategy
        slime.strategy = AIStrategy()
        actor.troop.append(slime)
