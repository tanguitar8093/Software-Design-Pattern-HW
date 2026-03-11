from typing import List
from models.Player.Player import Player
from models.Desk import Deck
from models.Card import Card

class Game:
    def __init__(self, players: List[Player]):
        if len(players) != 4:
            raise ValueError("Game must have exactly 4 players.")
        self._players = players
        self._deck = Deck()
        self._turn_cards = {}  # Keep track of cards played in a turn: Player -> Card

    def start(self) -> None:
        print("=== Game Started ===")
        # 1. 玩家設定名字
        for player in self._players:
            player.name_himself()

        # 2. 洗牌
        print("\nShuffling deck...")
        self._deck.shuffle()
        
        # 3. 每人抽 13 張牌
        print("Drawing cards...")
        for _ in range(13):
            for player in self._players:
                card = self._deck.draw_card()
                player.add_hand(card)

        # 4. 遊戲進行 13 回合
        for turn in range(1, 14):
            print(f"\n--- Turn {turn} ---")
            self.take_a_turn()
            self.show_cards()
            self.diff_cards()

        # 5. 結算並印出最終勝利者
        self.print_victor()

    def take_a_turn(self) -> None:
        """P1~P4 輪流出 (Show) 一張牌 (彼此皆無法知曉彼此出的牌)"""
        self._turn_cards.clear()
        for player in self._players:
            print(f"{player.name}'s turn to think...")
            self._turn_cards[player] = player.show()

    def show_cards(self) -> None:
        """顯示 P1~P4 各出的牌的內容"""
        print("\nCards on the table:")
        for player, card in self._turn_cards.items():
            print(f"{player.name} shows {card.suit.name} {card.rank.name}")

    def diff_cards(self) -> None:
        """將 P1~P4 出的牌進行比大小決勝負，將優勝者的分數(Point)加一。"""
        winner = None
        max_card = None
        for player, card in self._turn_cards.items():
            if max_card is None or card > max_card:
                max_card = card
                winner = player
        
        if winner:
            print(f"\n>>> Winner of this turn is {winner.name}! (+1 Point)")
            winner.add_point()
        
    def print_victor(self) -> None:
        print("\n=== Game Over ===")
        print("Final Scores:")
        for player in self._players:
            print(f"{player.name}: {player.point} points")

        max_point = max(p.point for p in self._players)
        victors = [p for p in self._players if p.point == max_point]
        print("\n🏆 Final Victor(s) 🏆:")
        for p in victors:
            print(f"  {p.name} with {p.point} points!")