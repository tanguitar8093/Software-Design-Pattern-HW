from __future__ import annotations
from abc import ABC
from typing import TYPE_CHECKING, List, Optional
from homework8_Waterball.v1.common.enums import Role

if TYPE_CHECKING:
    from homework8_Waterball.v1.domain.channels.broadcast import Broadcast
    from homework8_Waterball.v1.domain.channels.chat_room import ChatRoom
    from homework8_Waterball.v1.domain.channels.forum import Forum


class Participant(ABC):
    def __init__(self, id: str):
        self.id: str = id


class Member(Participant):
    def __init__(self, id: str, role: Role = Role.MEMBER):
        super().__init__(id)
        self.role: Role = role

    def sendMessage(self, chatRoom: ChatRoom, content: str, tags: Optional[List[str]] = None) -> None:
        from homework8_Waterball.v1.domain.channels.chat_room import Message
        msg = Message(self.id, content, tags)
        chatRoom.postMessage(msg)

    def publishPost(self, forum: Forum, title: str, content: str, tags: Optional[List[str]] = None) -> None:
        from homework8_Waterball.v1.domain.channels.forum import Post
        post = Post(str(id(self)), self.id, title, content, tags)
        forum.createPost(post)

    def commentPost(self, forum: Forum, postId: str, content: str, tags: Optional[List[str]] = None) -> None:
        from homework8_Waterball.v1.domain.channels.forum import Comment
        comment = Comment(self.id, content, tags)
        forum.addComment(postId, comment)

    def startBroadcast(self, broadcast: Broadcast) -> None:
        broadcast.start(self.id)

    def speak(self, broadcast: Broadcast, content: str) -> None:
        from homework8_Waterball.v1.domain.channels.broadcast import VoiceMessage
        broadcast.speak(VoiceMessage(self.id, content))

    def stopBroadcast(self, broadcast: Broadcast) -> None:
        broadcast.stop(self.id)
