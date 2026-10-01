import unittest
from datetime import datetime

from v1.app.driver import AppDriver
from v1.app.event_line_parser import ParsedEvent
from v1.app.event_type import InputEventType
from v1.app.handler_chain import build_handler_chain
from v1.app.handler_context import HandlerContext
from v1.app.handlers.activity import ActivityHandler
from v1.app.handlers.base import EventHandler, HandlingResult
from v1.app.handlers.lifecycle import LifecycleHandler
from v1.app.handlers.membership import MembershipHandler
from v1.community.community import WaterCommunity


class TrackingTerminal(EventHandler):
    def __init__(self) -> None:
        super().__init__()
        self.requests: list[ParsedEvent] = []

    def can_handle(self, request: ParsedEvent) -> bool:
        return True

    def execute(self, request: ParsedEvent, context: HandlerContext) -> HandlingResult:
        self.requests.append(request)
        return HandlingResult.CONTINUE


class FutureEventHandler(EventHandler):
    def can_handle(self, request: ParsedEvent) -> bool:
        return request.name is InputEventType.UNKNOWN and request.rawName == "future event"

    def execute(self, request: ParsedEvent, context: HandlerContext) -> HandlingResult:
        context.output.append("future event handled")
        return HandlingResult.CONTINUE


class HandlerChainTest(unittest.TestCase):
    def test_unmatched_request_is_forwarded_to_next_handler(self) -> None:
        terminal = TrackingTerminal()
        context = HandlerContext([])
        request = ParsedEvent(InputEventType.UNKNOWN, {}, rawName="future event")

        self.assertIs(MembershipHandler(terminal).handle(request, context), HandlingResult.CONTINUE)
        self.assertEqual(terminal.requests, [request])

    def test_matching_request_is_handled_without_forwarding(self) -> None:
        terminal = TrackingTerminal()
        community = WaterCommunity(datetime(2023, 8, 7))
        context = HandlerContext([], community=community)

        result = MembershipHandler(terminal).handle(ParsedEvent(InputEventType.LOGIN, {"userId": "1"}), context)

        self.assertIs(result, HandlingResult.CONTINUE)
        self.assertEqual(community.getOnlineCount(), 1)
        self.assertEqual(terminal.requests, [])

    def test_unmatched_request_without_next_handler_fails_loudly(self) -> None:
        request = ParsedEvent(InputEventType.UNKNOWN, {}, rawName="future event")

        with self.assertRaisesRegex(RuntimeError, "no terminal handler"):
            MembershipHandler().handle(request, HandlerContext([]))

    def test_matched_request_before_start_is_consumed_without_forwarding(self) -> None:
        terminal = TrackingTerminal()

        result = MembershipHandler(terminal).handle(ParsedEvent(InputEventType.LOGIN, {}), HandlerContext([]))

        self.assertIs(result, HandlingResult.CONTINUE)
        self.assertEqual(terminal.requests, [])

    def test_end_handler_stops_without_forwarding(self) -> None:
        terminal = TrackingTerminal()
        context = HandlerContext([])

        result = LifecycleHandler(terminal).handle(ParsedEvent(InputEventType.END, {}), context)

        self.assertIs(result, HandlingResult.STOP)
        self.assertEqual(terminal.requests, [])

    def test_each_group_accepts_only_its_own_event_types(self) -> None:
        groups = (
            (LifecycleHandler(), {InputEventType.STARTED, InputEventType.END}),
            (MembershipHandler(), {InputEventType.LOGIN, InputEventType.LOGOUT}),
            (ActivityHandler(), {
                InputEventType.ELAPSED, InputEventType.NEW_MESSAGE, InputEventType.NEW_POST,
                InputEventType.GO_BROADCASTING, InputEventType.SPEAK, InputEventType.STOP_BROADCASTING,
            }),
        )
        for handler, event_types in groups:
            for event_type in InputEventType:
                self.assertEqual(handler.can_handle(ParsedEvent(event_type, {})), event_type in event_types)

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
