from ..events.domain_events import (
    BroadcastStartedEvent,
    BroadcastStoppedEvent,
    LoginEvent,
    LogoutEvent,
    MessagePostedEvent,
    TimeElapsedEvent,
)
from ..fsm.core import Event, Trigger

BOT_TAG = "bot"  # Message.tags 標記機器人的統一慣例字串


class CommandTrigger(Trigger):
    def __init__(self, command: str):
        self.command = command

    def isTriggeredBy(self, event: Event) -> bool:
        if not isinstance(event, MessagePostedEvent):
            return False
        message = event.message
        return BOT_TAG in message.tags and message.content == self.command


class MentionsBotTrigger(Trigger):
    def isTriggeredBy(self, event: Event) -> bool:
        if not isinstance(event, MessagePostedEvent):
            return False
        return BOT_TAG in event.message.tags


class LoginTrigger(Trigger):
    def isTriggeredBy(self, event: Event) -> bool:
        return isinstance(event, LoginEvent)


class LogoutTrigger(Trigger):
    def isTriggeredBy(self, event: Event) -> bool:
        return isinstance(event, LogoutEvent)


class BroadcastStartedTrigger(Trigger):
    def isTriggeredBy(self, event: Event) -> bool:
        return isinstance(event, BroadcastStartedEvent)


class BroadcastStoppedTrigger(Trigger):
    def isTriggeredBy(self, event: Event) -> bool:
        return isinstance(event, BroadcastStoppedEvent)


class TimeElapsedTrigger(Trigger):
    def isTriggeredBy(self, event: Event) -> bool:
        return isinstance(event, TimeElapsedEvent)
