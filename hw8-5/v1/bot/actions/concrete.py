from typing import Callable

from ...activities.knowledge_king import KnowledgeKingGame, Question
from ...activities.recording import RecordingSession
from ...events.domain_events import DomainEvent, PostCreatedEvent
from ...fsm.core import Action, Event
from ..bot import Bot
from ..states import QuestioningState, RecordingState


class CommentPostAction(Action):
    def __init__(self, bot: Bot, text: str, tagsProvider: Callable[[Event], list[str]]):
        self.bot = bot
        self.text = text
        self.tagsProvider = tagsProvider

    def execute(self, event: Event) -> None:
        if not isinstance(event, PostCreatedEvent):
            return
        self.bot.commentPost(event.post.id, self.text, self.tagsProvider(event))


class FlushRecordReplayAction(Action):
    def __init__(self, bot: Bot, recordingState: RecordingState):
        self.bot = bot
        self.recordingState = recordingState

    def execute(self, event: Event) -> None:
        self.bot.replyChatMessage(self.recordingState.session.generateReplay(), [])


class DeductQuotaAction(Action):
    def __init__(self, bot: Bot, cost: int):
        self.bot = bot
        self.cost = cost

    def execute(self, event: Event) -> None:
        self.bot.quota -= self.cost


class CreateRecordingSessionAction(Action):
    def __init__(self, recordingState: RecordingState):
        self.recordingState = recordingState

    def execute(self, event: Event) -> None:
        if not isinstance(event, DomainEvent):
            return
        recorderId = event.getSourceId()
        if recorderId is not None:
            self.recordingState.session = RecordingSession(recorderId)


class CreateKnowledgeKingGameAction(Action):
    def __init__(self, questioningState: QuestioningState, bot: Bot, questions: list[Question]):
        self.questioningState = questioningState
        self.bot = bot
        self.questions = questions

    def execute(self, event: Event) -> None:
        self.questioningState.game = KnowledgeKingGame(list(self.questions), self.bot.getCurrentTime())


class SendChatMessageAction(Action):
    def __init__(self, bot: Bot, contentProvider: Callable[[Event], str]):
        self.bot = bot
        self.contentProvider = contentProvider

    def execute(self, event: Event) -> None:
        self.bot.replyChatMessage(self.contentProvider(event), [])
