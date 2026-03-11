from abc import ABC, abstractmethod


class Game(ABC):
    """
    抽象遊戲基底類別（樣板方法模式）。

    定義遊戲流程的骨架（start），將各具體步驟委派給子類別實作。
    所有牌類遊戲皆繼承此類並覆寫抽象方法。
    """

    def __init__(self, players: list):
        if len(players) != 4:
            raise ValueError("Game requires exactly 4 players.")
        self._players = players
        self._deck = self._create_deck()

    # ── 樣板方法（Template Method）────────────────────
    def start(self) -> None:
        print(f"\n=== Welcome to {self._game_name()} ===\n")
        for player in self._players:
            player.name_himself()
        self._deck.shuffle()
        self._deal_cards()
        while not self._is_game_over():
            self._take_a_turn()
            self._show_cards()
            self._diff_cards()
        self._print_victor()

    # ── 掛鉤（Hook）──────────────────────────────────
    def _game_name(self) -> str:
        return "Card Game"

    # ── 抽象步驟（Abstract steps）────────────────────
    @abstractmethod
    def _create_deck(self):
        """建立並回傳遊戲專用牌堆。"""
        pass

    @abstractmethod
    def _deal_cards(self) -> None:
        """發牌給所有玩家。"""
        pass

    @abstractmethod
    def _is_game_over(self) -> bool:
        """回傳遊戲是否結束。"""
        pass

    @abstractmethod
    def _take_a_turn(self) -> None:
        """執行一個回合的出牌邏輯。"""
        pass

    @abstractmethod
    def _show_cards(self) -> None:
        """展示本回合桌面狀態。"""
        pass

    @abstractmethod
    def _diff_cards(self) -> None:
        """評分：判斷本回合得分者。"""
        pass

    @abstractmethod
    def _print_victor(self) -> None:
        """宣告最終勝利者。"""
        pass
