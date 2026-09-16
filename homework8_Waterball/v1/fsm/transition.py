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

    def tryHandle(self, context: TransitionContext) -> bool:
        if self._guard is not None and not self._guard.isSatisfied(context):
            return False
        if self._action is not None:
            self._action.execute(context)
        return True
