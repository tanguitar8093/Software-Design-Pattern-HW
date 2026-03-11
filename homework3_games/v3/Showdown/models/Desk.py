from typing import List
import random
from models.Card import Card
from models.enums import Rank, Suit

class Deck:
    def __init__(self):
        self._cards: List[Card] = []
        for rank in Rank:
            for suit in Suit:
                self._cards.append(Card(rank, suit))

    def shuffle(self) -> None:
        random.shuffle(self._cards)

    def draw_card(self) -> Card:
        if not self._cards:
            raise Exception("No more cards in the deck.")
        return self._cards.pop()
