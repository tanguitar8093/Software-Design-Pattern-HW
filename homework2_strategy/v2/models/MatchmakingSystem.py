from models.Individual import Individual
from models.Based import Based
from models.ReversedBased import ReversedBased
from models.HabitBased import HabitBased
from models.DistanveBased import DistanveBased

class MatchmakingSystem:
    def __init__(self,matching_strategy: Based ,me: Individual, users: list[Individual]) -> None:
        self._matching_strategy: Based  = matching_strategy
        self._me: Individual = me
        self._users: list[Individual] = users
    def match_user(self) -> Individual:
        matched_users = self._matching_strategy.match_user(self._me, self._users)
        return matched_users[0]
     