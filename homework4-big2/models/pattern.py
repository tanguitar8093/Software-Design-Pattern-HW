from abc import ABC, abstractmethod
from typing import List, Any
from models.card import Card

class CardPattern(ABC):
    def __init__(self, cards: List[Card]):
        self.cards = cards

    @abstractmethod
    def get_pattern_name(self) -> str:
        pass

    @abstractmethod
    def validate(self) -> bool:
        pass

    @abstractmethod
    def __lt__(self, other: Any) -> bool:
        pass

class Single(CardPattern):
    def get_pattern_name(self) -> str:
        return "Single"

    def validate(self) -> bool:
        pass

    def __lt__(self, other: Any) -> bool:
        pass

class Pair(CardPattern):
    def get_pattern_name(self) -> str:
        return "Pair"

    def validate(self) -> bool:
        pass

    def __lt__(self, other: Any) -> bool:
        pass

class Straight(CardPattern):
    def get_pattern_name(self) -> str:
        return "Straight"

    def validate(self) -> bool:
        pass

    def __lt__(self, other: Any) -> bool:
        pass

class FullHouse(CardPattern):
    def get_pattern_name(self) -> str:
        return "Full House"

    def validate(self) -> bool:
        pass

    def __lt__(self, other: Any) -> bool:
        pass
