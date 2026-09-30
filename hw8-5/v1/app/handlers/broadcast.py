from ..event_line_parser import ParsedEvent
from ..event_type import InputEventType
from ..handler_context import HandlerContext
from .base import EventHandler, HandlingResult


class GoBroadcastingHandler(EventHandler):
    event_type = InputEventType.GO_BROADCASTING

    def execute(self, request: ParsedEvent, context: HandlerContext) -> HandlingResult:
        if context.community is not None:
            context.community.startBroadcast(str(request.payload["speakerId"]))
        return HandlingResult.CONTINUE


class SpeakHandler(EventHandler):
    event_type = InputEventType.SPEAK

    def execute(self, request: ParsedEvent, context: HandlerContext) -> HandlingResult:
        if context.community is not None:
            payload = request.payload
            context.community.speak(str(payload["speakerId"]), payload.get("content", ""))
        return HandlingResult.CONTINUE


class StopBroadcastingHandler(EventHandler):
    event_type = InputEventType.STOP_BROADCASTING

    def execute(self, request: ParsedEvent, context: HandlerContext) -> HandlingResult:
        if context.community is not None:
            context.community.stopBroadcast(str(request.payload["speakerId"]))
        return HandlingResult.CONTINUE
