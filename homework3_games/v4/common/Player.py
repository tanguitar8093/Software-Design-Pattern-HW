from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from common.Decision import AbstractDecision


class AbstractPlayer(ABC):
    """
    抽象玩家基底類別（共用於 Showdown 與 UNO）。

    封裝所有遊戲共用的玩家狀態（名稱、分數、手牌、決策）。
    具體遊戲的 Player 子類別繼承此類，並在 __init__ 中初始化
    遊戲專用的 Hand 物件，以及實作 name_himself()。

    出牌統一透過 show(context=None)，委派給注入的 Decision 物件：
      - Showdown：show() / show(context=None) → 決策不使用 context
      - UNO：     show(top_card)               → 決策使用 context 作為頂牌
    """

    def __init__(self, decision: 'AbstractDecision'):
        self._point: int = 0
        self._hand = None          # 由子類別的 __init__ 初始化為遊戲專用 Hand
        self._name: str = ""
        self._decision: 'AbstractDecision' = decision

    # ── 屬性 ──────────────────────────────────────────
    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def point(self) -> int:
        return self._point

    # ── 抽象方法 ──────────────────────────────────────
    @abstractmethod
    def name_himself(self) -> None:
        """提示玩家輸入名稱，或為 AI 自動設定名稱。"""
        pass

    # ── 具體方法 ──────────────────────────────────────
    def show(self, context=None):
        """出牌：統一委派給 Decision.make_decision(hand, context)。"""
        return self._decision.make_decision(self._hand, context)

    def add_point(self, point: int = 1) -> None:
        self._point += point

    def add_hand(self, card) -> None:
        self._hand.add_card(card)

    def has_empty_hand(self) -> bool:
        return len(self._hand.cards) == 0
