from common.Decision import AbstractDecision
from models.Hand import Hand
from models.Card import Card


class Decision(AbstractDecision):
    """
    UNO 決策抽象基底（繼承自 common.AbstractDecision）。

    覆寫 make_decision(hand, context=None)。
    UNO 的 context 為當前頂牌（Card），決策需根據它篩選可出的牌。
    """

    def make_decision(self, hand: Hand, context: Card = None) -> Card:
        pass
