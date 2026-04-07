from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from models.card import Card
from models.handler import SingleHandler, PairHandler, StraightHandler, FullHouseHandler
from models.round_strategy.game_context import GameContext

if TYPE_CHECKING:
    from models.pattern import CardPattern
    from models.player import Player

class RoundStrategy(ABC):
    @abstractmethod
    def play_round(self, game: GameContext) -> None:
        pass

class RoundBaseStrategy(RoundStrategy):
    def __init__(self) -> None:
        super().__init__()
        self._pass_count = 0

    @property
    def pass_count(self) -> int:
        return self._pass_count
    
    @pass_count.setter
    def pass_count(self, value: int) -> None:
        if value < 0:
            raise ValueError("pass_count 不可小於0")
        self._pass_count = value

    # ===== 樣板方法核心 =====
    def play_round(self, game: GameContext) -> None:
        # 1. 找出 current_player，設定這回合的出牌順序 => (異)
        self.prepare_starting_player(game)

        # 回合初始設定 (同)
        game.top_play = None
        self._pass_count = 0
        current_idx = 0 
        
        print(f"第 {game.rounds} 回合開始！")
        
        # 累積連續三個 pass 此回合結束 => (同)
        while self._pass_count < 3:
            current_player = game.players[current_idx]
            print(f"輪到玩家：{current_player.name}")
            top_play_str = " ".join(str(c) for c in game.top_play.cards) if game.top_play else "無"
            print(f"目前牌面：{top_play_str}")
            
            # 2. current_player 出牌
            cards = current_player.play(game.top_play)
            
            # 3. 驗證 (統整「先發禁Pass」、「頂牌大小」、「首回合梅花三」規則) => (同+異)
            # 如果驗證沒過，直接 continue 讓同一個玩家重新出牌
            is_valid, card_pattern = self.validate_action(current_player, cards, game.top_play)
            if not is_valid:
                continue

            # 4. 更新遊戲資訊
            if cards is None:
                # 這是合法的 Pass
                print(f"玩家 {current_player.name} 選擇 Pass")
                self._pass_count += 1
            else:
                # 這是合法的出牌
                print(f"玩家 {current_player.name} 出牌成功：{card_pattern.get_pattern_name()} {' '.join(str(c) for c in cards)}")
                game.top_play = card_pattern # 出牌成功設為頂牌
                game.top_player = current_player
                # 扣除手牌
                for card in cards:
                    current_player.remove_card(card)
                self._pass_count = 0  # 有人出牌，重新計數 pass
                
                # 5. 判斷遊戲是否結束
                if game.validate_end_game(current_player):
                    break
            
            # 換下一位玩家
            current_idx = (current_idx + 1) % len(game.players)


    # ---------- 以下為驗證與共用細節 ----------

    # (異+同) 集中驗證所有邏輯，避免迴圈被細節淹沒
    def validate_action(self, current_player: Player, cards: list[Card] | None, top_play: CardPattern | None) -> tuple[bool, CardPattern | None]:
        # 驗證 Pass
        if cards is None:
            # (同) 先發玩家 (top_play 為空時) 不得 Pass
            if top_play is None:
                print(f"玩家 {current_player.name} 無法 Pass，請重新出牌！")
                return False, None
            return True, None

        # 將出的牌轉為牌型
        handler_chain = SingleHandler(PairHandler(StraightHandler(FullHouseHandler())))
        card_pattern = handler_chain.handle(cards)
        if card_pattern is None:
            print(f"玩家 {current_player.name} 出牌失敗，請重新出牌！")
            return False, None

        # 驗證 (同)：必須符合頂牌比較規則
        if top_play is not None:
            if type(top_play) is not type(card_pattern) or not (top_play < card_pattern):
                print(f"玩家 {current_player.name} 出牌失敗，請重新出牌！")
                return False, None
        
        # 驗證 (異)：特殊規則 (譬如第一回合首發梅花三)
        if not self.validate_special_rule(card_pattern, top_play):
            print(f"玩家 {current_player.name} 出牌失敗，請重新出牌！")
            return False, None

        return True, card_pattern

    @abstractmethod
    def prepare_starting_player(self, game: GameContext) -> None:
        """(異) 準備這回合第一位發牌的玩家，並設定好順序"""
        pass

    def validate_special_rule(self, card_pattern: CardPattern, top_play: CardPattern | None) -> bool:
        """(異) 預設無特殊規則，可供子類別覆寫"""
        return True
