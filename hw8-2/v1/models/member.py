from typing import List

from .broadcast import Broadcast, VoiceMessage
from .chat_room import ChatRoom, Message
from .enums import Role
from .forum import Comment, Forum, Post
from .participant import Participant


class Member(Participant):
    """對應 OOA-Clean.mmd Member：社群互動、下指令的意圖發起者。"""

    def __init__(self, id: str, role: Role) -> None:
        super().__init__(id)
        self.role = role

    def send_message(self, chat_room: ChatRoom, content: str, tags: List[str]) -> None:
        chat_room.post_message(Message(self.id, content, tags))

    def publish_post(self, forum: Forum, id: str, title: str, content: str, tags: List[str]) -> None:
        forum.create_post(Post(id, self.id, title, content, tags))

    def comment_post(self, forum: Forum, post_id: str, content: str, tags: List[str]) -> None:
        forum.add_comment(post_id, Comment(self.id, content, tags))

    def start_broadcast(self, broadcast: Broadcast) -> None:
        broadcast.start(self.id)

    def speak(self, broadcast: Broadcast, content: str) -> None:
        broadcast.speak(VoiceMessage(self.id, content))

    def stop_broadcast(self, broadcast: Broadcast) -> None:
        broadcast.stop(self.id)
