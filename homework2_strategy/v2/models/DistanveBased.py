from models.Based import Based
from models.Individual import Individual

class DistanveBased(Based):
    """DistanveBased."""
    
    def match_user(self, me: Individual, users: list[Individual]) -> list[Individual]:
        """matchStrategy."""
        
        def dist(compare_user) -> float:
            """dist."""
            x1, y1 = me.coord
            x2, y2 = compare_user.coord
            return (x1 - x2) ** 2 + (y1 - y2) ** 2
        
        sorted_users = sorted(users, key=dist)
        return sorted_users