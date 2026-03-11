from models.Player.Player import Player
from models.Decision.CommandLineDecision import CommandLineDecision


class HumanPlayer(Player):
    def __init__(self):
        super().__init__(decision=CommandLineDecision())

    def name_himself(self) -> None:
        self._name = input("Please enter your name: ").strip() or "Unknown Human"
