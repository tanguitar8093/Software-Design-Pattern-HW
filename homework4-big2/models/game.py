from typing import List, Optional
from models.player import Player
from models.deck import Deck
from models.pattern import CardPattern
from models.validator import Validator

class Big2Game:
    # 1. 將 Validator 綁定在「私有變數名」上
    # 這樣內部 self._players = ... 時會觸發驗證，但外部看不到這些變數
    _players = Validator(list, rule=lambda p: len(p) == 4) 
    _top_play = Validator(CardPattern, allow_none=True)
    _top_player = Validator(Player, allow_none=True)
    _first_player_index = Validator(int, rule=lambda i: 0 <= i <= 3)

    def __init__(self, players: List[Player]):
        # 2. 內部初始化：賦值給私有變數，觸發上面的 Validator 驗證
        self._players = players
        self._top_play = None
        self._top_player = None
        self._first_player_index = 0
        
        # 純內部狀態
        self._rounds: int = 1
        self._is_game_over: bool = False
        self._deck: Deck = Deck()

    # 3. 對外開放「唯讀」屬性 (Read-only Properties)
    # 外部只能讀取，不能執行 game.players = ...
    @property
    def players(self) -> List[Player]:
        return self._players[:] # 回傳副本防止外部直接修改 list 內容

    @property
    def top_play(self) -> Optional[CardPattern]:
        return self._top_play

    @property
    def top_player(self) -> Optional[Player]:
        return self._top_player

    @property
    def first_player_index(self) -> int:
        return self._first_player_index

    # 4. 遊戲邏輯方法
    def start(self) -> None:
        # Step 2: 命名 name_himself()
        for i, player in enumerate(self.players):
            player.name_himself(i)
            
        # Step 3: 洗牌 shuffle()
        self._deck.shuffle()

        # Step 4: 發牌 deal() - 將 52 張牌輪流發給 4 位玩家直到 Deck Empty 為止
        # _deck.cards 回傳的是複製清單，我們直接用長度來當迴圈控制，發向 player
        total_cards = len(self._deck)  # 此時剛初始化應為 52 張
        for i in range(total_cards):
            card = self._deck.deal()
            # 用求餘數的方式將牌依序分給四位玩家 (0, 1, 2, 3, 0, 1...)
            self.players[i % 4].hand_cards.append(card)
    def _play_round(self) -> None:
        """內部邏輯：處理每一輪的出牌"""
        pass

    def _finalize_game(self) -> None:
        """內部邏輯：遊戲結束結算"""
        pass