from abc import ABC, abstractmethod
from models.Individual import Individual
class Based(ABC):
    """Based."""
    
    @abstractmethod
    def match_user(self, me: Individual, users: list[Individual]) -> list[Individual]:
        """matchStrategy."""
        pass