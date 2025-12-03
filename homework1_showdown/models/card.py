from utils.enums import Suit, Rank

class Card:
    def __init__(self, suit, rank):
        try:
            self._suit: Suit = suit
            self._rank: Rank = rank
        except ValueError as exc:
            raise ValueError("suit 或 rank 不在範圍內") from exc

    @property
    def suit(self) -> Suit:
        return self._suit

    @suit.setter
    def suit(self, value: Suit) -> None:
        self._suit = Suit(value)

    @property
    def rank(self) -> Rank:
        return self._rank

    @rank.setter
    def rank(self, value: Rank) -> None:
        self._rank = Rank(value)

    def __gt__(self, other):
        return (self.suit, self.rank) > (other.suit, other.rank)

    def __str__(self):
        return f"{self.suit.name}-{self.rank.name} ({self.suit.value}-{self.rank.value})"