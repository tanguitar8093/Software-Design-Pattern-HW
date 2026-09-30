from ..event_line_parser import ParsedEvent
from ..event_type import InputEventType
from ..handler_context import HandlerContext
from .base import EventHandler, HandlingResult


class ElapsedHandler(EventHandler):
    event_type = InputEventType.ELAPSED

    def execute(self, request: ParsedEvent, context: HandlerContext) -> HandlingResult:
        if context.community is not None:
            context.community.elapseTime(request.payload["amount"], request.payload["unit"])
        return HandlingResult.CONTINUE
