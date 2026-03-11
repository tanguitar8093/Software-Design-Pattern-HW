import sys
import os
# 讓 models/Game.py 可以 import common.Game（位於 v3/ 根目錄）
sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..')))

from common.Game import Game as BaseGame
from typing import List
from models.Player.Player import Player
from models.Desk import Deck
from models.Card import Card


class Game(BaseGame):
    """
    Showdown 具體遊戲類別。

    覆寫了 BaseGame 中所有抽象方法：
      - _create_deck()    建立 52 張標準牌堆
      - _deal_cards()     每人發 13 張
      - _is_game_over()   打完 13 回合後結束
      - _take_a_turn()    四人同時出一張牌
      - _show_cards()     展示桌面各人出的牌
      - _diff_cards()     找出最大牌的玩家，+1 分
      - _print_victor()   列印最終積分與勝利者

    掛鉤（Hook）：
      - _game_name()      回傳 "Showdown"
    """

    def __init__(self, players: List[Player]):
        self._turn_cards: dict = {}
        self._turns_played: int = 0
        super().__init__(players)

    # ── 工廠方法 ──────────────────────────────────────
    def _create_deck(self):
        return Deck()

    # ── 掛鉤 ─────────────────────────────────────────
    def _game_name(self) -> str:
        return "Showdown"

    # ── 抽象方法實作 ──────────────────────────────────
    def _deal_cards(self) -> None:
        for _ in range(13):
            for player in self._players:
                player.add_hand(self._deck.draw_card())

    def _is_game_over(self) -> bool:
        return self._turns_played >= 13

    def _take_a_turn(self) -> None:
        self._turn_cards.clear()
        for player in self._players:
            print(f"{player.name}'s turn to think...")
            self._turn_cards[player] = player.show()
        self._turns_played += 1

    def _show_cards(self) -> None:
        print("\nCards on the table:")
        for player, card in self._turn_cards.items():
            print(f"{player.name} shows {card.suit.name} {card.rank.name}")

    def _diff_cards(self) -> None:
        winner = None
        max_card = None
        for player, card in self._turn_cards.items():
            if max_card is None or card > max_card:
                max_card = card
                winner = player
        if winner:
            print(f"\n>>> Winner of this turn is {winner.name}! (+1 Point)")
            winner.add_point()

    def _print_victor(self) -> None:
        print("\n=== Game Over ===")
        print("Final Scores:")
        for player in self._players:
            print(f"{player.name}: {player.point} points")
        max_point = max(p.point for p in self._players)
        victors = [p for p in self._players if p.point == max_point]
        print("\n🏆 Final Victor(s) 🏆:")
        for p in victors:
            print(f"  {p.name} with {p.point} points!")
