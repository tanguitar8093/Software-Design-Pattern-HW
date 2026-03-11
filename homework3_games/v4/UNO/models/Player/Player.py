from abc import abstractmethod
from common.Player import AbstractPlayer
from models.Hand import Hand
from models.Card import Card
from models.Decision.Decision import Decision


class Player(AbstractPlayer):
    """
    UNO 玩家抽象基底。

    繼承 common.AbstractPlayer，在 __init__ 中建立
    UNO 專用的 Hand（無上限）。
    新增 UNO 特有的 has_valid_card() 方法。
    """

    def __init__(self, decision: Decision):
        super().__init__(decision)
        self._hand = Hand()          # UNO 專用 Hand（無張數上限）

    @abstractmethod
    def name_himself(self) -> None:
        pass

    def has_valid_card(self, top_card: Card) -> bool:
        """判斷手牌中是否有可出的牌（同色或同數字）。"""
        return any(card.is_match(top_card) for card in self._hand.cards)
