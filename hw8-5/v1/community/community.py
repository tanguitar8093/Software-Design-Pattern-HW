from abc import ABC
from datetime import datetime as DateTime
from datetime import timedelta
from enum import Enum
from typing import Optional
from uuid import uuid4

from .channels import Broadcast, ChatRoom, Comment, Forum, Message, Post, VoiceMessage
from ..events.domain_events import LoginEvent, LogoutEvent, TimeElapsedEvent
from ..events.publisher import EventPublisher

BOT_ID = "bot"  # Bot 以社群成員身份發言時統一使用的 authorId/speakerId


class Role(Enum):
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"


class Participant(ABC):
    def __init__(self, id: str):
        self.id = id


class Member(Participant):
    def __init__(self, id: str, role: Role):
        super().__init__(id)
        self.role = role

    def sendMessage(self, chatRoom: ChatRoom, content: str, tags: list[str]) -> None:
        chatRoom.postMessage(Message(self.id, content, tags))

    def publishPost(self, forum: Forum, title: str, content: str, tags: list[str]) -> None:
        forum.createPost(Post(str(uuid4()), self.id, title, content, tags))

    def commentPost(self, forum: Forum, postId: str, content: str, tags: list[str]) -> None:
        forum.addComment(postId, Comment(self.id, content, tags))

    def startBroadcast(self, broadcast: Broadcast) -> None:
        broadcast.start(self.id)

    def speak(self, broadcast: Broadcast, content: str) -> None:
        broadcast.speak(VoiceMessage(self.id, content))

    def stopBroadcast(self, broadcast: Broadcast) -> None:
        broadcast.stop(self.id)


class WaterCommunity:
    def __init__(self, currentTime: DateTime):
        self.currentTime = currentTime
        self._eventPublisher = EventPublisher([])
        self._chatRoom = ChatRoom(self._eventPublisher)
        self._forum = Forum(self._eventPublisher)
        self._broadcast = Broadcast(self._eventPublisher)
        self._onlineParticipants: dict[str, Participant] = {}

    def login(self, participant: Participant) -> None:
        self._onlineParticipants[participant.id] = participant
        isAdmin = isinstance(participant, Member) and participant.role == Role.ADMIN
        self._eventPublisher.notify(LoginEvent(participant.id, isAdmin))

    def logout(self, participantId: str) -> None:
        self._onlineParticipants.pop(participantId, None)
        self._eventPublisher.notify(LogoutEvent(participantId))

    def elapseTime(self, amount: int, unit: str) -> None:
        key = unit if unit.endswith("s") else f"{unit}s"
        self.currentTime += timedelta(**{key: amount})
        self._eventPublisher.notify(TimeElapsedEvent(amount, unit))

    def getOnlineParticipants(self) -> list[Participant]:
        return list(self._onlineParticipants.values())

    def getOnlineCount(self) -> int:
        return len(self._onlineParticipants)

    def getParticipant(self, participantId: str) -> Optional[Participant]:
        return self._onlineParticipants.get(participantId)

    def isBroadcasting(self) -> bool:
        return self._broadcast.isBroadcasting()

    def getEventPublisher(self) -> EventPublisher:
        return self._eventPublisher

    def postMessage(self, authorId: str, content: str, tags: list[str]) -> None:
        """App 層專用：以成員身份發訊息，不需要拿到 ChatRoom 實例。"""
        self._chatRoom.postMessage(Message(authorId, content, tags))

    def createPost(self, id: str, authorId: str, title: str, content: str, tags: list[str]) -> None:
        self._forum.createPost(Post(id, authorId, title, content, tags))

    def addComment(self, postId: str, authorId: str, content: str, tags: list[str]) -> None:
        self._forum.addComment(postId, Comment(authorId, content, tags))

    def startBroadcast(self, speakerId: str) -> None:
        self._broadcast.start(speakerId)

    def speak(self, speakerId: str, content: str) -> None:
        self._broadcast.speak(VoiceMessage(speakerId, content))

    def stopBroadcast(self, speakerId: str) -> None:
        self._broadcast.stop(speakerId)

    def postBotReply(self, content: str, tags: list[str]) -> None:
        self._chatRoom.postMessage(Message(BOT_ID, content, tags))

    def postBotComment(self, postId: str, content: str, tags: list[str]) -> None:
        self._forum.addComment(postId, Comment(BOT_ID, content, tags))

    def postBotVoice(self, content: str) -> None:
        self._broadcast.speak(VoiceMessage(BOT_ID, content))
