from abc import ABC, abstractmethod
from typing import List, Optional
from models.card import Card
from models.pattern import CardPattern

class Player(ABC):
    def __init__(self, name: str):
        self.name = name
        self.hand_cards: List[Card] = []

    @abstractmethod
    def name_himself(self, player_index: int) -> None:
        pass

    @abstractmethod
    def play(self, top_play: Optional[CardPattern]) -> Optional[List[Card]]:
        pass
    
    def pass_turn(self) -> None:
        pass

class HumanPlayer(Player):
    def name_himself(self, player_index: int) -> None:
        self.name = input("請輸入玩家名稱：")

    def play(self, top_play: Optional[CardPattern]) -> Optional[List[Card]]:
        pass

class AIPlayer(Player):
    def name_himself(self, player_index: int) -> None:
        # 根據外部索引動態給定名稱
        self.name = f"AIplayer_{player_index}"

    def play(self, top_play: Optional[CardPattern]) -> Optional[List[Card]]:
        pass
