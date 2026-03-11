from common.Decision import AbstractDecision
from models.Hand import Hand
from models.Card import Card


class Decision(AbstractDecision):
    """
    Showdown 決策抽象基底（繼承自 common.AbstractDecision）。

    覆寫 make_decision(hand, context=None)。
    Showdown 的決策不需要 context（不需頂牌資訊）。
    """

    def make_decision(self, hand: Hand, context=None) -> Card:
        pass
