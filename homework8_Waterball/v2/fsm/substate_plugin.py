from __future__ import annotations
from typing import TYPE_CHECKING
from .plugin import FsmPlugin

if TYPE_CHECKING:
    from .engine import FiniteStateMachine
    from .transition import TransitionContext
    from .state import CompositeState


class SubStateMachinePlugin(FsmPlugin):
    """
    子狀態機插件 (Sub-state Machine Plugin):
    實現 README 設計需求 - 1：子狀態機功能獨立抽離為插件，遵守 OCP 原則。
    當目前狀態為 CompositeState 時，優先將 Trigger 委派給內部的子狀態機 (_innerFsm) 處理。
    若子狀態機成功處理，則阻止外層狀態機重複轉移。
    """
    def onPreFire(self, fsm: FiniteStateMachine, context: TransitionContext) -> bool:
        from .state import CompositeState
        curr = fsm.getCurrentState()
        if isinstance(curr, CompositeState):
            # 委派至內層子狀態機處理
            return curr.handle(context)
        return False
