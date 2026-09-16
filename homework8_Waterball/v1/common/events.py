from __future__ import annotations
from typing import TYPE_CHECKING, Any
from homework8_Waterball.v1.common.enums import CommunityEventType
from homework8_Waterball.v1.common.observer import CommunityEvent

if TYPE_CHECKING:
    from homework8_Waterball.v1.domain.channels.broadcast import VoiceMessage
    from homework8_Waterball.v1.domain.channels.chat_room import Message
    from homework8_Waterball.v1.domain.channels.forum import Post


class MessageReceivedEvent(CommunityEvent):
    def __init__(self, message: Message):
        super().__init__(CommunityEventType.MESSAGE_RECEIVED)
        self.message: Message = message

    def dispatchTo(self, bot: Any) -> None:
        bot.onMessageReceived(self.message)


class PostPublishedEvent(CommunityEvent):
    def __init__(self, post: Post):
        super().__init__(CommunityEventType.POST_PUBLISHED)
        self.post: Post = post

    def dispatchTo(self, bot: Any) -> None:
        bot.onPostPublished(self.post)


class BroadcastStartedEvent(CommunityEvent):
    def __init__(self, speakerId: str):
        super().__init__(CommunityEventType.BROADCAST_STARTED)
        self.speakerId: str = speakerId

    def dispatchTo(self, bot: Any) -> None:
        bot.onBroadcastStarted(self.speakerId)


class VoiceSpokenEvent(CommunityEvent):
    def __init__(self, voiceMessage: VoiceMessage):
        super().__init__(CommunityEventType.VOICE_SPOKEN)
        self.voiceMessage: VoiceMessage = voiceMessage

    def dispatchTo(self, bot: Any) -> None:
        bot.onVoiceSpoken(self.voiceMessage)


class BroadcastStoppedEvent(CommunityEvent):
    def __init__(self, speakerId: str):
        super().__init__(CommunityEventType.BROADCAST_STOPPED)
        self.speakerId: str = speakerId

    def dispatchTo(self, bot: Any) -> None:
        bot.onBroadcastStopped(self.speakerId)


class TimeElapsedEvent(CommunityEvent):
    def __init__(self, seconds: int):
        super().__init__(CommunityEventType.TIME_ELAPSED)
        self.seconds: int = seconds

    def dispatchTo(self, bot: Any) -> None:
        bot.onTimeElapsed(self.seconds)


class OnlineChangedEvent(CommunityEvent):
    def __init__(self, onlineCount: int):
        super().__init__(CommunityEventType.ONLINE_CHANGED)
        self.onlineCount: int = onlineCount

    def dispatchTo(self, bot: Any) -> None:
        if hasattr(bot, "onOnlineChanged"):
            bot.onOnlineChanged(self.onlineCount)
