# Transition 為 FSM 模組外部依賴（完整定義見 fsm-ooa-4.mmd），此檔案不重複定義，僅以字串型別註記引用。
from abc import ABC, abstractmethod
from typing import Optional


class Event(ABC):
    """Marker interface，本身不宣告任何方法。"""


class Trigger(ABC):
    @abstractmethod
    def isTriggeredBy(self, event: Event) -> bool:
        raise NotImplementedError


class Guard(ABC):
    @abstractmethod
    def isSatisfied(self, event: Event) -> bool:
        raise NotImplementedError


class Action(ABC):
    @abstractmethod
    def execute(self, event: Event) -> None:
        raise NotImplementedError


class StateNode(ABC):
    @abstractmethod
    def onEnter(self, event: Event) -> None:
        raise NotImplementedError

    @abstractmethod
    def onExit(self, event: Event) -> None:
        raise NotImplementedError

    @abstractmethod
    def fire(self, event: Event) -> bool:
        raise NotImplementedError


class State(StateNode):
    def __init__(self, enter: Action, exit: Action):
        self.enter = enter
        self.exit = exit

    def onEnter(self, event: Event) -> None:
        raise NotImplementedError

    def onExit(self, event: Event) -> None:
        raise NotImplementedError

    def fire(self, event: Event) -> bool:
        raise NotImplementedError


class InitialStateSelector(ABC):
    @abstractmethod
    def select(self, event: Event) -> StateNode:
        raise NotImplementedError


class FiniteStateMachine(StateNode):
    def __init__(
        self,
        currentState: Optional[StateNode],
        initialStateSelector: InitialStateSelector,
        transitions: "list[Transition]",
    ):
        self.currentState = currentState
        self.initialStateSelector = initialStateSelector
        self.transitions = transitions

    def addTransition(self, transition: "Transition") -> None:
        raise NotImplementedError

    def onEnter(self, event: Event) -> None:
        raise NotImplementedError

    def onExit(self, event: Event) -> None:
        raise NotImplementedError

    def fire(self, event: Event) -> bool:
        raise NotImplementedError
