from ..event_line_parser import ParsedEvent
from ..event_type import InputEventType
from ..handler_context import HandlerContext
from .base import EventHandler, HandlingResult


class GoBroadcastingHandler(EventHandler):
    def handle(self, request: ParsedEvent, context: HandlerContext) -> HandlingResult:
        if request.name is not InputEventType.GO_BROADCASTING:
            return self.forward(request, context)
        if context.community is not None:
            context.community.startBroadcast(str(request.payload["speakerId"]))
        return HandlingResult.CONTINUE


class SpeakHandler(EventHandler):
    def handle(self, request: ParsedEvent, context: HandlerContext) -> HandlingResult:
        if request.name is not InputEventType.SPEAK:
            return self.forward(request, context)
        if context.community is not None:
            payload = request.payload
            context.community.speak(str(payload["speakerId"]), payload.get("content", ""))
        return HandlingResult.CONTINUE


class StopBroadcastingHandler(EventHandler):
    def handle(self, request: ParsedEvent, context: HandlerContext) -> HandlingResult:
        if request.name is not InputEventType.STOP_BROADCASTING:
            return self.forward(request, context)
        if context.community is not None:
            context.community.stopBroadcast(str(request.payload["speakerId"]))
        return HandlingResult.CONTINUE
