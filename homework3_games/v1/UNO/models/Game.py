from typing import List
from models.Player.Player import Player
from models.Deck import Deck
from models.Card import Card

class Game:
    def __init__(self, players: List[Player]):
        if len(players) != 4:
            raise ValueError("Game must have exactly 4 players.")
        self._players = players
        self._deck = Deck()
        self._discard_pile: List[Card] = []
        self._top_card: Card = None
        self._winner: Player = None

    def start(self) -> None:
        print("=== UNO Game Started ===")
        # 1. 玩家命名
        for player in self._players:
            player.name_himself()

        # 2. 洗牌
        print("\nShuffling deck...")
        self._deck.shuffle()
        
        # 3. 每人抽 5 張牌
        print("Drawing cards...")
        for _ in range(5):
            for player in self._players:
                player.add_hand(self._deck.draw_card())

        # 4. 翻開第一張牌到檯面上
        self._top_card = self._deck.draw_card()
        self._discard_pile.append(self._top_card)

        # 為了搭配未來樣板方法，保留此對應方法的調用結構
        turn_count = 1
        while self._winner is None:
            print(f"\n--- Turn {turn_count} ---")
            self.take_a_turn()
            self.show_cards()
            self.diff_cards()
            turn_count += 1

        self.print_victor()

    def _draw_card_safe(self) -> Card:
        """防呆：如果抽牌時牌堆沒了，將檯面上舊的牌洗回牌堆"""
        if self._deck.is_empty():
            print("Deck is empty, reshuffling discard pile...")
            cards_to_recycle = self._discard_pile[:-1]
            self._discard_pile = [self._top_card]
            self._deck.add_discarded_cards(cards_to_recycle)
        return self._deck.draw_card()

    def take_a_turn(self) -> None:
        """P1~P4 輪流出牌回合"""
        for player in self._players:
            if self._winner is not None:
                break
                
            print(f"\n{player.name}'s turn. Top card on table: {self._top_card.color.name} {self._top_card.number.name}")
            
            if not player.has_valid_card(self._top_card):
                print(f"{player.name} has no valid cards and must draw a card.")
                drawn_card = self._draw_card_safe()
                player.add_hand(drawn_card)
                # 規則並未強制剛抽的牌若能出要馬上出，這邊以實作簡單的 "抽牌即結束本家回合"
            else:
                played_card = player.show(self._top_card)
                if played_card:
                    print(f"{player.name} plays {played_card.color.name} {played_card.number.name}")
                    self._top_card = played_card
                    self._discard_pile.append(played_card)
            
            # 手牌為空則獲勝
            if player.has_empty_hand():
                self._winner = player

    def show_cards(self) -> None:
        """因應未來 Template 機制，用於印出目前檯面上最新狀態"""
        if self._winner is None:
            print(f"\n--> Turn resolved. Top card is now {self._top_card.color.name} {self._top_card.number.name}")

    def diff_cards(self) -> None:
        """因應未來 Template 機制，這裡可以實作回合的簡單結算或給勝者加分等效果"""
        if self._winner:
            self._winner.add_point() # 給予贏家+1分, 符合Showdown那邊的架構

    def print_victor(self) -> None:
        if self._winner:
            print(f"\n=== Game Over ===")
            print(f"🏆 Final Victor is {self._winner.name}! 🏆")
