from ..fsm.core import Action, Event, Guard


class AndGuard(Guard):
    def __init__(self, guards: list[Guard]):
        self.guards = guards

    def isSatisfied(self, event: Event) -> bool:
        raise NotImplementedError


class NotGuard(Guard):
    def __init__(self, guard: Guard):
        self.guard = guard

    def isSatisfied(self, event: Event) -> bool:
        raise NotImplementedError


class CompositeAction(Action):
    def __init__(self, actions: list[Action]):
        self.actions = actions

    def execute(self, event: Event) -> None:
        raise NotImplementedError
