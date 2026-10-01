from typing import Optional

from datetime import datetime as DateTime

from ..activities.knowledge_king import KnowledgeKingGame
from ..activities.recording import RecordingSession
from ..fsm.core import Action, Event, Guard, State
from .triggers.triggers import MessageFromMemberTrigger, MentionsBotTrigger, PostCreatedTrigger, VoiceSpokenTrigger


class DefaultConversationState(State):
    def __init__(self, enter: Action, exit: Action, messages: list[str], replyCycleIndex: int = 0):
        super().__init__(enter, exit)
        self.messages = messages  # 圖上沒畫，但 getNextReplyMessage 輪播缺一不可的訊息清單
        self.replyCycleIndex = replyCycleIndex
        self.messageAction: Optional[Action] = None
        self.postAction: Optional[Action] = None

    def getNextReplyMessage(self) -> str:
        message = self.messages[self.replyCycleIndex % len(self.messages)]
        self.replyCycleIndex += 1
        return message

    def fire(self, event: Event) -> bool:
        if self.messageAction is not None and MessageFromMemberTrigger().isTriggeredBy(event):
            self.messageAction.execute(event)
        if self.postAction is not None and PostCreatedTrigger().isTriggeredBy(event):
            self.postAction.execute(event)
        return False  # 原地反應不阻止外層 FSM 處理同一事件的轉移


class InteractingState(State):
    def __init__(self, enter: Action, exit: Action, messages: list[str], replyCycleIndex: int = 0):
        super().__init__(enter, exit)
        self.messages = messages
        self.replyCycleIndex = replyCycleIndex
        self.messageAction: Optional[Action] = None
        self.postAction: Optional[Action] = None

    def getNextReplyMessage(self) -> str:
        message = self.messages[self.replyCycleIndex % len(self.messages)]
        self.replyCycleIndex += 1
        return message

    def fire(self, event: Event) -> bool:
        if self.messageAction is not None and MessageFromMemberTrigger().isTriggeredBy(event):
            self.messageAction.execute(event)
        if self.postAction is not None and PostCreatedTrigger().isTriggeredBy(event):
            self.postAction.execute(event)
        return False


class WaitingState(State):
    pass


class RecordingState(State):
    def __init__(self, enter: Action, exit: Action, session: Optional[RecordingSession] = None):
        super().__init__(enter, exit)
        self.session = session  # 0..1：CreateRecordingSessionAction 觸發前是 None
        self.voiceAction: Optional[Action] = None

    def fire(self, event: Event) -> bool:
        if self.voiceAction is not None and VoiceSpokenTrigger().isTriggeredBy(event):
            self.voiceAction.execute(event)
        return False


class QuestioningState(State):
    def __init__(self, enter: Action, exit: Action, game: Optional[KnowledgeKingGame] = None):
        super().__init__(enter, exit)
        self.game = game  # Bot 建構當下還沒有遊戲，CreateKnowledgeKingGameAction 觸發後才會賦值
        self.answerCorrectGuard: Optional[Guard] = None
        self.lastQuestionGuard: Optional[Guard] = None
        self.correctAnswerAction: Optional[Action] = None

    def fire(self, event: Event) -> bool:
        if (
            self.correctAnswerAction is not None
            and self.answerCorrectGuard is not None
            and self.lastQuestionGuard is not None
            and MentionsBotTrigger().isTriggeredBy(event)
            and self.answerCorrectGuard.isSatisfied(event)
            and not self.lastQuestionGuard.isSatisfied(event)
        ):
            self.correctAnswerAction.execute(event)
        return False


class ThanksForJoiningState(State):
    def __init__(
        self,
        enter: Action,
        exit: Action,
        game: Optional[KnowledgeKingGame] = None,
        enteredAt: Optional[DateTime] = None,
    ):
        super().__init__(enter, exit)
        self.game = game
        self.enteredAt = enteredAt  # 進場時間戳記，給 20 秒後回 Normal 的 DurationElapsedGuard 用
