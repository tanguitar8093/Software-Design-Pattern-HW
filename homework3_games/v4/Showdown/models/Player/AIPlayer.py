from models.Player.Player import Player
from models.Decision.RandomDecision import RandomDecision


class AIPlayer(Player):
    def __init__(self, name: str):
        super().__init__(decision=RandomDecision())
        self._name = str(name)

    def name_himself(self) -> None:
        self._name = f"AIPlayer-{self._name}"
