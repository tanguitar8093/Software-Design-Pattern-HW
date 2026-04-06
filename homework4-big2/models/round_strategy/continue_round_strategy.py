from __future__ import annotations
from typing import TYPE_CHECKING
from models.player import Player
from models.card import Card
from models.round_strategy.round_strategy import RoundBaseStrategy
from models.round_strategy.game_context import GameContext
if TYPE_CHECKING:
    from models.pattern import CardPattern

class ContinueRoundStrategy(RoundBaseStrategy):  
    def validate_pass(self, hand_cards: list[Card], top_play: CardPattern | None) -> bool:
        return top_play is not None
    def do_before_common_rule(self,game: GameContext) -> None:
        game.top_play = None
        top_player = game.top_player
        if top_player is None:
            raise ValueError("ContinueRoundStrategy 需要 top_player 來決定出牌順序")
        players: list[Player] = game.players
        game.set_players_order(players[players.index(top_player):] + players[:players.index(top_player)])  