from models.Individual import Individual
from enums import MatchingType
class MatchmakingSystem:
    def __init__(self,matching_type: MatchingType,me: Individual, users: list[Individual],is_reversed: bool= False) -> None:
        self._matching_type: MatchingType = matching_type  
        self._is_reversed: bool = is_reversed
        self._me: Individual = me
        self._users: list[Individual] = users
    def match_user(self) -> Individual:
        best_match: Individual
        if self._matching_type == MatchingType.DISTANCE:
            best_distance = float('-inf') if self._is_reversed else float('inf')
            def dist(a, b):
                x1, y1 = a.coord
                x2, y2 = b.coord
                return (x1 - x2) ** 2 + (y1 - y2) ** 2
            for user in self._users:
                distance = dist(self._me, user)
                if self._is_reversed:
                    if distance > best_distance:
                        best_distance = distance
                        best_match = user
                else:
                    if distance < best_distance:
                        best_distance = distance
                        best_match = user
        elif self._matching_type == MatchingType.HABIT:
            best_common_habits = float('inf') if self._is_reversed else -1
            for user in self._users:
                common_habits = len(set(self._me.habits) & set(user.habits))
                if self._is_reversed:
                    if common_habits < best_common_habits:
                        best_common_habits = common_habits
                        best_match = user
                else:
                    if common_habits > best_common_habits:
                        best_common_habits = common_habits
                        best_match = user
        return best_match
