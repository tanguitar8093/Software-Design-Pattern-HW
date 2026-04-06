from enum import Enum
from .enums import Suit, Rank

class Card:
    def __init__(self, rank: Rank, suit: Suit):
        self._rank = rank
        self._suit = suit

    @property
    def rank(self) -> Rank:
        return self._rank

    @property
    def suit(self) -> Suit:
        return self._suit

    def __str__(self) -> str:
        return f"{self.suit.value}[{self.rank.value}]"
