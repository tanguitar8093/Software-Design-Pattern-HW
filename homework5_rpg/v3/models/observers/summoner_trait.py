from __future__ import annotations
from models.unit import Unit
from models.observers.death_observer import DeathObserver

class SummonerTrait(DeathObserver):
    def __init__(self, master: Unit):
        self.master = master

    def on_unit_death(self, dead_unit: Unit):
        pass # Spec requirement: Slime death can be observed. Spec doesn't strictly say heal, but the text said "回復血量？", let's assume it restores 30 HP to master, or just print it.
        # Actually spec says: "史萊姆死亡這件事情應該要能夠被觀察，因此觸發：【召喚使(Summoner) 血量回復】？"
        # Since it's a question in the description, we will heal 30 to be safe.
        if self.master.hp > 0:
            self.master.hp += 30
