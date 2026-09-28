class Message:
    def __init__(self, authorId: str, content: str, tags: list[str]):
        self.authorId = authorId
        self.content = content
        self.tags = tags


class ChatRoom:
    def postMessage(self, message: Message) -> None:
        raise NotImplementedError


class Post:
    def __init__(self, id: str, authorId: str, title: str, content: str, tags: list[str]):
        self.id = id
        self.authorId = authorId
        self.title = title
        self.content = content
        self.tags = tags

    def addComment(self, comment: "Comment") -> None:
        raise NotImplementedError


class Comment:
    def __init__(self, authorId: str, content: str, tags: list[str]):
        self.authorId = authorId
        self.content = content
        self.tags = tags


class Forum:
    def createPost(self, post: Post) -> None:
        raise NotImplementedError

    def addComment(self, postId: str, comment: Comment) -> None:
        raise NotImplementedError

    def getPost(self, id: str) -> Post:
        raise NotImplementedError


class VoiceMessage:
    def __init__(self, speakerId: str, content: str):
        self.speakerId = speakerId
        self.content = content


class Broadcast:
    def __init__(self, currentSpeakerId: str):
        self.currentSpeakerId = currentSpeakerId

    def start(self, speakerId: str) -> None:
        raise NotImplementedError

    def speak(self, voiceMessage: VoiceMessage) -> None:
        raise NotImplementedError

    def stop(self, speakerId: str) -> None:
        raise NotImplementedError

    def isBroadcasting(self) -> bool:
        raise NotImplementedError
