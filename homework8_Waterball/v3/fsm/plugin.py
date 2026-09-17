from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from .engine import FiniteStateMachine
    from .transition import TransitionContext


class FsmPlugin(ABC):
    """
    FSM 插件規範介面 (Plugin Interface):
    遵守 OCP 原則。在核心 FiniteStateMachine 完全不修改的前提下，
    透過註冊插件 (Plugin) 來擴充狀態機功能（例如階層式子狀態機 Composite Plugin）。
    若 Client 專案未引入此插件，核心 FSM 依然能獨立完整運作。
    """
    @abstractmethod
    def beforeStateHandle(self, fsm: FiniteStateMachine, context: TransitionContext) -> bool:
        """
        在 FSM 評估狀態自身 handle 與常態轉移 (Transitions) 之前觸發。
        若回傳 True，表示插件已成功消化該事件（如由子狀態機內部處理），FSM 不再執行外層轉移。
        """
        pass

    def afterStateChanged(self, fsm: FiniteStateMachine, oldState: Optional[Any], newState: Optional[Any], context: TransitionContext) -> None:
        """狀態切換後的掛鉤回呼 (可選實作)"""
        pass
