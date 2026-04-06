from abc import ABC, abstractmethod
from typing import List, Optional
from models.card import Card
from models.pattern import CardPattern, Single, Pair, Straight, FullHouse

class PatternHandler(ABC):
    def __init__(self, next_handler: Optional['PatternHandler'] = None):
        self.next = next_handler

    def handle(self, cards: List[Card]) -> Optional[CardPattern]:
        if self.match(cards):
            return self.do_handling(cards)
        elif self.next:
            return self.next.handle(cards)
        return None

    @abstractmethod
    def do_handling(self, cards: List[Card]) -> Optional[CardPattern]:
        pass

    @abstractmethod
    def match(self, cards: List[Card]) -> bool:
        pass

class SingleHandler(PatternHandler):
    def do_handling(self, cards: List[Card]) -> CardPattern | None:
        return Single(cards)

    def match(self, cards: List[Card]) -> bool:
        return Single(cards).validate()

class PairHandler(PatternHandler):
    def do_handling(self, cards: List[Card]) -> CardPattern | None:
        if self.match(cards):
            return Pair(cards)
        return None

    def match(self, cards: List[Card]) -> bool:
        return Pair(cards).validate()

class StraightHandler(PatternHandler):
    def do_handling(self, cards: List[Card]) -> CardPattern | None:
        if self.match(cards):
            return Straight(cards)
        return None

    def match(self, cards: List[Card]) -> bool:
        return Straight(cards).validate()

class FullHouseHandler(PatternHandler):
    def do_handling(self, cards: List[Card]) -> CardPattern | None:
        if self.match(cards):
            return FullHouse(cards)
        return None

    def match(self, cards: List[Card]) -> bool:
        return FullHouse(cards).validate()
