from __future__ import annotations
from typing import Any, List, Optional
from .state import State
from .transition import (
    Transition,
    TransitionContext,
    Trigger,
)


class FiniteStateMachine:
    def __init__(self, initialState: Optional[State] = None):
        self._currentState: Optional[State] = initialState
        self._transitions: List[Transition] = []
        self._target: Any = None

    def setTarget(self, target: Any) -> None:
        self._target = target

    def addTransition(self, transition: Transition) -> None:
        self._transitions.append(transition)

    def getCurrentState(self) -> Optional[State]:
        return self._currentState

    def changeState(self, nextState: State, context: TransitionContext) -> None:
        if self._currentState is not None:
            self._currentState.onExit(context)
        self._currentState = nextState
        if self._currentState is not None:
            self._currentState.onEnter(context)

    def fire(self, trigger: Trigger) -> bool:
        context = TransitionContext(trigger=trigger, fsm=self, target=self._target)

        # 1. 優先由目前狀態內部消化（Composite 委派或 Leaf 處理）
        if self._currentState is not None:
            handled = self._currentState.handle(context)
            if handled:
                return True

        # 2. 尋找符合 (currentState, triggerName) 的 Transition 候選者
        for trans in self._transitions:
            if trans.fromState == self._currentState and trans.triggerName == trigger.name:
                # 3. 評估 Guard 並執行 Action
                if trans.tryHandle(context):
                    # 4. 執行舊狀態 exit -> 切換 -> 新狀態 enter
                    self.changeState(trans.toState, context)
                    return True

        return False
