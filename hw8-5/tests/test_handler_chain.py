import unittest
from datetime import datetime

from v1.app.driver import AppDriver
from v1.app.event_line_parser import ParsedEvent
from v1.app.event_type import InputEventType
from v1.app.handler_chain import build_handler_chain
from v1.app.handler_context import HandlerContext
from v1.app.handlers.base import EventHandler, HandlingResult
from v1.app.handlers.lifecycle import EndHandler
from v1.app.handlers.membership import LoginHandler
from v1.community.community import WaterCommunity


class TrackingTerminal(EventHandler):
    def __init__(self) -> None:
        super().__init__()
        self.requests: list[ParsedEvent] = []

    def handle(self, request: ParsedEvent, context: HandlerContext) -> HandlingResult:
        self.requests.append(request)
        return HandlingResult.CONTINUE


class FutureEventHandler(EventHandler):
    def handle(self, request: ParsedEvent, context: HandlerContext) -> HandlingResult:
        if request.name is not InputEventType.UNKNOWN or request.rawName != "future event":
            return self.forward(request, context)
        context.output.append("future event handled")
        return HandlingResult.CONTINUE


class HandlerChainTest(unittest.TestCase):
    def test_unmatched_request_is_forwarded_to_next_handler(self) -> None:
        terminal = TrackingTerminal()
        context = HandlerContext([])
        request = ParsedEvent(InputEventType.UNKNOWN, {}, rawName="future event")

        self.assertIs(LoginHandler(terminal).handle(request, context), HandlingResult.CONTINUE)
        self.assertEqual(terminal.requests, [request])

    def test_matching_request_is_handled_without_forwarding(self) -> None:
        terminal = TrackingTerminal()
        community = WaterCommunity(datetime(2023, 8, 7))
        context = HandlerContext([], community=community)

        result = LoginHandler(terminal).handle(ParsedEvent(InputEventType.LOGIN, {"userId": "1"}), context)

        self.assertIs(result, HandlingResult.CONTINUE)
        self.assertEqual(community.getOnlineCount(), 1)
        self.assertEqual(terminal.requests, [])

    def test_end_handler_stops_without_forwarding(self) -> None:
        terminal = TrackingTerminal()
        context = HandlerContext([])

        result = EndHandler(terminal).handle(ParsedEvent(InputEventType.END, {}), context)

        self.assertIs(result, HandlingResult.STOP)
        self.assertEqual(terminal.requests, [])

    def test_unknown_event_is_handled_at_default_chain_tail(self) -> None:
        context = HandlerContext([])
        request = ParsedEvent(InputEventType.UNKNOWN, {}, rawName="future event")
        self.assertIs(build_handler_chain().handle(request, context), HandlingResult.CONTINUE)
        self.assertEqual(context.output, [])

    def test_custom_handler_can_be_prepended_without_changing_driver(self) -> None:
        driver = AppDriver(handler_chain=FutureEventHandler(build_handler_chain()))

        output = driver.run(
            [
                '[started] {"time": "2023-08-07 00:00:00", "quota": 10}',
                '[future event] {"newField": 1}',
                '[login] {"userId": "1"}',
                "[end]",
                '[future event] {"newField": 2}',
            ]
        )

        self.assertEqual(output, ["future event handled"])
        assert driver.community is not None
        self.assertEqual(driver.community.getOnlineCount(), 1)


if __name__ == "__main__":
    unittest.main()
