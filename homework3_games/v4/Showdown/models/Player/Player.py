from abc import abstractmethod
from common.Player import AbstractPlayer
from models.Hand import Hand
from models.Decision.Decision import Decision


class Player(AbstractPlayer):
    """
    Showdown 玩家抽象基底。

    繼承 common.AbstractPlayer，在 __init__ 中建立
    Showdown 專用的 Hand（上限 13 張）。
    name_himself() 仍為抽象，由 HumanPlayer / AIPlayer 實作。
    """

    def __init__(self, decision: Decision):
        super().__init__(decision)
        self._hand = Hand()          # Showdown 專用 Hand（最多 13 張）

    @abstractmethod
    def name_himself(self) -> None:
        pass
