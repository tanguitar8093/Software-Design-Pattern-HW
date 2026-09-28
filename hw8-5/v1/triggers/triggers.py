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
        raise NotImplementedError


class LogoutTrigger(Trigger):
    def isTriggeredBy(self, event: Event) -> bool:
        raise NotImplementedError


class BroadcastStartedTrigger(Trigger):
    def isTriggeredBy(self, event: Event) -> bool:
        raise NotImplementedError


class BroadcastStoppedTrigger(Trigger):
    def isTriggeredBy(self, event: Event) -> bool:
        raise NotImplementedError


class TimeElapsedTrigger(Trigger):
    def isTriggeredBy(self, event: Event) -> bool:
        raise NotImplementedError
