from typing import Optional

from ..community.community import BOT_ID
from ..events.domain_events import (
    BroadcastStartedEvent,
    BroadcastStoppedEvent,
    CommentAddedEvent,
    DomainEvent,
    MessagePostedEvent,
    PostCreatedEvent,
    TimeElapsedEvent,
    VoiceSpokenEvent,
)
from ..events.publisher import CommunityObserver


def _formatTags(tags: list[str]) -> str:
    if not tags:
        return ""
    return " " + ", ".join(f"@{tag}" for tag in tags)


class TranscriptObserver(CommunityObserver):
    """把 App 層關心的網域事件轉成輸出格式規定的逐行文字紀錄，跟 Bot 各自訂閱、互不影響。"""

    def __init__(self, output: list[str], id: str = "transcript"):
        self._id = id
        self.output = output

    def getId(self) -> str:
        return self._id

    def onEvent(self, event: DomainEvent) -> None:
        line = self._format(event)
        if line is not None:
            self.output.append(line)

    def _format(self, event: DomainEvent) -> Optional[str]:
        if isinstance(event, TimeElapsedEvent):
            return f"🕑 {event.amount} {event.unit} elapsed..."
        if isinstance(event, MessagePostedEvent):
            message = event.message
            tags = _formatTags(message.tags)
            if message.authorId == BOT_ID:
                return f"🤖: {message.content}{tags}"
            return f"💬 {message.authorId}: {message.content}{tags}"
        if isinstance(event, PostCreatedEvent):
            post = event.post
            tags = _formatTags(post.tags)
            return f"{post.authorId}: 【{post.title}】{post.content}{tags}"
        if isinstance(event, CommentAddedEvent):
            comment = event.comment
            if comment.authorId != BOT_ID:  # 規格只定義機器人留言的輸出格式
                return None
            tags = _formatTags(comment.tags)
            return f"🤖 comment in post {event.postId}: {comment.content}{tags}"
        if isinstance(event, BroadcastStartedEvent):
            if event.speakerId == BOT_ID:
                return "🤖 go broadcasting..."
            return f"📢 {event.speakerId} is broadcasting..."
        if isinstance(event, VoiceSpokenEvent):
            voice = event.voiceMessage
            if voice.speakerId == BOT_ID:
                return f"🤖 speaking: {voice.content}"
            return f"📢 {voice.speakerId}: {voice.content}"
        if isinstance(event, BroadcastStoppedEvent):
            if event.speakerId == BOT_ID:
                return "🤖 stop broadcasting..."
            return f"📢 {event.speakerId} stop broadcasting"
        return None
