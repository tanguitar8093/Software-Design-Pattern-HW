from ...community.community import BOT_ID
from ...events.domain_events import (
    BroadcastStartedEvent,
    BroadcastStoppedEvent,
    LoginEvent,
    LogoutEvent,
    MessagePostedEvent,
    PostCreatedEvent,
    TimeElapsedEvent,
    VoiceSpokenEvent,
)
from ...fsm.core import Event, Trigger

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


class MessageFromMemberTrigger(Trigger):
    """任何非機器人自己發出的聊天訊息，不要求標記機器人（輪播回覆用，跟 MentionsBotTrigger 不同）。"""

    def isTriggeredBy(self, event: Event) -> bool:
        if not isinstance(event, MessagePostedEvent):
            return False
        return event.message.authorId != BOT_ID


class PostCreatedTrigger(Trigger):
    def isTriggeredBy(self, event: Event) -> bool:
        return isinstance(event, PostCreatedEvent)


class VoiceSpokenTrigger(Trigger):
    def isTriggeredBy(self, event: Event) -> bool:
        return isinstance(event, VoiceSpokenEvent)


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
