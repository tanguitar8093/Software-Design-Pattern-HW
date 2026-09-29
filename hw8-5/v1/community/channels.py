from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..events.publisher import EventPublisher  # 只用於型別注記，避免與 events.domain_events 形成循環 import


class Message:
    def __init__(self, authorId: str, content: str, tags: list[str]):
        self.authorId = authorId
        self.content = content
        self.tags = tags


class ChatRoom:
    def __init__(self, eventPublisher: "EventPublisher"):
        self._eventPublisher = eventPublisher

    def postMessage(self, message: Message) -> None:
        from ..events.domain_events import MessagePostedEvent  # 延遲 import 讓双方模組都先載完再互相引用

        self._eventPublisher.notify(MessagePostedEvent(message))


class Post:
    def __init__(self, id: str, authorId: str, title: str, content: str, tags: list[str]):
        self.id = id
        self.authorId = authorId
        self.title = title
        self.content = content
        self.tags = tags
        self._comments: list["Comment"] = []  # 圖上沒畫，但 addComment 缺一不可的內部緩衝

    def addComment(self, comment: "Comment") -> None:
        self._comments.append(comment)


class Comment:
    def __init__(self, authorId: str, content: str, tags: list[str]):
        self.authorId = authorId
        self.content = content
        self.tags = tags


class Forum:
    def __init__(self, eventPublisher: "EventPublisher"):
        self._eventPublisher = eventPublisher
        self._posts: dict[str, Post] = {}  # 圖上沒畫，但 createPost/getPost 缺一不可的內部存储

    def createPost(self, post: Post) -> None:
        from ..events.domain_events import PostCreatedEvent

        self._posts[post.id] = post
        self._eventPublisher.notify(PostCreatedEvent(post))

    def addComment(self, postId: str, comment: Comment) -> None:
        from ..events.domain_events import CommentAddedEvent

        self._posts[postId].addComment(comment)
        self._eventPublisher.notify(CommentAddedEvent(comment))

    def getPost(self, id: str) -> Post:
        return self._posts[id]


class VoiceMessage:
    def __init__(self, speakerId: str, content: str):
        self.speakerId = speakerId
        self.content = content


class Broadcast:
    def __init__(self, eventPublisher: "EventPublisher", currentSpeakerId: Optional[str] = None):
        self._eventPublisher = eventPublisher
        self.currentSpeakerId = currentSpeakerId

    def start(self, speakerId: str) -> None:
        from ..events.domain_events import BroadcastStartedEvent

        self.currentSpeakerId = speakerId
        self._eventPublisher.notify(BroadcastStartedEvent(speakerId))

    def speak(self, voiceMessage: VoiceMessage) -> None:
        from ..events.domain_events import VoiceSpokenEvent

        self._eventPublisher.notify(VoiceSpokenEvent(voiceMessage))

    def stop(self, speakerId: str) -> None:
        from ..events.domain_events import BroadcastStoppedEvent

        self.currentSpeakerId = None
        self._eventPublisher.notify(BroadcastStoppedEvent(speakerId))

    def isBroadcasting(self) -> bool:
        return self.currentSpeakerId is not None
