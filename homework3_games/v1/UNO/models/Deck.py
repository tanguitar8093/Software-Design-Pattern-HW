from typing import List
import random
from models.Card import Card
from models.enums import Color, Number

class Deck:
    def __init__(self):
        self._cards: List[Card] = []
        self._init_deck()

    def _init_deck(self):
        """牌堆中一開始存有 40 張牌：4 種顏色 x 10 個數字"""
        for color in Color:
            for number in Number:
                self._cards.append(Card(color, number))

    def shuffle(self) -> None:
        random.shuffle(self._cards)

    def draw_card(self) -> Card:
        if not self._cards:
            raise Exception("Deck is empty")
        return self._cards.pop()

    def is_empty(self) -> bool:
        return len(self._cards) == 0

    def add_discarded_cards(self, cards: List[Card]) -> None:
        self._cards.extend(cards)
        self.shuffle()
