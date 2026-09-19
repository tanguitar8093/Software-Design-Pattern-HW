from dataclasses import dataclass, field
from typing import List, Optional

from .formatting import with_tags


@dataclass
class Message:
    author_id: str
    content: str
    tags: List[str] = field(default_factory=list)


class ChatRoom:
    """對應 OOA-Clean.mmd ChatRoom：輸出訊息至終端，非 Bot 發言時通報 Bot。"""

    def __init__(self) -> None:
        self.bot: Optional["Bot"] = None  # noqa: F821 (由 WaterballCommunity 組裝時注入)

    def post_message(self, message: Message) -> None:
        if message.author_id == "bot":
            print(f"🤖: {with_tags(message.content, message.tags)}")
        else:
            print(f"💬 {message.author_id}: {with_tags(message.content, message.tags)}")
            self.bot.on_message_received(message)
