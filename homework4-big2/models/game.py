from typing import List, Optional
from .strategy import RoundStrategy, FirstRoundStrategy, ContinueRoundStrategy
from .validator import Validator
from .deck import Deck
from .player import Player
from .pattern import CardPattern
class Big2Game:

    _players = Validator(list, rule=lambda p: len(p) == 4)
    
    def __init__(self, players: List[Player]):
        # 觸發 Validator
        self._players = players
        self._rounds = 1
        self._is_game_over = False
        self._deck = Deck()
        self._top_play = None  # Add top_play attribute

    @property
    def rounds(self) -> int:
        return self._rounds

    @property
    def top_play(self) -> Optional[CardPattern]:
        return self._top_play

    @top_play.setter
    def top_play(self, value: Optional[CardPattern]) -> None:
        self._top_play = value

    @property
    def players(self) -> List[Player]:
        # 這裡回傳副本是正確的（保護性拷貝）
        return self._players[:] 

    def set_players_order(self, new_order: List[Player]) -> None:
        self._players = new_order

    def start(self) -> None:
        # 初始化名字
        for i, player in enumerate(self._players): # 直接用底層資料
            player.name_himself(i)
            
        self._deck.shuffle()

        # 發牌：必須直接操作 self._players_val 確保資料有寫進去
        total_cards = len(self._deck)
        for i in range(total_cards):
            card = self._deck.deal()
            # 修正：不要經由 property，直接經由底層 list
            self._players[i % 4].hand_cards.append(card)
        
        while not self._is_game_over:
            # 根據回合選擇策略
            strategy: RoundStrategy = FirstRoundStrategy() if self._rounds == 1 else ContinueRoundStrategy()
            
            # 執行策略 (Dependency Injection)
            strategy.play_round(self)
            # 檢查結束邏輯 (假設簡化)
            if any(len(p.hand_cards) == 0 for p in self._players):
                self._is_game_over = True
            self._rounds += 1