from typing import Callable, Any, Type
from ..fsm.core import FiniteStateMachine, State, Transition, Event, Action, Guard
from .context import BotContext

class LambdaAction(Action):
    def __init__(self, func: Callable[[Event, BotContext], None]):
        self.func = func
    def execute(self, event: Event, context: Any) -> None:
        self.func(event, context)

class LambdaGuard(Guard):
    def __init__(self, func: Callable[[Event, BotContext], bool]):
        self.func = func
    def evaluate(self, event: Event, context: Any) -> bool:
        return self.func(event, context)

class FluentFSMBuilder:
    def __init__(self, initial_state: str):
        self.fsm = FiniteStateMachine(initial_state)

    def state(self, name: str, on_entry: Callable = None, on_exit: Callable = None, sub_machine: FiniteStateMachine = None) -> 'FluentFSMBuilder':
        entry = LambdaAction(on_entry) if on_entry else None
        exit_action = LambdaAction(on_exit) if on_exit else None
        s = State(name, entry, exit_action)
        if sub_machine:
             s.sub_machine = sub_machine
        self.fsm.add_state(s)
        return self

    def transition(self, from_state: str, event: str, to_state: str, guard: Callable = None, action: Callable = None) -> 'FluentFSMBuilder':
        g = LambdaGuard(guard) if guard else None
        a = LambdaAction(action) if action else None
        t = Transition(from_state, to_state, event, g, a)
        self.fsm.add_transition(t)
        return self
        
    def build(self) -> FiniteStateMachine:
        return self.fsm

