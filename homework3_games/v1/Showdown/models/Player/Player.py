from abc import ABC, abstractmethod
from models.Hand import Hand
from models.Card import Card
from models.Decision.Decision import Decision

class Player(ABC):
    
    def __init__(self, decision: Decision):
        self._point: int = 0
        self._hand: Hand = Hand()
        self._name: str = ""
        self._decision: Decision = decision

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def point(self) -> int:
        return self._point

    @abstractmethod
    def name_himself(self) -> None:
        pass

    def show(self) -> Card:
        """Takes a turn: Show a card. Returns the card chosen by decision."""
        # Use the stored decision object to pick a card
        return self._decision.make_decision(self._hand)

    def add_point(self, point: int = 1) -> None:
        self._point += point
    
    def add_hand(self, card: Card) -> None:
        """Adds a card to the player's Hand object."""
        self._hand.add_card(card)
        