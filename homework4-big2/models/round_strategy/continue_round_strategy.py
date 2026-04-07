from __future__ import annotations
from typing import TYPE_CHECKING
from models.round_strategy.round_strategy import RoundBaseStrategy
from models.round_strategy.game_context import GameContext

class ContinueRoundStrategy(RoundBaseStrategy):  
    # (異) 找出 current_player (非第一回合，從上一輪贏家起手)
    def prepare_starting_player(self, game: GameContext) -> None:
        top_player = game.top_player
        if top_player is None:
            raise ValueError("ContinueRoundStrategy 需要 top_player 來決定出牌順序")
        players = game.players
        game.set_players_order(players[players.index(top_player):] + players[:players.index(top_player)])  