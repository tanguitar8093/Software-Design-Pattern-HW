from models.Based import Based
from models.Individual import Individual

class ReversedBased(Based):
    """ReversedBased."""
    
    def __init__(self, next: Based):
        self.next = next

    def match_user(self, me: Individual, users: list[Individual]) -> list[Individual]:
        """matchStrategy."""
        users = self.next.match_user(me, users)
        sorted_users = list(reversed(users))
        return sorted_users