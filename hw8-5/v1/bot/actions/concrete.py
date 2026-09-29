from typing import Callable

from ...activities.knowledge_king import KnowledgeKingGame, Question
from ...activities.recording import RecordingSession
from ...community.channels import VoiceMessage
from ...events.domain_events import DomainEvent, PostCreatedEvent, VoiceSpokenEvent
from ...fsm.core import Action, Event
from ..bot import Bot
from ..states import DefaultConversationState, InteractingState, QuestioningState, RecordingState, ThanksForJoiningState


class ResetReplyCycleAction(Action):
    """每次重新進入 Default/Interacting 都要從第一則輪播訊息開始（README 明定的行為）。"""

    def __init__(self, state: "DefaultConversationState | InteractingState"):
        self.state = state

    def execute(self, event: Event) -> None:
        self.state.replyCycleIndex = 0


class CommentPostAction(Action):
    def __init__(self, bot: Bot, text: str, tagsProvider: Callable[[Event], list[str]]):
        self.bot = bot
        self.text = text
        self.tagsProvider = tagsProvider

    def execute(self, event: Event) -> None:
        if not isinstance(event, PostCreatedEvent):
            return
        self.bot.commentPost(event.post.id, self.text, self.tagsProvider(event))


class FlushRecordReplayAction(Action):
    def __init__(self, bot: Bot, recordingState: RecordingState):
        self.bot = bot
        self.recordingState = recordingState

    def execute(self, event: Event) -> None:
        if self.recordingState.session is None:
            return
        self.bot.replyChatMessage(self.recordingState.session.generateReplay(), [self.bot.recorderId])
        self.recordingState.session = None


class DeductQuotaAction(Action):
    def __init__(self, bot: Bot, cost: int):
        self.bot = bot
        self.cost = cost

    def execute(self, event: Event) -> None:
        self.bot.quota -= self.cost


class SetRecorderAction(Action):
    """N: 誰下 record 指令，誰就是接下來這整段錄音狀態期間的錄音者。"""

    def __init__(self, bot: Bot):
        self.bot = bot

    def execute(self, event: Event) -> None:
        self.bot.recorderId = event.getSourceId() if isinstance(event, DomainEvent) else None


class ClearRecorderAction(Action):
    def __init__(self, bot: Bot):
        self.bot = bot

    def execute(self, event: Event) -> None:
        self.bot.recorderId = None


class CreateRecordingSessionAction(Action):
    """每次進入錄音中狀態都重開一個乾淨的 session，錄音者身分讀 Bot.recorderId（不是這次廣播的講者）。"""

    def __init__(self, recordingState: RecordingState, bot: Bot):
        self.recordingState = recordingState
        self.bot = bot

    def execute(self, event: Event) -> None:
        self.recordingState.session = RecordingSession(self.bot.recorderId)  # type: ignore[arg-type]


class AddVoiceToRecordingSessionAction(Action):
    def __init__(self, recordingState: RecordingState):
        self.recordingState = recordingState

    def execute(self, event: Event) -> None:
        if not isinstance(event, VoiceSpokenEvent) or self.recordingState.session is None:
            return
        self.recordingState.session.addVoice(VoiceMessage(event.voiceMessage.speakerId, event.voiceMessage.content))


class CreateKnowledgeKingGameAction(Action):
    def __init__(self, questioningState: QuestioningState, bot: Bot, questions: list[Question]):
        self.questioningState = questioningState
        self.bot = bot
        self.questions = questions

    def execute(self, event: Event) -> None:
        self.questioningState.game = KnowledgeKingGame(list(self.questions), self.bot.getCurrentTime())


class CarryGameToThanksForJoiningAction(Action):
    def __init__(self, questioningState: QuestioningState, thanksForJoiningState: ThanksForJoiningState):
        self.questioningState = questioningState
        self.thanksForJoiningState = thanksForJoiningState

    def execute(self, event: Event) -> None:
        self.thanksForJoiningState.game = self.questioningState.game


class AnnounceGameResultAction(Action):
    """進場行為：沒人廣播就用語音公布結果，否則改用聊天訊息；同時記錄進場時間給 20 秒後回 Normal 的 Guard 用。"""

    def __init__(self, bot: Bot, thanksForJoiningState: ThanksForJoiningState):
        self.bot = bot
        self.thanksForJoiningState = thanksForJoiningState

    def execute(self, event: Event) -> None:
        game = self.thanksForJoiningState.game
        assert game is not None
        winner = game.getWinner()
        text = "Tie!" if winner == "Tie" else f"The winner is {winner}"
        if self.bot.isBroadcasting():
            self.bot.replyChatMessage(text, [])
        else:
            self.bot.broadcastVoice(text)
        self.thanksForJoiningState.enteredAt = self.bot.getCurrentTime()


class SendChatMessageAction(Action):
    def __init__(
        self,
        bot: Bot,
        contentProvider: Callable[[Event], str],
        tagsProvider: Callable[[Event], list[str]] = lambda event: [],
    ):
        self.bot = bot
        self.contentProvider = contentProvider
        self.tagsProvider = tagsProvider

    def execute(self, event: Event) -> None:
        self.bot.replyChatMessage(self.contentProvider(event), self.tagsProvider(event))
