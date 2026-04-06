from .round_strategy.round_strategy import RoundStrategy
from .round_strategy.first_round_strategy import FirstRoundStrategy
from .round_strategy.continue_round_strategy import ContinueRoundStrategy
from .deck import Deck
from .player.player import Player
from .pattern import CardPattern
class Big2Game:
    
    def __init__(self, players: list[Player]):
        self._players: list[Player] = players
        self._rounds: int = 1
        self._is_game_over: bool = False
        self._deck: Deck = Deck()
        self._top_play: CardPattern | None = None  
        self._top_player: Player | None = None

    @property
    def players(self) -> list[Player]:
        return self._players[:] 
    
    @property
    def rounds(self) -> int:
        return self._rounds

    @property
    def is_game_over(self) -> bool:
        return self._is_game_over

    @property
    def deck(self) -> Deck:
        return self._deck

    @property
    def top_play(self) -> CardPattern | None:
        return self._top_play
    
    @top_play.setter
    def top_play(self, value: CardPattern | None) -> None:
        if value is not None and not isinstance(value, CardPattern):
            raise ValueError("top_play 必須是 CardPattern 類型或 None")
        self._top_play = value

    @property
    def top_player(self) -> Player | None:
        return self._top_player

    @top_player.setter
    def top_player(self, player: Player | None) -> None:
        if player is not None and player not in self._players:
            raise ValueError("top_player 必須是玩家列表中的一員或 None")
        self._top_player = player
    
    def set_players_order(self, players: list[Player]) -> None:
        if set(players) != set(self._players):
            raise ValueError("傳入的玩家列表與現有玩家不相同")
        self._players = players[:]
    
    def validate_end_game(self,player: Player) -> bool:
        if not player.hand_cards:
            print(f"遊戲結束！")
            self._is_game_over = True
            return True
        return False

    def print_winner(self) -> None:
        winner = self.top_player
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
            strategy.play_round(self)
            self._rounds += 1
        # 印出勝利者
        self.print_winner()