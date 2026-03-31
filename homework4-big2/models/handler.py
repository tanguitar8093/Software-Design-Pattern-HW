from abc import ABC, abstractmethod
from typing import List, Optional
from models.card import Card
from models.pattern import CardPattern

class PatternHandler(ABC):
    def __init__(self, next_handler: Optional['PatternHandler'] = None):
        self.next = next_handler

    def handle(self, cards: List[Card]) -> Optional[CardPattern]:
        result = self.do_handling(cards)
        if result:
            return result
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
    def do_handling(self, cards: List[Card]) -> Optional[CardPattern]:
        pass

    def match(self, cards: List[Card]) -> bool:
        pass

class PairHandler(PatternHandler):
    def do_handling(self, cards: List[Card]) -> Optional[CardPattern]:
        pass

    def match(self, cards: List[Card]) -> bool:
        pass

class StraightHandler(PatternHandler):
    def do_handling(self, cards: List[Card]) -> Optional[CardPattern]:
        pass

    def match(self, cards: List[Card]) -> bool:
        pass

class FullHouseHandler(PatternHandler):
    def do_handling(self, cards: List[Card]) -> Optional[CardPattern]:
        pass

    def match(self, cards: List[Card]) -> bool:
        pass
