from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from .engine import FiniteStateMachine
    from .state import State


class Trigger:
    def __init__(self, name: str, payload: Optional[Dict[str, Any]] = None):
        self.name: str = name
        self.payload: Dict[str, Any] = payload if payload is not None else {}


class TransitionContext:
    def __init__(self, trigger: Trigger, fsm: FiniteStateMachine, target: Any = None):
        self.trigger: Trigger = trigger
        self.fsm: FiniteStateMachine = fsm
        self.target: Any = target


class Guard(ABC):
    @abstractmethod
    def isSatisfied(self, context: TransitionContext) -> bool:
        pass


class Action(ABC):
    @abstractmethod
    def execute(self, context: TransitionContext) -> None:
        pass


class Transition:
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

    def isTriggeredBy(self, currentState: Optional[State], trigger: Trigger) -> bool:
        return self.fromState == currentState and self.triggerName == trigger.name

    def isAllowed(self, context: TransitionContext) -> bool:
        if self._guard is not None:
            return self._guard.isSatisfied(context)
        return True

    def executeAction(self, context: TransitionContext) -> None:
        if self._action is not None:
            self._action.execute(context)

    def tryHandle(self, context: TransitionContext) -> bool:
        if not self.isAllowed(context):
            return False
        self.executeAction(context)
        return True
