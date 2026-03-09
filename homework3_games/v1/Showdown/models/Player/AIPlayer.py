#抽象要 import 那些東西
from abc import ABC, abstractmethod

class AIPlayer(ABC):
    
    def __init__(self):
        self._points: int = 0
        self._hand: Hand = Hand()
        self._name: str = ""


    @abstractmethod
    def name_himself(self):
        pass

    def show(self,decision: Decision):
        decision.make_decision(hand: self._hand)

    def add_point(self,point: int):
        self._points += point
    
    def add_hand(self,card: Card):
        pass
        