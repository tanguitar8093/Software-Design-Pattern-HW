from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class Trigger:
    """
    通用 FSM 觸發事件：
    - name: 事件名稱
    - payload: 事件內容資料
    """
    def __init__(self, name: String, payload: Optional[Dict[str, Any]] = None):
        self.name: str = name
        self.payload: Dict[str, Any] = payload if payload is not None else {}


class TransitionContext:
    """
    轉移上下文：提供 Guard、Action、State 運作時所需的環境資料
    - trigger: 觸發此轉移的 Trigger
    - fsm: 驅動的狀態機
    - target: 綁定的主體對象（例如 Bot）
    """
    def __init__(self, trigger: Trigger, fsm: FiniteStateMachine, target: Any = None):
        self.trigger: Trigger = trigger
        self.fsm: FiniteStateMachine = fsm
        self.target: Any = target


class Guard(ABC):
    """
    轉移守衛條件策略介面 (Strategy Pattern)
    """
    @abstractmethod
    def isSatisfied(self, context: TransitionContext) -> bool:
        pass


class Action(ABC):
    """
    轉移動作策略介面 (Strategy Pattern)
    """
    @abstractmethod
    def execute(self, context: TransitionContext) -> None:
        pass


class State(ABC):
    """
    狀態介面 (State Pattern / Composite Component)
    """
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
        """
        處理非轉移事件（如輪播回覆、內部消化）。
        若事件已被內部消化處理，回傳 True；若未處理回傳 False。
        """
        pass


class AtomicState(State, ABC):
    """
    原子葉狀態 (Composite Leaf)
    """
    def onEnter(self, context: TransitionContext) -> None:
        pass

    def onExit(self, context: TransitionContext) -> None:
        pass

    def handle(self, context: TransitionContext) -> bool:
        return False


class Transition:
    """
    狀態轉移類別：
    - fromState: 起始狀態
    - toState: 目標狀態
    - triggerName: 觸發事件名稱
    - guard: 條件策略
    - action: 副作用策略
    """
    def __init__(
        self,
        fromState: State,
        toState: State,
        triggerName: str,
        guard: Optional[Guard] = None,
        action: Optional[Action] = None,
    ):
        self.fromState: State = fromState
        self.toState: State = toState
        self.triggerName: str = triggerName
        self._guard: Optional[Guard] = guard
        self._action: Optional[Action] = action

    def tryHandle(self, context: TransitionContext) -> bool:
        if self._guard is not None and not self._guard.isSatisfied(context):
            return False
        if self._action is not None:
            self._action.execute(context)
        return True


class FiniteStateMachine:
    """
    通用有限狀態機引擎 (Template Method Pattern):
    - currentState: 目前所處狀態
    - transitions: 轉移清單
    - fire(trigger): 固化轉移核心生命週期演算法
    """
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

        # 1. 優先嘗試由目前狀態內部消化（Composite 委派或 Leaf 處理）
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


class CompositeState(State):
    """
    複合狀態 / 子狀態機插件 (Composite Pattern / Sub-FSM Plugin)
    內部持有一台 FiniteStateMachine (innerFsm)，支援任意深度嵌套
    """
    def __init__(self, id: str, innerFsm: FiniteStateMachine):
        super().__init__(id)
        self._innerFsm: FiniteStateMachine = innerFsm

    def getInnerFsm(self) -> FiniteStateMachine:
        return self._innerFsm

    def onEnter(self, context: TransitionContext) -> None:
        # 進入 CompositeState 時，若 innerFsm 有初始狀態，觸發其 onEnter
        curr = self._innerFsm.getCurrentState()
        if curr is not None:
            curr.onEnter(context)

    def onExit(self, context: TransitionContext) -> None:
        # 退出 CompositeState 時，遞迴退出 innerFsm 目前狀態
        curr = self._innerFsm.getCurrentState()
        if curr is not None:
            curr.onExit(context)

    def handle(self, context: TransitionContext) -> bool:
        # 委派給內部子狀態機先嘗試處理
        return self._innerFsm.fire(context.trigger)
