from abc import ABC, abstractmethod
from models.card import Card
from models.pattern import CardPattern

class Player(ABC):
    def __init__(self, id: int):
        self._name: str = ""
        self._hand_cards: list[Card] = []
        self._id = id

    def add_card(self, card: Card) -> None:
        if not isinstance(card, Card):
            raise TypeError("只能添加 Card 類型的物件")
        self._hand_cards.append(card)
    
    def remove_card(self, card: Card) -> None:
        if not isinstance(card, Card):
            raise TypeError("只能移除 Card 類型的物件")

        self._hand_cards.remove(card)

    @property
    def id(self) -> int:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def hand_cards(self) -> list[Card]:
        return self._hand_cards[:]

    @abstractmethod
    def name_himself(self, player_index: int) -> None:
        pass

    @abstractmethod
    def play(self, top_play: CardPattern | None) -> list[Card] | None:
        pass



