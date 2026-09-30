from ..event_line_parser import ParsedEvent
from ..event_type import InputEventType
from ..handler_context import HandlerContext
from .base import EventHandler, HandlingResult


class NewMessageHandler(EventHandler):
    def handle(self, request: ParsedEvent, context: HandlerContext) -> HandlingResult:
        if request.name is not InputEventType.NEW_MESSAGE:
            return self.forward(request, context)
        if context.community is not None:
            payload = request.payload
            context.community.postMessage(str(payload["authorId"]), payload.get("content", ""), payload.get("tags", []))
        return HandlingResult.CONTINUE


class NewPostHandler(EventHandler):
    def handle(self, request: ParsedEvent, context: HandlerContext) -> HandlingResult:
        if request.name is not InputEventType.NEW_POST:
            return self.forward(request, context)
        if context.community is not None:
            payload = request.payload
            context.community.createPost(
                str(payload["id"]),
                str(payload["authorId"]),
                payload.get("title", ""),
                payload.get("content", ""),
                payload.get("tags", []),
            )
        return HandlingResult.CONTINUE
