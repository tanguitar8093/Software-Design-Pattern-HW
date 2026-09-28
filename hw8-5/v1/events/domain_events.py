from abc import ABC, abstractmethod
from typing import Optional

from ..community.channels import Comment, Message, Post, VoiceMessage
from ..fsm.core import Event


class DomainEvent(Event, ABC):
    @abstractmethod
    def getSourceId(self) -> Optional[str]:
        raise NotImplementedError


class MessagePostedEvent(DomainEvent):
    def __init__(self, message: Message):
        self.message = message

    def getSourceId(self) -> Optional[str]:
        return self.message.authorId


class PostCreatedEvent(DomainEvent):
    def __init__(self, post: Post):
        self.post = post

    def getSourceId(self) -> Optional[str]:
        return self.post.authorId


class CommentAddedEvent(DomainEvent):
    def __init__(self, comment: Comment):
        self.comment = comment

    def getSourceId(self) -> Optional[str]:
        return self.comment.authorId


class BroadcastStartedEvent(DomainEvent):
    def __init__(self, speakerId: str):
        self.speakerId = speakerId

    def getSourceId(self) -> Optional[str]:
        return self.speakerId


class BroadcastStoppedEvent(DomainEvent):
    def __init__(self, speakerId: str):
        self.speakerId = speakerId

    def getSourceId(self) -> Optional[str]:
        return self.speakerId


class VoiceSpokenEvent(DomainEvent):
    def __init__(self, voiceMessage: VoiceMessage):
        self.voiceMessage = voiceMessage

    def getSourceId(self) -> Optional[str]:
        return self.voiceMessage.speakerId


class LoginEvent(DomainEvent):
    def __init__(self, userId: str, isAdmin: bool):
        self.userId = userId
        self.isAdmin = isAdmin

    def getSourceId(self) -> Optional[str]:
        return self.userId


class LogoutEvent(DomainEvent):
    def __init__(self, userId: str):
        self.userId = userId

    def getSourceId(self) -> Optional[str]:
        return self.userId


class TimeElapsedEvent(DomainEvent):
    def __init__(self, amount: int, unit: str):
        self.amount = amount
        self.unit = unit

    def getSourceId(self) -> Optional[str]:
        return None
