from abc import ABC
from datetime import datetime as DateTime
from enum import Enum

from .channels import Broadcast, ChatRoom, Forum
from ..events.publisher import EventPublisher


class Role(Enum):
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"


class Participant(ABC):
    def __init__(self, id: str):
        self.id = id


class Member(Participant):
    def __init__(self, id: str, role: int):
        super().__init__(id)
        self.role = role

    def sendMessage(self, chatRoom: ChatRoom, content: str, tags: list[str]) -> None:
        raise NotImplementedError

    def publishPost(self, forum: Forum, title: str, content: str, tags: list[str]) -> None:
        raise NotImplementedError

    def commentPost(self, forum: Forum, postId: str, content: str, tags: list[str]) -> None:
        raise NotImplementedError

    def startBroadcast(self, broadcast: Broadcast) -> None:
        raise NotImplementedError

    def speak(self, broadcast: Broadcast, content: str) -> None:
        raise NotImplementedError

    def stopBroadcast(self, broadcast: Broadcast) -> None:
        raise NotImplementedError


class WaterCommunity:
    def __init__(self, currentTime: DateTime):
        self.currentTime = currentTime

    def login(self, participant: Participant) -> None:
        raise NotImplementedError

    def logout(self, participantId: str) -> None:
        raise NotImplementedError

    def elapseTime(self, amount: int, unit: str) -> None:
        raise NotImplementedError

    def getOnlineParticipants(self) -> list[Participant]:
        raise NotImplementedError

    def getOnlineCount(self) -> int:
        raise NotImplementedError

    def getEventPublisher(self) -> EventPublisher:
        raise NotImplementedError

    def postBotReply(self, content: str, tags: list[str]) -> None:
        raise NotImplementedError
