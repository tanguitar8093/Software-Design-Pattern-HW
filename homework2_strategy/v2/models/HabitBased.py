from models.Based import Based
from models.Individual import Individual

class HabitBased(Based):
    """HabitBased."""
    
    def match_user(self, me: Individual, users: list[Individual]) -> list[Individual]:
        """matchStrategy."""
        def calculate_common_count(user):
            return len(set(user.habits).intersection(set(me.habits)))
        sorted_users = sorted(users, key=calculate_common_count, reverse=True)
        return sorted_users