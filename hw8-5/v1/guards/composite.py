from ..fsm.core import Action, Event, Guard


class AndGuard(Guard):
    def __init__(self, guards: list[Guard]):
        self.guards = guards

    def isSatisfied(self, event: Event) -> bool:
        return all(guard.isSatisfied(event) for guard in self.guards)


class NotGuard(Guard):
    def __init__(self, guard: Guard):
        self.guard = guard

    def isSatisfied(self, event: Event) -> bool:
        return not self.guard.isSatisfied(event)


class CompositeAction(Action):
    def __init__(self, actions: list[Action]):
        self.actions = actions

    def execute(self, event: Event) -> None:
        for action in self.actions:
            action.execute(event)
