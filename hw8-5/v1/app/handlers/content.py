from ..event_line_parser import ParsedEvent
from ..event_type import InputEventType
from ..handler_context import HandlerContext
from .base import EventHandler, HandlingResult


class NewMessageHandler(EventHandler):
    event_type = InputEventType.NEW_MESSAGE

    def execute(self, request: ParsedEvent, context: HandlerContext) -> HandlingResult:
        if context.community is not None:
            payload = request.payload
            context.community.postMessage(str(payload["authorId"]), payload.get("content", ""), payload.get("tags", []))
        return HandlingResult.CONTINUE


class NewPostHandler(EventHandler):
    event_type = InputEventType.NEW_POST

    def execute(self, request: ParsedEvent, context: HandlerContext) -> HandlingResult:
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
