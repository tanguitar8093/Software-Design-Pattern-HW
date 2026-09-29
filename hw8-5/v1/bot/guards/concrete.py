from datetime import datetime as DateTime
from datetime import timedelta
from typing import Callable, Optional

from ...community.community import Member, Role
from ...events.domain_events import DomainEvent, MessagePostedEvent
from ...fsm.core import Event, FiniteStateMachine, Guard, StateNode
from ..bot import Bot
from ..states import QuestioningState


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
    """錄音者身分跟著 Bot.recorderId 走（下 record 指令的人），不綁定任何一次的 RecordingSession。"""

    def __init__(self, bot: Bot):
        self.bot = bot

    def isSatisfied(self, event: Event) -> bool:
        if not isinstance(event, MessagePostedEvent):
            return False
        return event.getSourceId() == self.bot.recorderId


class SubstateActiveGuard(Guard):
    """通用組件：判斷某台複合 FSM 目前作用中的子狀態是不是指定的那一顆（給跨子狀態的最外層轉移用）。"""

    def __init__(self, fsm: FiniteStateMachine, expected: StateNode):
        self.fsm = fsm
        self.expected = expected

    def isSatisfied(self, event: Event) -> bool:
        return self.fsm.currentState is self.expected


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
