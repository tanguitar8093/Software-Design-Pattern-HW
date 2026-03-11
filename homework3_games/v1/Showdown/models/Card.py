from models.enums import Rank, Suit

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

    def __gt__(self, other: 'Card') -> bool:
        if self._rank != other._rank:
            return self._rank > other._rank
        return self._suit > other._suit
