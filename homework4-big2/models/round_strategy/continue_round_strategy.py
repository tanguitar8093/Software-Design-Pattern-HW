from __future__ import annotations
from typing import TYPE_CHECKING
from models.round_strategy.round_strategy import RoundBaseStrategy

if TYPE_CHECKING:
    from models.player.player import Player

class ContinueRoundStrategy(RoundBaseStrategy):  
    # (異) 找出 current_player (非第一回合，從上一輪贏家起手)
    def prepare_starting_player(self, players: list[Player], last_winner: Player | None) -> list[Player]:
        if last_winner is None:
            raise ValueError("ContinueRoundStrategy 需要 last_winner 來決定出牌順序")
        idx = players.index(last_winner)
        return players[idx:] + players[:idx]
