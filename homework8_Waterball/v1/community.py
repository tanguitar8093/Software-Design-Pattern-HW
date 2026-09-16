from __future__ import annotations
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, List, Optional


class Role(Enum):
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"


class CommunityEventType(Enum):
    MESSAGE_RECEIVED = "MESSAGE_RECEIVED"
    POST_PUBLISHED = "POST_PUBLISHED"
    BROADCAST_STARTED = "BROADCAST_STARTED"
    VOICE_SPOKEN = "VOICE_SPOKEN"
    BROADCAST_STOPPED = "BROADCAST_STOPPED"
    TIME_ELAPSED = "TIME_ELAPSED"
    ONLINE_CHANGED = "ONLINE_CHANGED"


class CommunityEvent(ABC):
    def __init__(self, event_type: CommunityEventType):
        self.type: CommunityEventType = event_type

    @abstractmethod
    def dispatchTo(self, bot: Any) -> None:
        pass


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


class CommunityObserver(ABC):
    @abstractmethod
    def update(self, event: CommunityEvent) -> None:
        pass


class Observable(ABC):
    def __init__(self):
        self._observers: List[CommunityObserver] = []

    def register(self, observer: CommunityObserver) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def unregister(self, observer: CommunityObserver) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, event: CommunityEvent) -> None:
        for obs in list(self._observers):
            obs.update(event)


class Message:
    def __init__(self, authorId: str, content: str, tags: Optional[List[str]] = None):
        self.authorId: str = authorId
        self.content: str = content
        self.tags: List[str] = tags if tags is not None else []


class Comment:
    def __init__(self, authorId: str, content: str, tags: Optional[List[str]] = None):
        self.authorId: str = authorId
        self.content: str = content
        self.tags: List[str] = tags if tags is not None else []


class Post:
    def __init__(self, id: str, authorId: str, title: str, content: str, tags: Optional[List[str]] = None):
        self.id: str = id
        self.authorId: str = authorId
        self.title: str = title
        self.content: str = content
        self.tags: List[str] = tags if tags is not None else []
        self._comments: List[Comment] = []

    def addComment(self, comment: Comment) -> None:
        self._comments.append(comment)


class VoiceMessage:
    def __init__(self, speakerId: str, content: str):
        self.speakerId: str = speakerId
        self.content: str = content


class Participant(ABC):
    def __init__(self, id: str):
        self.id: str = id


class Member(Participant):
    def __init__(self, id: str, role: Role = Role.MEMBER):
        super().__init__(id)
        self.role: Role = role

    def sendMessage(self, chatRoom: ChatRoom, content: str, tags: Optional[List[str]] = None) -> None:
        msg = Message(self.id, content, tags)
        chatRoom.postMessage(msg)

    def publishPost(self, forum: Forum, title: str, content: str, tags: Optional[List[str]] = None) -> None:
        post = Post(str(id(self)), self.id, title, content, tags)
        forum.createPost(post)

    def commentPost(self, forum: Forum, postId: str, content: str, tags: Optional[List[str]] = None) -> None:
        comment = Comment(self.id, content, tags)
        forum.addComment(postId, comment)

    def startBroadcast(self, broadcast: Broadcast) -> None:
        broadcast.start(self.id)

    def speak(self, broadcast: Broadcast, content: str) -> None:
        broadcast.speak(VoiceMessage(self.id, content))

    def stopBroadcast(self, broadcast: Broadcast) -> None:
        broadcast.stop(self.id)


class ChatRoom(Observable):
    def __init__(self, output_sink: Optional[List[str]] = None):
        super().__init__()
        self._output_sink: List[str] = output_sink if output_sink is not None else []

    def setOutputSink(self, sink: List[str]) -> None:
        self._output_sink = sink

    def postMessage(self, message: Message) -> None:
        tags_str = ""
        if message.tags:
            tags_str = " " + ", ".join([f"@{t}" for t in message.tags])
        
        # 機器人發言與一般成員發言輸出格式
        if message.authorId == "bot":
            # 判斷是否為題目的選項行（如 A) ..., B) ..., C) ..., D) ...）
            # README 輸出格式中，題號行有 "🤖: 0. 請問..."，但選項行沒有 "🤖: "
            is_option_line = len(message.content) >= 3 and message.content[0] in "ABCD" and message.content[1] == ")"
            if is_option_line:
                self._output_sink.append(f"{message.content}{tags_str}")
            elif "\n" in message.content:
                # 處理多行訊息（例如 Record Replay）
                # README 格式：
                # 🤖: [Record Replay] 大家好，我是小華！
                # 歡迎來到小華脫口秀
                # ...
                # 感謝大家的支持，這就是今晚的小華脫口秀啦！ @3
                lines = message.content.split("\n")
                for i, l in enumerate(lines):
                    if i == 0:
                        self._output_sink.append(f"🤖: {l}")
                    elif i == len(lines) - 1:
                        self._output_sink.append(f"{l}{tags_str}")
                    else:
                        self._output_sink.append(l)
            else:
                self._output_sink.append(f"🤖: {message.content}{tags_str}")
        else:
            self._output_sink.append(f"💬 {message.authorId}: {message.content}{tags_str}")

        # 推播事件通知所有 Observer (Bot)
        self.notify(MessageReceivedEvent(message))


class Forum(Observable):
    def __init__(self, output_sink: Optional[List[str]] = None):
        super().__init__()
        self._posts: List[Post] = []
        self._output_sink: List[str] = output_sink if output_sink is not None else []

    def setOutputSink(self, sink: List[str]) -> None:
        self._output_sink = sink

    def createPost(self, post: Post) -> None:
        self._posts.append(post)
        tags_str = ""
        if post.tags:
            tags_str = " " + ", ".join([f"@{t}" for t in post.tags])
        self._output_sink.append(f"{post.authorId}: 【{post.title}】{post.content}{tags_str}")
        self.notify(PostPublishedEvent(post))

    def addComment(self, postId: str, comment: Comment) -> None:
        tags_str = ""
        if comment.tags:
            tags_str = " " + ", ".join([f"@{t}" for t in comment.tags])
        if comment.authorId == "bot":
            self._output_sink.append(f"🤖 comment in post {postId}: {comment.content}{tags_str}")
        else:
            self._output_sink.append(f"💬 comment in post {postId} by {comment.authorId}: {comment.content}{tags_str}")


class Broadcast(Observable):
    def __init__(self, output_sink: Optional[List[str]] = None):
        super().__init__()
        self.currentSpeakerId: Optional[str] = None
        self._output_sink: List[str] = output_sink if output_sink is not None else []

    def setOutputSink(self, sink: List[str]) -> None:
        self._output_sink = sink

    def isBroadcasting(self) -> bool:
        return self.currentSpeakerId is not None

    def start(self, speakerId: str) -> None:
        self.currentSpeakerId = speakerId
        if speakerId == "bot":
            self._output_sink.append("🤖 go broadcasting...")
        else:
            self._output_sink.append(f"📢 {speakerId} is broadcasting...")
        self.notify(BroadcastStartedEvent(speakerId))

    def speak(self, voiceMessage: VoiceMessage) -> None:
        if voiceMessage.speakerId == "bot":
            self._output_sink.append(f"🤖 speaking: {voiceMessage.content}")
        else:
            self._output_sink.append(f"📢 {voiceMessage.speakerId}: {voiceMessage.content}")
        self.notify(VoiceSpokenEvent(voiceMessage))

    def stop(self, speakerId: str) -> None:
        if self.currentSpeakerId == speakerId:
            self.currentSpeakerId = None
            if speakerId == "bot":
                self._output_sink.append("🤖 stop broadcasting...")
            else:
                self._output_sink.append(f"📢 {speakerId} stop broadcasting")
            self.notify(BroadcastStoppedEvent(speakerId))


class WaterballCommunity(Observable):
    def __init__(self, initialTime: str = "2023-08-07 00:00:00", output_sink: Optional[List[str]] = None):
        super().__init__()
        self.currentTime: str = initialTime
        self.chatRoom: ChatRoom = ChatRoom(output_sink)
        self.forum: Forum = Forum(output_sink)
        self.broadcast: Broadcast = Broadcast(output_sink)
        self._onlineParticipants: List[Participant] = []
        self._membersMap: dict[str, Member] = {}
        self._output_sink: List[str] = output_sink if output_sink is not None else []

    def setOutputSink(self, sink: List[str]) -> None:
        self._output_sink = sink
        self.chatRoom.setOutputSink(sink)
        self.forum.setOutputSink(sink)
        self.broadcast.setOutputSink(sink)

    def login(self, participant: Participant) -> None:
        if participant not in self._onlineParticipants:
            self._onlineParticipants.append(participant)
        if isinstance(participant, Member):
            self._membersMap[participant.id] = participant
        self.notify(OnlineChangedEvent(len(self._onlineParticipants)))

    def logout(self, participantId: str) -> None:
        self._onlineParticipants = [p for p in self._onlineParticipants if p.id != participantId]
        self.notify(OnlineChangedEvent(len(self._onlineParticipants)))

    def elapseTime(self, amount: int, unit: str) -> None:
        self._output_sink.append(f"🕑 {amount} {unit} elapsed...")
        # 計算轉換為秒數傳遞
        seconds = amount
        if unit == "minutes":
            seconds = amount * 60
        elif unit == "hours":
            seconds = amount * 3600
        self.notify(TimeElapsedEvent(seconds))

    def getOnlineParticipants(self) -> List[Participant]:
        return list(self._onlineParticipants)

    def getOnlineCount(self) -> int:
        return len(self._onlineParticipants)

    def getMember(self, memberId: str) -> Optional[Member]:
        return self._membersMap.get(memberId)


class RecordingSession:
    def __init__(self, recorderId: str):
        self.recorderId: str = recorderId
        self._voices: List[VoiceMessage] = []

    def addVoice(self, message: VoiceMessage) -> None:
        self._voices.append(message)

    def generateReplay(self) -> str:
        content = "\n".join([v.content for v in self._voices])
        return f"[Record Replay] {content}"


class Question:
    def __init__(self, number: int, description: str, options: List[str], correctAnswer: str):
        self.number: int = number
        self.description: str = description
        self.options: List[str] = options
        self.correctAnswer: str = correctAnswer

    def isCorrect(self, answer: str) -> bool:
        return answer.strip().upper() == self.correctAnswer.strip().upper()


class KnowledgeKingGame:
    def __init__(self):
        self.currentQuestionIndex: int = 0
        self.scores: dict[str, int] = {}
        self.questions: List[Question] = [
            Question(
                0,
                "0. 請問哪個 SQL 語句用於選擇所有的行？\nA) SELECT *\nB) SELECT ALL\nC) SELECT ROWS\nD) SELECT DATA",
                ["A", "B", "C", "D"],
                "A",
            ),
            Question(
                1,
                "1. 請問哪個 CSS 屬性可用於設置文字的顏色？\nA) text-align\nB) font-size\nC) color\nD) padding",
                ["A", "B", "C", "D"],
                "C",
            ),
            Question(
                2,
                "2. 請問在計算機科學中，「XML」代表什麼？\nA) Extensible Markup Language\nB) Extensible Modeling Language\nC) Extended Markup Language\nD) Extended Modeling Language",
                ["A", "B", "C", "D"],
                "A",
            ),
        ]

    def getCurrentQuestion(self) -> Optional[Question]:
        if self.currentQuestionIndex < len(self.questions):
            return self.questions[self.currentQuestionIndex]
        return None

    def submitAnswer(self, memberId: str, answer: str) -> bool:
        q = self.getCurrentQuestion()
        if q is not None and q.isCorrect(answer):
            self.scores[memberId] = self.scores.get(memberId, 0) + 1
            self.currentQuestionIndex += 1
            return True
        return False

    def isFinished(self) -> bool:
        return self.currentQuestionIndex >= len(self.questions)

    def getWinner(self) -> str:
        if not self.scores:
            return "Tie!"
        max_score = max(self.scores.values())
        winners = [uid for uid, s in self.scores.items() if s == max_score]
        if len(winners) > 1:
            return "Tie!"
        return f"The winner is {winners[0]}"
