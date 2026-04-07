from __future__ import annotations
from typing import TYPE_CHECKING
from models.enums import Suit, Rank
from models.card import Card
from models.round_strategy.round_strategy import RoundBaseStrategy

if TYPE_CHECKING:
    from models.player.player import Player
    from models.pattern import CardPattern

class FirstRoundStrategy(RoundBaseStrategy):
    def _validate_having_clubs_3(self, cards: list[Card] | None) -> bool:
        if not cards:
            return False
        return any(c.suit == Suit.CLUBS and c.rank == Rank.THREE for c in cards)

    # (異) 找出 current_player (第一回合梅花三負責起手)
    def prepare_starting_player(self, players: list[Player], last_winner: Player | None) -> list[Player]:
        for player in players:
            if self._validate_having_clubs_3(player.hand_cards):
                print(f"玩家 {player.name} 擁有梅花 3，將先開始出牌！")
                return players[players.index(player):] + players[:players.index(player)]
        raise ValueError("沒有玩家擁有梅花 3")

    # (異) 驗證時要判斷第一回合首發是梅花三
    def validate_special_rule(self, card_pattern: CardPattern, top_play: CardPattern | None) -> bool:
        if top_play is None:
            cards = card_pattern.cards 
            return self._validate_having_clubs_3(cards)
        return True
