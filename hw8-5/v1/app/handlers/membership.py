from ...community.community import Member, Role
from ..event_line_parser import ParsedEvent
from ..event_type import InputEventType
from ..handler_context import HandlerContext
from .base import EventHandler, HandlingResult


class LoginHandler(EventHandler):
    event_type = InputEventType.LOGIN

    def execute(self, request: ParsedEvent, context: HandlerContext) -> HandlingResult:
        if context.community is not None:
            payload = request.payload
            role = Role.ADMIN if payload.get("isAdmin", False) else Role.MEMBER
            context.community.login(Member(str(payload["userId"]), role))
        return HandlingResult.CONTINUE


class LogoutHandler(EventHandler):
    event_type = InputEventType.LOGOUT

    def execute(self, request: ParsedEvent, context: HandlerContext) -> HandlingResult:
        if context.community is not None:
            context.community.logout(str(request.payload["userId"]))
        return HandlingResult.CONTINUE
