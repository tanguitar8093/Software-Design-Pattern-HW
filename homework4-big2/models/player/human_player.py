from __future__ import annotations
from models.player.player import Player
from models.card import Card
from models.pattern import CardPattern

class HumanPlayer(Player):
    def name_himself(self, player_index: int) -> None:
        self._name = input("請輸入玩家名稱：")

    def play(self, top_play: CardPattern | None) -> list[Card] | None:
        from functools import cmp_to_key
        from models.pattern import _is_card_less_than
        
        # 確保手牌由小到大排序
        self._hand_cards.sort(key=cmp_to_key(lambda c1, c2: -1 if _is_card_less_than(c1, c2) else 1))
        
        card_strs = [str(c) for c in self._hand_cards]
        index_line = ""
        
        for i, c_str in enumerate(card_strs):
            # 每個索引置左對齊對應的牌距 (包含一個空白的寬度)
            width = len(c_str) + 1 if i < len(card_strs) - 1 else len(c_str)
            index_line += f"{i:<{width}}"
            
        print(index_line)
        print(" ".join(card_strs))
        
        user_input = input()
        if user_input.strip() == "-1":
            return None
            
        indices = [int(idx) for idx in user_input.split()]
        return [self._hand_cards[i] for i in indices]