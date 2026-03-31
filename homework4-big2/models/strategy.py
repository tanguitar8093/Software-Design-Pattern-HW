from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Optional, Protocol, TYPE_CHECKING
from .enums import Suit, Rank

# 使用 TYPE_CHECKING 讓型別檢查器認識這些類別，但執行時不會發生 import
if TYPE_CHECKING:
    from models.player import Player
    from models.pattern import CardPattern

# --- 1. 定義遊戲上下文介面 (解除雙向依賴的關鍵) ---
class GameContext(Protocol):
    @property
    def players(self) -> List[Player]: 
        """獲取目前遊戲中的玩家清單副本"""
        ...

    @property
    def rounds(self) -> int: 
        """獲取目前是第幾局"""
        ...

    @property
    def top_play(self) -> Optional[CardPattern]: 
        """獲取目前檯面上最大的牌組"""
        ...

    def set_players_order(self, new_order: List[Player]) -> None:
        """允許策略調整遊戲中的玩家出牌順序"""
        ...

# --- 2. 策略基類 (Template Method 結構) ---
class RoundStrategy(ABC):
    @abstractmethod
    def play_round(self, game: GameContext) -> None:
        """每一輪執行的進入點"""
        pass

class RoundBaseStrategy(RoundStrategy):
    def play_round(self, game: GameContext) -> None:
        # 將 game 實體存為成員變數，供子類別方法存取
        self.game = game
        
        # 執行 Template Method 骨架
        self.do_before_common_rule()
        self.do_common_rule()
        self.do_after_common_rule()

    def do_common_rule(self) -> None:
        """所有回合通用的邏輯：例如循環詢問玩家出牌"""
        # 實作範例：可以透過 self.game.players 取得玩家進行輪替
        print(f"--- 第 {self.game.rounds} 回合開始執行通用規則 ---")

    def do_before_common_rule(self) -> None:
        """回合前置準備（由子類別實作）"""
        pass

    def do_after_common_rule(self) -> None:
        """回合後置處理（由子類別實作）"""
        pass

# --- 3. 具體策略實作 ---

class FirstRoundStrategy(RoundBaseStrategy):
    """
    第一回合特有策略：
    1. 尋找持有梅花 3 的玩家。
    2. 將該玩家排在第一位出牌。
    """
    def do_before_common_rule(self) -> None:
        players = self.game.players
        
        for i, p in enumerate(players):
            # 檢查手牌是否有梅花 3
            has_club_3 = any(
                c.suit == Suit.CLUBS and c.rank == Rank.THREE 
                for c in p.hand_cards
            )
            
            if has_club_3:
                # 重新排列玩家順序，讓梅花 3 玩家當 index 0
                new_order = players[i:] + players[:i]
                self.game.set_players_order(new_order)
                print(f"由玩家 {p.name} 領先開始。")
                break

class ContinueRoundStrategy(RoundBaseStrategy):
    """
    後續回合策略：
    例如處理上一局贏家先出，或是清空檯面重新開始。
    """
    def do_after_common_rule(self) -> None:
        # 這裡可以實作續局特有邏輯
        # 例如：檢查是否有人手牌歸零，設定遊戲結束標記等
        pass