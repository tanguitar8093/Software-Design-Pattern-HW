from typing import List
from models.Card import Card

class Hand:
    def __init__(self):
        self._cards: List[Card] = []

    @property
    def cards(self) -> List[Card]:
        return self._cards

    def add_card(self, card: Card) -> None:
        if len(self._cards) >= 13:
            raise Exception("Hand is already full (max 13 cards).")
        self._cards.append(card)

    def remove_card(self, card: Card) -> None:
        if card in self._cards:
            self._cards.remove(card)
        else:
            raise ValueError("Card not in hand.")
