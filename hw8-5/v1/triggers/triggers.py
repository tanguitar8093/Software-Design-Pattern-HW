from ..events.domain_events import (
    BroadcastStartedEvent,
    BroadcastStoppedEvent,
    LoginEvent,
    LogoutEvent,
    TimeElapsedEvent,
)
from ..fsm.core import Event, Trigger


class CommandTrigger(Trigger):
    def __init__(self, command: str):
        self.command = command

    def isTriggeredBy(self, event: Event) -> bool:
        raise NotImplementedError


class MentionsBotTrigger(Trigger):
    def isTriggeredBy(self, event: Event) -> bool:
        raise NotImplementedError


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
