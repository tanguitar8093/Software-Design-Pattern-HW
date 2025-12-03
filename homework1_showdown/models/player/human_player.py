from models.player.player import Player
from utils.enums import PlyaerId
from models.card import Card

class HumanPlayer(Player):
    def __init__(self, player_id: PlyaerId):
        super().__init__(player_id)
    def name_himself(self) -> None:
        name = input("請輸入您的名字：").strip()
        self.name = f"Human-{name}({self.id.name})"
    def exchange_hands(self, players: list[Player]) -> None:
        if self.exchange_used:
            print("已使用過交換手牌特權")
            return
        
        print("可交換手牌的玩家：")
        print("0. 跳過")
        available = [p for p in players if p is not self]
        for idx, p in enumerate(available, 1):
            print(f"{idx}. {p.name} ({p.id.name})")
        choice = int(input("請選擇要交換的玩家編號："))
        if choice == 0:
            return
        elif 1 <= choice <= len(available):
            chosen_partner = available[choice - 1]
            self._do_exchange_hands(chosen_partner)
        else:
            print("無效的選擇")
            return self.exchange_hands(players)
    def show(self) -> Card:
        if not self.hands:
            raise ValueError("沒有手牌可出")

        print("你的手牌：")
        for idx, card in enumerate(self.hands, 1):
            print(f"{idx}. {card}")
        choice = int(input("請選擇要出的牌編號：")) - 1
        if 0 <= choice < len(self.hands):
            return self._do_show(choice)
        else:
            print("無效的選擇")
            return self.show()  
