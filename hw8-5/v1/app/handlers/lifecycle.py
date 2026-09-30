from datetime import datetime as DateTime
from typing import Final

from ...bot.facade import BotFacade
from ...community.community import WaterCommunity
from ..event_line_parser import ParsedEvent
from ..event_type import InputEventType
from ..handler_context import HandlerContext
from ..transcript_observer import TranscriptObserver
from .base import EventHandler, HandlingResult

START_TIME_FORMAT: Final[str] = "%Y-%m-%d %H:%M:%S"


class LifecycleHandler(EventHandler):
    event_types = frozenset((InputEventType.STARTED, InputEventType.END))

    def execute(self, request: ParsedEvent, context: HandlerContext) -> HandlingResult:
        if request.name is InputEventType.END:
            return HandlingResult.STOP
        payload = request.payload
        quota = payload.get("quota")
        if type(quota) is not int or quota <= 0:
            raise ValueError("[started] quota must be a positive integer")
        current_time = DateTime.strptime(payload["time"], START_TIME_FORMAT)
        community = WaterCommunity(current_time)
        community.getEventPublisher().register(TranscriptObserver(context.output))
        context.community = community
        facade = BotFacade(community, quota=quota)
        context.bot = facade.bot
        return HandlingResult.CONTINUE


class UnknownEventHandler(EventHandler):
    """鏈尾：保留原有未知事件靜默略過的行為。"""

    def can_handle(self, request: ParsedEvent) -> bool:
        return True

    def execute(self, request: ParsedEvent, context: HandlerContext) -> HandlingResult:
        return HandlingResult.CONTINUE
