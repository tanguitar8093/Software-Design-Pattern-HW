from abc import ABC, abstractmethod
from models.Hand import Hand
from models.Card import Card

class Decision(ABC):
    
    @abstractmethod
    def make_decision(self, hand: Hand) -> Card:
        pass
        
