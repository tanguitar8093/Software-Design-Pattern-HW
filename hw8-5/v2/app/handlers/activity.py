from ..event_line_parser import ParsedEvent
from ..event_type import InputEventType
from ..handler_context import HandlerContext
from .base import EventHandler, HandlingResult


class ActivityHandler(EventHandler):
    """成員對社群的時間、內容與廣播操作，不包含生命週期或身分變動。"""

    event_types = frozenset((
        InputEventType.ELAPSED,
        InputEventType.NEW_MESSAGE,
        InputEventType.NEW_POST,
        InputEventType.GO_BROADCASTING,
        InputEventType.SPEAK,
        InputEventType.STOP_BROADCASTING,
    ))

    def execute(self, request: ParsedEvent, context: HandlerContext) -> HandlingResult:
        community = context.community
        if community is None:
            return HandlingResult.CONTINUE

        payload = request.payload
        if request.name is InputEventType.ELAPSED:
            community.elapseTime(payload["amount"], payload["unit"])
        elif request.name is InputEventType.NEW_MESSAGE:
            community.postMessage(str(payload["authorId"]), payload.get("content", ""), payload.get("tags", []))
        elif request.name is InputEventType.NEW_POST:
            community.createPost(
                str(payload["id"]),
                str(payload["authorId"]),
                payload.get("title", ""),
                payload.get("content", ""),
                payload.get("tags", []),
            )
        elif request.name is InputEventType.GO_BROADCASTING:
            community.startBroadcast(str(payload["speakerId"]))
        elif request.name is InputEventType.SPEAK:
            community.speak(str(payload["speakerId"]), payload.get("content", ""))
        else:
            community.stopBroadcast(str(payload["speakerId"]))
        return HandlingResult.CONTINUE
