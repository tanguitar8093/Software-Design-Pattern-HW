from ..event_line_parser import ParsedEvent
from ..event_type import InputEventType
from ..handler_context import HandlerContext
from .base import EventHandler, HandlingResult


class ElapsedHandler(EventHandler):
    def handle(self, request: ParsedEvent, context: HandlerContext) -> HandlingResult:
        if request.name is not InputEventType.ELAPSED:
            return self.forward(request, context)
        if context.community is not None:
            context.community.elapseTime(request.payload["amount"], request.payload["unit"])
        return HandlingResult.CONTINUE
