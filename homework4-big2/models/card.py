from enum import Enum
from .enums import Suit, Rank

class Card:
    def __init__(self, rank: Rank, suit: Suit):
        self.rank = rank
        self.suit = suit

    def __str__(self) -> str:
        return f"{self.rank.value}{self.suit.value}"
