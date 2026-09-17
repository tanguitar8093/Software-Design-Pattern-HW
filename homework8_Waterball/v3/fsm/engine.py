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
    def __init__(self, initialState: Optional[State] = None, target: Any = None):
        self._currentState: Optional[State] = initialState
        self._transitions: List[Transition] = []
        self._plugins: List[FsmPlugin] = []
        self._target: Any = target

    def setTarget(self, target: Any) -> None:
        self._target = target

    def getTarget(self) -> Any:
        return self._target

    def installPlugin(self, plugin: FsmPlugin) -> FiniteStateMachine:
        if plugin not in self._plugins:
            self._plugins.append(plugin)
        return self

    def uninstallPlugin(self, plugin: FsmPlugin) -> None:
        if plugin in self._plugins:
            self._plugins.remove(plugin)

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
            p.afterStateChanged(self, old_state, nextState, context)

    def fire(self, trigger: Trigger) -> bool:
        context = TransitionContext(trigger=trigger, fsm=self, target=self._target)

        # 1. 外掛插件優先攔截處理 (README 子狀態機 OCP Extension Point)
        for plugin in self._plugins:
            if plugin.beforeStateHandle(self, context):
                return True

        # 2. 目前狀態嘗試消化（葉狀態 handle）
        if self._currentState is not None:
            handled = self._currentState.handle(context)
            if handled:
                return True

        # 3. 尋找符合 (currentState, triggerName) 的 Transition 候選者
        for trans in self._transitions:
            if trans.isTriggeredBy(self._currentState, trigger):
                # 4. 評估 Guard
                if trans.isAllowed(context):
                    # 5. 固定轉換順序：oldState.onExit -> transition.executeAction -> newState.onEnter
                    old_state = self._currentState
                    if old_state is not None:
                        old_state.onExit(context)
                    trans.executeAction(context)
                    self._currentState = trans.toState
                    if self._currentState is not None:
                        self._currentState.onEnter(context)
                    for p in self._plugins:
                        p.afterStateChanged(self, old_state, trans.toState, context)
                    return True

        return False
