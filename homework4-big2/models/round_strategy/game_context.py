from __future__ import annotations
from typing import Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from models.player import Player
    from models.pattern import CardPattern

# Static Duck Typing: 為了解決雙向依賴的問題, DIP+ISP
class GameContext(Protocol):
    @property
    def players(self) -> list[Player]: 
        ...

    @property
    def rounds(self) -> int: 
        ...

    @property
    def top_play(self) -> CardPattern | None: 
        ...

    @top_play.setter
    def top_play(self, value: CardPattern | None) -> None:
        ...

    @property
    def top_player(self) -> Player | None:
        ...

    @top_player.setter
    def top_player(self, player: Player | None) -> None:
        ...

    def validate_end_game(self, player: Player) -> bool:
        ...

    def set_players_order(self, players: list[Player]) -> None:
        ...