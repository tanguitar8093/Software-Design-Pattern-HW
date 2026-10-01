import unittest

from v1.app.transcript_observer import TranscriptObserver
from v1.community.channels import Comment, Message, Post, VoiceMessage
from v1.events.domain_events import (
    BroadcastStartedEvent,
    BroadcastStoppedEvent,
    CommentAddedEvent,
    MessagePostedEvent,
    PostCreatedEvent,
    TimeElapsedEvent,
    VoiceSpokenEvent,
)


class TranscriptObserverTest(unittest.TestCase):
    def setUp(self) -> None:
        self.output: list[str] = []
        self.observer = TranscriptObserver(self.output)

    def test_time_elapsed(self) -> None:
        self.observer.onEvent(TimeElapsedEvent(10, "seconds"))
        self.assertEqual(self.output, ["🕑 10 seconds elapsed..."])

    def test_member_message_without_tags(self) -> None:
        self.observer.onEvent(MessagePostedEvent(Message("1", "hello", [])))
        self.assertEqual(self.output, ["💬 1: hello"])

    def test_member_message_with_tags(self) -> None:
        self.observer.onEvent(MessagePostedEvent(Message("3", "hi", ["1", "2"])))
        self.assertEqual(self.output, ["💬 3: hi @1, @2"])

    def test_bot_message_uses_bot_prefix(self) -> None:
        self.observer.onEvent(MessagePostedEvent(Message("bot", "thank you", ["4"])))
        self.assertEqual(self.output, ["🤖: thank you @4"])

    def test_post_created(self) -> None:
        self.observer.onEvent(PostCreatedEvent(Post("1", "8", "title", "content", ["1", "2"])))
        self.assertEqual(self.output, ["8: 【title】content @1, @2"])

    def test_bot_comment_is_formatted(self) -> None:
        self.observer.onEvent(CommentAddedEvent("1", Comment("bot", "Nice post", ["8"])))
        self.assertEqual(self.output, ["🤖 comment in post 1: Nice post @8"])

    def test_member_comment_has_no_defined_format(self) -> None:
        self.observer.onEvent(CommentAddedEvent("1", Comment("2", "me too", [])))
        self.assertEqual(self.output, [])

    def test_member_broadcast_started(self) -> None:
        self.observer.onEvent(BroadcastStartedEvent("4"))
        self.assertEqual(self.output, ["📢 4 is broadcasting..."])

    def test_bot_broadcast_started(self) -> None:
        self.observer.onEvent(BroadcastStartedEvent("bot"))
        self.assertEqual(self.output, ["🤖 go broadcasting..."])

    def test_member_voice_spoken(self) -> None:
        self.observer.onEvent(VoiceSpokenEvent(VoiceMessage("4", "大家早安")))
        self.assertEqual(self.output, ["📢 4: 大家早安"])

    def test_bot_voice_spoken(self) -> None:
        self.observer.onEvent(VoiceSpokenEvent(VoiceMessage("bot", "The winner is 2")))
        self.assertEqual(self.output, ["🤖 speaking: The winner is 2"])

    def test_member_broadcast_stopped(self) -> None:
        self.observer.onEvent(BroadcastStoppedEvent("4"))
        self.assertEqual(self.output, ["📢 4 stop broadcasting"])

    def test_bot_broadcast_stopped(self) -> None:
        self.observer.onEvent(BroadcastStoppedEvent("bot"))
        self.assertEqual(self.output, ["🤖 stop broadcasting..."])


if __name__ == "__main__":
    unittest.main()
