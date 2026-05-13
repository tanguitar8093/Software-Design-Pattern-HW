from models.actions.action import Action
from models.actions.basic_attack import BasicAttack
from models.observers.summoner_trait import SummonerTrait
from models.strategies.ai_strategy import AIStrategy
from models.unit import Unit


class Summon(Action):
    def __init__(self) -> None:
        super().__init__("召喚", 150, 0, "none")

    def execute(self, actor: Unit, targets: list[Unit]) -> None:
        print(f"[{actor.troop_id}]{actor.name} 使用了 召喚。")

        slime = Unit("Slime", 100, 0, 50, actor.is_hero)
        slime.troop = actor.troop
        slime.enemy_troop = actor.enemy_troop
        slime.troop_id = actor.troop_id
        slime.attach(SummonerTrait(actor))
        slime.skills.append(BasicAttack())
        slime.strategy = AIStrategy()
        actor.troop.append(slime)
