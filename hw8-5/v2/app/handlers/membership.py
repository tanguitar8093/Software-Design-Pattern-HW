from ...community.community import Member, Role
from ..event_line_parser import ParsedEvent
from ..event_type import InputEventType
from ..handler_context import HandlerContext
from .base import EventHandler, HandlingResult


class MembershipHandler(EventHandler):
    event_types = frozenset((InputEventType.LOGIN, InputEventType.LOGOUT))

    def execute(self, request: ParsedEvent, context: HandlerContext) -> HandlingResult:
        if context.community is not None:
            payload = request.payload
            if request.name is InputEventType.LOGIN:
                role = Role.ADMIN if payload.get("isAdmin", False) else Role.MEMBER
                context.community.login(Member(str(payload["userId"]), role))
            else:
                context.community.logout(str(payload["userId"]))
        return HandlingResult.CONTINUE
