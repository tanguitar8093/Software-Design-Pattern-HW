from __future__ import annotations
from typing import TYPE_CHECKING
from models.enums import Suit, Rank
from models.card import Card
from models.round_strategy.round_strategy import RoundBaseStrategy
from models.round_strategy.game_context import GameContext
if TYPE_CHECKING:
    from models.player import Player
    from models.pattern import CardPattern

class FirstRoundStrategy(RoundBaseStrategy):
    def _validate_having_clubs_3(self, cards: list[Card] | None) -> bool:
        if not cards:
            return False
        return any(c.suit == Suit.CLUBS and c.rank == Rank.THREE for c in cards)

    def do_before_common_rule(self,game: GameContext) -> None:
        players: list[Player] = game.players

        for player in (players):
            if self._validate_having_clubs_3(player.hand_cards):
                game.set_players_order(players[players.index(player):] + players[:players.index(player)])
                print(f"玩家 {player.name} 擁有梅花 3，將先開始出牌！")
                break

    def validate_play(self, card_pattern: CardPattern | None, top_play: CardPattern | None) -> bool:
        if not super().validate_play(card_pattern, top_play):
            return False
        if top_play is None and card_pattern is not None:
            cards = card_pattern.cards 
            return self._validate_having_clubs_3(cards)
        return True

    def validate_pass(self, hand_cards: list[Card], top_play: CardPattern | None) -> bool:
        return not self._validate_having_clubs_3(hand_cards)
