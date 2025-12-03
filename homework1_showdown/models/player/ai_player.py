import random
from models.player.player import Player
from utils.enums import PlyaerId
from models.card import Card

class AIPlayer(Player):
    def __init__(self, player_id: PlyaerId):
        super().__init__(player_id)
    def name_himself(self) -> None:
        self.name= f"AI-{self.id.name}"
    def exchange_hands(self, players: list[Player]) -> None:
        if not self.exchange_used and self.hands and random.random() < 0.5:
            available = [p for p in players if p is not self]
            chosen_partner = random.choice(available)
            self._do_exchange_hands(chosen_partner) 
    def show(self) -> Card:
        return self._do_show(random.randint(0, len(self.hands) - 1))