from ...community.community import Member, Role
from ..event_line_parser import ParsedEvent
from ..event_type import InputEventType
from ..handler_context import HandlerContext
from .base import EventHandler, HandlingResult


class LoginHandler(EventHandler):
    def handle(self, request: ParsedEvent, context: HandlerContext) -> HandlingResult:
        if request.name is not InputEventType.LOGIN:
            return self.forward(request, context)
        if context.community is not None:
            payload = request.payload
            role = Role.ADMIN if payload.get("isAdmin", False) else Role.MEMBER
            context.community.login(Member(str(payload["userId"]), role))
        return HandlingResult.CONTINUE


class LogoutHandler(EventHandler):
    def handle(self, request: ParsedEvent, context: HandlerContext) -> HandlingResult:
        if request.name is not InputEventType.LOGOUT:
            return self.forward(request, context)
        if context.community is not None:
            context.community.logout(str(request.payload["userId"]))
        return HandlingResult.CONTINUE
