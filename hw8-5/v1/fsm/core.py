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
        self.enter.execute(event)

    def onExit(self, event: Event) -> None:
        self.exit.execute(event)

    def fire(self, event: Event) -> bool:
        return False


class InitialStateSelector(ABC):
    @abstractmethod
    def select(self, event: Event) -> StateNode:
        raise NotImplementedError


class Transition:
    def __init__(
        self,
        from_: StateNode,
        trigger: Trigger,
        to: StateNode,
        guard: Optional[Guard] = None,
        action: Optional[Action] = None,
    ):
        self.from_ = from_
        self.trigger = trigger
        self.guard = guard
        self.action = action
        self.to = to

    def isApplicable(self, currentState: StateNode, event: Event) -> bool:
        if currentState is not self.from_:
            return False
        if not self.trigger.isTriggeredBy(event):
            return False
        if self.guard is not None and not self.guard.isSatisfied(event):
            return False
        return True


class FiniteStateMachine(StateNode):
    def __init__(
        self,
        currentState: Optional[StateNode],
        initialStateSelector: InitialStateSelector,
        transitions: list[Transition],
    ):
        self.currentState = currentState
        self.initialStateSelector = initialStateSelector
        self.transitions = transitions

    def addTransition(self, transition: Transition) -> None:
        self.transitions.append(transition)

    def onEnter(self, event: Event) -> None:
        self.currentState = self.initialStateSelector.select(event)
        self.currentState.onEnter(event)

    def onExit(self, event: Event) -> None:
        if self.currentState is not None:
            self.currentState.onExit(event)

    def fire(self, event: Event) -> bool:
        if self.currentState is not None and self.currentState.fire(event):
            return True
        for transition in self.transitions:
            if transition.isApplicable(self.currentState, event):
                self.currentState.onExit(event)
                if transition.action is not None:
                    transition.action.execute(event)
                self.currentState = transition.to
                self.currentState.onEnter(event)
                return True
        return False
