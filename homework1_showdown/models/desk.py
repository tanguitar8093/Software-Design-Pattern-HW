from models.card import Card
from utils.enums import Suit, Rank
import random

class Desk:
    def __init__(self):
        self._cards: list[Card] = []
        self._create_deck()

    @property
    def cards(self) -> tuple[Card, ...]:
        return tuple(self._cards)

    def _create_deck(self):
        for suit in Suit:
            for rank in Rank:
                self._cards.append(Card(suit, rank))
        if len(self._cards) != 52:
            raise ValueError("牌組數量錯誤，應為 52 張")
    def shuffle(self):
        random.shuffle(self._cards)

    def draw_card(self):
        if not self._cards:
            raise ValueError("沒有牌可以抽了")
        return self._cards.pop()