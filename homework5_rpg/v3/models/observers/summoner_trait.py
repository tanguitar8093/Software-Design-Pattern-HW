from models.observers.death_observer import DeathObserver
from models.unit import Unit


class SummonerTrait(DeathObserver):
    def __init__(self, master: Unit) -> None:
        self.master = master

    def on_unit_death(self, dead_unit: Unit) -> None:
        if self.master.hp > 0:
            self.master.hp += 30
