from .round_strategy.round_strategy import RoundStrategy
from .round_strategy.first_round_strategy import FirstRoundStrategy
from .round_strategy.continue_round_strategy import ContinueRoundStrategy
from .deck import Deck
from .player.player import Player

class Big2Game:
    def __init__(self, players: list[Player]):
        self._players: list[Player] = players
        self._rounds: int = 1
        self._is_game_over: bool = False
        self._deck: Deck = Deck()
        self._top_player: Player | None = None

    def print_winner(self) -> None:
        winner = self._top_player
        if winner is None:
            raise ValueError("無法印出勝利者，因為 top_player 為 None")
        print(f"恭喜玩家 {winner.name} 獲勝！")

    def start(self) -> None:
        # 玩家命名
        for i, player in enumerate(self._players):
            player.name_himself(i)
        # 洗牌
        self._deck.shuffle()
        for player in self._players:
            print(player.name)
        # 發牌
        total_cards = len(self._deck)
        for i in range(total_cards):
            card = self._deck.deal()
            self._players[i % 4].add_card(card)
            
        # 進行遊戲
        while not self._is_game_over:
            strategy: RoundStrategy = FirstRoundStrategy() if self._rounds == 1 else ContinueRoundStrategy()
            
            # Data In: 玩家清單, 回合數, 上一把贏家
            result = strategy.play_round(self._players, self._rounds, self._top_player)
            
            # Data Out: 將策略回傳的結果更新至 Game 的狀態
            self._top_player = result.top_player
            if result.is_game_over:
                self._is_game_over = True
                break
                
            self._rounds += 1
            
        # 印出勝利者
        self.print_winner()
