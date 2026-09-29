from datetime import datetime as DateTime
from datetime import timedelta
from typing import Callable, Optional

from ...community.community import Member, Role
from ...events.domain_events import DomainEvent, MessagePostedEvent
from ...fsm.core import Event, Guard
from ..bot import Bot
from ..states import QuestioningState, RecordingState


class OnlineCountAtLeastGuard(Guard):
    def __init__(self, bot: Bot, threshold: int):
        self.bot = bot
        self.threshold = threshold

    def isSatisfied(self, event: Event) -> bool:
        return self.bot.getOnlineCount() >= self.threshold


class IsBroadcastingGuard(Guard):
    def __init__(self, bot: Bot):
        self.bot = bot

    def isSatisfied(self, event: Event) -> bool:
        return self.bot.isBroadcasting()


class AdminOnlyGuard(Guard):
    def __init__(self, bot: Bot):
        self.bot = bot

    def isSatisfied(self, event: Event) -> bool:
        if not isinstance(event, DomainEvent):
            return False
        participant = self.bot.getParticipant(event.getSourceId())
        return isinstance(participant, Member) and participant.role == Role.ADMIN


class QuotaAvailableGuard(Guard):
    def __init__(self, bot: Bot, cost: int):
        self.bot = bot
        self.cost = cost

    def isSatisfied(self, event: Event) -> bool:
        return self.bot.quota >= self.cost


class CorrectAnswerGuard(Guard):
    def __init__(self, questioningState: QuestioningState):
        self.questioningState = questioningState
        self._lastEvent: Optional[Event] = None
        self._lastResult: bool = False

    def isSatisfied(self, event: Event) -> bool:
        if not isinstance(event, MessagePostedEvent):
            return False
        if event is self._lastEvent:  # 同一次 fire() 裡被別條 Transition 重複問，避免重複計分（N20）
            return self._lastResult
        self._lastEvent = event
        self._lastResult = self.questioningState.game.submitAnswer(event.getSourceId(), event.message.content)
        return self._lastResult


class GameFinishedGuard(Guard):
    def __init__(self, questioningState: QuestioningState):
        self.questioningState = questioningState

    def isSatisfied(self, event: Event) -> bool:
        return self.questioningState.game.isFinished()


class IsRecorderGuard(Guard):
    def __init__(self, recordingState: RecordingState):
        self.recordingState = recordingState

    def isSatisfied(self, event: Event) -> bool:
        if not isinstance(event, MessagePostedEvent):
            return False
        return event.getSourceId() == self.recordingState.session.recorderId


class DurationElapsedGuard(Guard):
    def __init__(self, bot: Bot, duration: int, unit: str, getAnchorTime: Callable[[], DateTime]):
        self.bot = bot
        self.duration = duration
        self.unit = unit
        self.getAnchorTime = getAnchorTime

    def isSatisfied(self, event: Event) -> bool:
        key = self.unit if self.unit.endswith("s") else f"{self.unit}s"
        threshold = timedelta(**{key: self.duration})
        return self.bot.getCurrentTime() - self.getAnchorTime() >= threshold
