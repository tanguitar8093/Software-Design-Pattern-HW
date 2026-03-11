from abc import ABC, abstractmethod


class Game(ABC):
    """
    樣板方法（Template Method）抽象基底類別。

    start() 定義了所有紙牌遊戲共同的骨架流程：
        1. 玩家自我介紹
        2. 洗牌
        3. 發牌          ← _deal_cards()     — 抽象：各遊戲決定發法
        4. 回合迴圈，直到遊戲結束：
              ├─ _take_a_turn()  — 抽象：一回合的出牌邏輯
              ├─ _show_cards()   — 抽象：展示桌面狀態
              └─ _diff_cards()   — 抽象：計算勝負、記分
        5. 宣告勝利者    ← _print_victor()    — 抽象：宣告方式

    子類別只需實作帶 @abstractmethod 的方法；
    _game_name() 是一個「掛鉤（Hook）」，有預設值但可選擇性覆寫。
    """

    def __init__(self, players: list):
        if len(players) != 4:
            raise ValueError("Game must have exactly 4 players.")
        self._players = players
        self._deck = self._create_deck()

    @abstractmethod
    def _create_deck(self):
        """工廠方法：子類別返回各自的牌堆實例。"""
        pass

    # ───────────────── 樣板方法 ─────────────────
    def start(self) -> None:
        print(f"=== {self._game_name()} Started ===")
        for player in self._players:
            player.name_himself()

        print("\nShuffling deck...")
        self._deck.shuffle()

        print("Drawing cards...")
        self._deal_cards()

        turn = 1
        while not self._is_game_over():
            print(f"\n--- Turn {turn} ---")
            self._take_a_turn()
            self._show_cards()
            self._diff_cards()
            turn += 1

        self._print_victor()

    # ───────────────── 掛鉤（Hook） ─────────────────
    def _game_name(self) -> str:
        """遊戲名稱，子類別可選擇性覆寫。"""
        return "Card Game"

    # ───────────────── 抽象方法 ─────────────────
    @abstractmethod
    def _deal_cards(self) -> None:
        """發牌：各遊戲決定發幾張、以何種方式發牌。"""
        pass

    @abstractmethod
    def _is_game_over(self) -> bool:
        """判斷遊戲是否結束。"""
        pass

    @abstractmethod
    def _take_a_turn(self) -> None:
        """執行一回合（所有玩家依序出牌）。"""
        pass

    @abstractmethod
    def _show_cards(self) -> None:
        """展示本回合桌面狀態。"""
        pass

    @abstractmethod
    def _diff_cards(self) -> None:
        """計算本回合勝負並記分。"""
        pass

    @abstractmethod
    def _print_victor(self) -> None:
        """宣告最終勝利者。"""
        pass
