from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from models.card import Card
from models.handler import SingleHandler, PairHandler, StraightHandler, FullHouseHandler
from models.round_strategy.game_context import GameContext

if TYPE_CHECKING:
    from models.pattern import CardPattern

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

    def play_round(self, game: GameContext) -> None:
        self.do_before_common_rule(game)
        self.do_common_rule(game)

    def do_common_rule(self, game: GameContext) -> None:  
        next_idx =-1 
        print(f"第 {game.rounds} 回合開始！")
        while self._pass_count < 3:
            if next_idx == -1:
                current_player = game.players[0]
            else:
                current_player = game.players[next_idx]
            print(f"輪到玩家：{current_player.name}")
            top_play_str = " ".join(str(c) for c in game.top_play.cards) if game.top_play else "無"
            print(f"目前牌面：{top_play_str}")
            
            cards= current_player.play(game.top_play)
            if cards is None:
                if self.validate_pass(current_player.hand_cards, game.top_play):
                    print(f"玩家 {current_player.name} 選擇 Pass")
                    self._pass_count += 1
                    next_idx = (game.players.index(current_player) + 1) % len(game.players)
                else:
                    print(f"玩家 {current_player.name} 無法 Pass，請重新出牌！")
            else:
                # 開始驗證玩家出的牌是否合法
                handler_chain = SingleHandler(PairHandler(StraightHandler(FullHouseHandler())))
                card_pattern = handler_chain.handle(cards)
                if card_pattern and self.validate_play(card_pattern, game.top_play):
                    print(f"玩家 {current_player.name} 出牌成功：{card_pattern.get_pattern_name()} {' '.join(str(c) for c in cards)}")
                    game.top_play = card_pattern
                    game.top_player = current_player
                    for card in cards:
                        current_player.remove_card(card)
                    self._pass_count = 0
                    next_idx = (game.players.index(current_player) + 1) % len(game.players)
                    if game.validate_end_game(current_player):
                        break
                else:
                    print(f"玩家 {current_player.name} 出牌失敗，請重新出牌！")
    def validate_play(self, card_pattern: CardPattern | None, top_play: CardPattern | None) -> bool:
        if top_play is not None:
            if type(top_play) is not type(card_pattern):
                return False
            return top_play < card_pattern
        return True
    def validate_pass(self, hand_cards: list[Card], top_play: CardPattern | None) -> bool:
        return True
   
    @abstractmethod
    def do_before_common_rule(self,game: GameContext) -> None:
        ...
