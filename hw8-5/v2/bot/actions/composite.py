from ...fsm.core import Action, Event


class NoopAction(Action):
    """Null Object：給不需要 entry/exit 行為的狀態卡位用，不認識任何業務語意。"""

    def execute(self, event: Event) -> None:
        pass


class CompositeAction(Action):
    def __init__(self, actions: list[Action]):
        self.actions = actions

    def execute(self, event: Event) -> None:
        for action in self.actions:
            action.execute(event)
