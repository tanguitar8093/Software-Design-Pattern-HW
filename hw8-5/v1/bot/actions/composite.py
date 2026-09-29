from ...fsm.core import Action, Event


class CompositeAction(Action):
    def __init__(self, actions: list[Action]):
        self.actions = actions

    def execute(self, event: Event) -> None:
        for action in self.actions:
            action.execute(event)
