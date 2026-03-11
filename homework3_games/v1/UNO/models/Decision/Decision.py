from abc import ABC, abstractmethod
from models.Hand import Hand
from models.Card import Card

class Decision(ABC):
    
    @abstractmethod
    def make_choice(self, hand: Hand, top_card: Card = None) -> Card:
        pass
