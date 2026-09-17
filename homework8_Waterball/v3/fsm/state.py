from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from .transition import TransitionContext

if TYPE_CHECKING:
    from .engine import FiniteStateMachine


class State(ABC):
    def __init__(self, id: str):
        self.id: str = id

    @abstractmethod
    def onEnter(self, context: TransitionContext) -> None:
        pass

    @abstractmethod
    def onExit(self, context: TransitionContext) -> None:
        pass

    @abstractmethod
    def handle(self, context: TransitionContext) -> bool:
        pass


class AtomicState(State, ABC):
    def onEnter(self, context: TransitionContext) -> None:
        pass

    def onExit(self, context: TransitionContext) -> None:
        pass

    def handle(self, context: TransitionContext) -> bool:
        return False


class CompositeState(State):
    def __init__(self, id: str, innerFsm: FiniteStateMachine):
        super().__init__(id)
        self._innerFsm: FiniteStateMachine = innerFsm

    def getInnerFsm(self) -> FiniteStateMachine:
        return self._innerFsm

    def onEnter(self, context: TransitionContext) -> None:
        curr = self._innerFsm.getCurrentState()
        if curr is not None:
            curr.onEnter(context)

    def onExit(self, context: TransitionContext) -> None:
        curr = self._innerFsm.getCurrentState()
        if curr is not None:
            curr.onExit(context)

    def handle(self, context: TransitionContext) -> bool:
        # README 子狀態機 OCP 規範：CompositeState handle 本身只回傳 False，
        # 子狀態機的 trigger 委派完全交由 SubStateMachinePlugin 執行。
        return False
