import sys
import os
# 將 v4/ 加入 sys.path，使 common 套件可被 import
sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..')))

from common.Game import Game as BaseGame
from typing import List
from models.Player.Player import Player
from models.Deck import Deck
from models.Card import Card


class Game(BaseGame):
    """
    UNO 具體遊戲類別。

    覆寫 BaseGame 所有抽象方法：
      - _create_deck()  : 建立 40 張 UNO 牌堆（4色 × 10數字）
      - _deal_cards()   : 每人發 5 張，翻一張作為頂牌
      - _is_game_over() : 有玩家手牌清空後結束
      - _take_a_turn()  : 每位玩家依序出牌或抽牌
      - _show_cards()   : 顯示目前頂牌
      - _diff_cards()   : 有勝者時記 1 分
      - _print_victor() : 宣告勝利者

    掛鉤（Hook）：
      - _game_name()    : 回傳 "UNO"
    """

    def __init__(self, players: List[Player]):
        self._discard_pile: List[Card] = []
        self._top_card: Card = None
        self._winner: Player = None
        super().__init__(players)

    # ── 工廠方法 ──────────────────────────────────────
    def _create_deck(self):
        return Deck()

    # ── 掛鉤 ─────────────────────────────────────────
    def _game_name(self) -> str:
        return "UNO"

    # ── 抽象方法實作 ──────────────────────────────────
    def _deal_cards(self) -> None:
        for _ in range(5):
            for player in self._players:
                player.add_hand(self._deck.draw_card())
        self._top_card = self._deck.draw_card()
        self._discard_pile.append(self._top_card)

    def _is_game_over(self) -> bool:
        return self._winner is not None

    def _take_a_turn(self) -> None:
        for player in self._players:
            if self._winner is not None:
                break
            print(f"\n{player.name}'s turn. Top card: "
                  f"{self._top_card.color.name} {self._top_card.number.name}")
            if not player.has_valid_card(self._top_card):
                print(f"{player.name} has no valid cards and must draw.")
                player.add_hand(self._draw_card_safe())
            else:
                played_card = player.show(self._top_card)   # context = top_card
                if played_card:
                    print(f"{player.name} plays "
                          f"{played_card.color.name} {played_card.number.name}")
                    self._top_card = played_card
                    self._discard_pile.append(played_card)
            if player.has_empty_hand():
                self._winner = player

    def _show_cards(self) -> None:
        if self._winner is None:
            print(f"\n--> Top card is now "
                  f"{self._top_card.color.name} {self._top_card.number.name}")

    def _diff_cards(self) -> None:
        if self._winner is not None:
            self._winner.add_point()

    def _print_victor(self) -> None:
        print(f"\n=== Game Over ===")
        print(f"[Trophy] Final Victor: {self._winner.name}!")

    # ── 私有輔助方法 ──────────────────────────────────
    def _draw_card_safe(self) -> Card:
        if self._deck.is_empty():
            print("Deck is empty, reshuffling discard pile...")
            cards_to_recycle = self._discard_pile[:-1]
            self._discard_pile = [self._top_card]
            self._deck.add_discarded_cards(cards_to_recycle)
        return self._deck.draw_card()
