from dataclasses import dataclass
from models.player.player import Player

@dataclass
class RoundResult:
    top_player: Player
    is_game_over: bool
