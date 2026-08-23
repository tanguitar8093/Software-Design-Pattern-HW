from typing import Any, Callable, Dict, List, Optional
from abc import ABC, abstractmethod

class Event:
    def __init__(self, name: str, payload: Dict[str, Any] = None):
        self.name = name
        self.payload = payload or {}

class Action(ABC):
    @abstractmethod
    def execute(self, event: Event, context: Any) -> None:
        pass

class Guard(ABC):
    @abstractmethod
    def evaluate(self, event: Event, context: Any) -> bool:
        pass

class Transition:
    def __init__(self, from_state: str, to_state: str, event_name: str, guard: Optional[Guard] = None, action: Optional[Action] = None):
        self.from_state = from_state
        self.to_state = to_state
        self.event_name = event_name
        self.guard = guard
        self.action = action

class State:
    def __init__(self, name: str, entry_action: Optional[Action] = None, exit_action: Optional[Action] = None):
        self.name = name
        self.entry_action = entry_action
        self.exit_action = exit_action
        self.sub_machine: Optional['FiniteStateMachine'] = None

class FiniteStateMachine:
    def __init__(self, initial_state: str):
        self.states: Dict[str, State] = {}
        self.transitions: List[Transition] = []
        self.initial_state = initial_state
        self.current_state: Optional[str] = None
        self.context: Any = None

    def add_state(self, state: State) -> None:
        self.states[state.name] = state

    def add_transition(self, transition: Transition) -> None:
        self.transitions.append(transition)

    def set_context(self, context: Any) -> None:
        self.context = context

    def start(self) -> None:
        if self.initial_state not in self.states:
            raise ValueError(f"Initial state '{self.initial_state}' not found.")
        self._enter_state(self.initial_state, None)

    def current(self) -> State:
        return self.states[self.current_state]

    def _enter_state(self, state_name: str, event: Optional[Event]) -> None:
        self.current_state = state_name
        state = self.states[state_name]
        
        if state.entry_action:
            state.entry_action.execute(event, self.context)
            
        if state.sub_machine:
             state.sub_machine.set_context(self.context)
             state.sub_machine.start()

    def _exit_state(self, state_name: str, event: Optional[Event]) -> None:
         state = self.states[state_name]
         if state.exit_action:
             state.exit_action.execute(event, self.context)

    def dispatch(self, event: Event) -> bool:
        if self.current_state is None:
            return False

        current_state_obj = self.states[self.current_state]
        
        # Dispatch to submachine first
        if current_state_obj.sub_machine:
            if current_state_obj.sub_machine.dispatch(event):
                return True

        for transition in self.transitions:
            if transition.from_state == self.current_state and transition.event_name == event.name:
                if transition.guard is None or transition.guard.evaluate(event, self.context):
                    self._exit_state(self.current_state, event)
                    
                    if transition.action:
                        transition.action.execute(event, self.context)
                        
                    self._enter_state(transition.to_state, event)
                    return True
        return False
