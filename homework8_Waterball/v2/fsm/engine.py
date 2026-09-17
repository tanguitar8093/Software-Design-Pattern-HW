from __future__ import annotations
from typing import Any, List, Optional
from .plugin import FsmPlugin
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
        self._plugins: List[FsmPlugin] = []
        self._target: Any = None

    def setTarget(self, target: Any) -> None:
        self._target = target

    def getTarget(self) -> Any:
        return self._target

    def installPlugin(self, plugin: FsmPlugin) -> FiniteStateMachine:
        self._plugins.append(plugin)
        return self

    def addTransition(self, transition: Transition) -> None:
        self._transitions.append(transition)

    def getCurrentState(self) -> Optional[State]:
        return self._currentState

    def setCurrentState(self, state: Optional[State]) -> None:
        self._currentState = state

    def changeState(self, nextState: State, context: TransitionContext) -> None:
        old_state = self._currentState
        if self._currentState is not None:
            self._currentState.onExit(context)
        self._currentState = nextState
        if self._currentState is not None:
            self._currentState.onEnter(context)
        for p in self._plugins:
            p.onPostChangeState(self, old_state, nextState, context)

    def fire(self, trigger: Trigger) -> bool:
        context = TransitionContext(trigger=trigger, fsm=self, target=self._target)

        # 1. 外掛插件優先攔截處理 (Plugin Extension Point)
        for plugin in self._plugins:
            if plugin.onPreFire(self, context):
                return True

        # 2. 目前狀態嘗試消化（葉狀態 handle）
        if self._currentState is not None:
            handled = self._currentState.handle(context)
            if handled:
                return True

        # 3. 尋找符合 (currentState, triggerName) 的 Transition 候選者
        for trans in self._transitions:
            if trans.fromState == self._currentState and trans.triggerName == trigger.name:
                # 4. 評估 Guard 並執行 Action
                if trans.tryHandle(context):
                    # 5. 執行舊狀態 exit -> 切換 -> 新狀態 enter
                    self.changeState(trans.toState, context)
                    return True

        return False
