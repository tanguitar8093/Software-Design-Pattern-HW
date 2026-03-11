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

    def show(self, top_card: Card = None) -> Card:
        return self._decision.make_choice(self._hand, top_card)

    def add_point(self, point: int = 1) -> None:
        self._point += point

    def add_hand(self, card: Card) -> None:
        self._hand.add_card(card)

    def has_valid_card(self, top_card: Card) -> bool:
        return any(card.is_match(top_card) for card in self._hand.cards)

    def has_empty_hand(self) -> bool:
        return len(self._hand.cards) == 0
