from abc import ABC, abstractmethod


class AbstractDecision(ABC):
    """
    抽象決策介面（Strategy 模式基底）。

    統一兩個遊戲的決策方法簽名：
      make_decision(hand, context=None)
    - Showdown：context 為 None（不需要額外資訊）。
    - UNO：context 為當前頂牌（Card），決定是否可出牌。
    """

    @abstractmethod
    def make_decision(self, hand, context=None):
        """
        從手牌中選出一張牌。

        :param hand:    玩家目前的手牌物件。
        :param context: 選用上下文資訊（UNO 傳入頂牌；Showdown 傳入 None）。
        :return:        選出的 Card 物件；若無法出牌則回傳 None。
        """
        pass
