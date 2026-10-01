import unittest

from v1.app.event_line_parser import parseLine
from v1.app.event_type import InputEventType


class EventLineParserTest(unittest.TestCase):
    def test_parses_bracketed_event_with_payload(self) -> None:
        parsed = parseLine('[started] {"time": "2023-08-07 00:00:00", "quota": 10}')
        assert parsed is not None
        self.assertIs(parsed.name, InputEventType.STARTED)
        self.assertEqual(parsed.payload, {"time": "2023-08-07 00:00:00", "quota": 10})

    def test_parses_event_without_payload(self) -> None:
        parsed = parseLine("[end]")
        assert parsed is not None
        self.assertIs(parsed.name, InputEventType.END)
        self.assertEqual(parsed.payload, {})

    def test_parses_elapsed_event(self) -> None:
        parsed = parseLine("[10 seconds elapsed]")
        assert parsed is not None
        self.assertIs(parsed.name, InputEventType.ELAPSED)
        self.assertEqual(parsed.payload, {"amount": 10, "unit": "seconds"})

    def test_parses_elapsed_event_with_other_units(self) -> None:
        parsed = parseLine("[1 hour elapsed]")
        assert parsed is not None
        self.assertEqual(parsed.payload, {"amount": 1, "unit": "hour"})

    def test_tolerates_extra_whitespace_before_payload(self) -> None:
        parsed = parseLine('[new post]  {"id": "1", "authorId": "8", "title": "t", "content": "c", "tags": []}')
        assert parsed is not None
        self.assertIs(parsed.name, InputEventType.NEW_POST)
        self.assertEqual(parsed.payload["id"], "1")

    def test_unknown_event_preserves_its_name(self) -> None:
        parsed = parseLine('[future event] {"newField": 1}')
        assert parsed is not None
        self.assertIs(parsed.name, InputEventType.UNKNOWN)
        self.assertEqual(parsed.rawName, "future event")
        self.assertEqual(parsed.payload, {"newField": 1})

    def test_blank_line_returns_none(self) -> None:
        self.assertIsNone(parseLine("   "))
        self.assertIsNone(parseLine(""))


if __name__ == "__main__":
    unittest.main()
