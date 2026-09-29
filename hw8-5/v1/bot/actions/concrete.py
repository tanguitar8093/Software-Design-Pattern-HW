from typing import Callable

from ...fsm.core import Action, Event


class CommentPostAction(Action):
    def __init__(self, text: str, tagsProvider: Callable):
        self.text = text
        self.tagsProvider = tagsProvider

    def execute(self, event: Event) -> None:
        raise NotImplementedError


class FlushRecordReplayAction(Action):
    def execute(self, event: Event) -> None:
        raise NotImplementedError


class DeductQuotaAction(Action):
    def __init__(self, cost: int):
        self.cost = cost

    def execute(self, event: Event) -> None:
        raise NotImplementedError


class CreateRecordingSessionAction(Action):
    def execute(self, event: Event) -> None:
        raise NotImplementedError


class CreateKnowledgeKingGameAction(Action):
    def execute(self, event: Event) -> None:
        raise NotImplementedError


class SendChatMessageAction(Action):
    def __init__(self, contentProvider: Callable):
        self.contentProvider = contentProvider

    def execute(self, event: Event) -> None:
        raise NotImplementedError
