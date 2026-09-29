from typing import Optional

from ..activities.knowledge_king import KnowledgeKingGame
from ..activities.recording import RecordingSession
from ..fsm.core import Action, State


class DefaultConversationState(State):
    def __init__(self, enter: Action, exit: Action, messages: list[str], replyCycleIndex: int = 0):
        super().__init__(enter, exit)
        self.messages = messages  # 圖上沒畫，但 getNextReplyMessage 輪播缺一不可的訊息清單
        self.replyCycleIndex = replyCycleIndex

    def getNextReplyMessage(self) -> str:
        message = self.messages[self.replyCycleIndex % len(self.messages)]
        self.replyCycleIndex += 1
        return message


class InteractingState(State):
    def __init__(self, enter: Action, exit: Action, messages: list[str], replyCycleIndex: int = 0):
        super().__init__(enter, exit)
        self.messages = messages
        self.replyCycleIndex = replyCycleIndex

    def getNextReplyMessage(self) -> str:
        message = self.messages[self.replyCycleIndex % len(self.messages)]
        self.replyCycleIndex += 1
        return message


class WaitingState(State):
    pass


class RecordingState(State):
    def __init__(self, enter: Action, exit: Action, session: Optional[RecordingSession] = None):
        super().__init__(enter, exit)
        self.session = session  # 0..1：CreateRecordingSessionAction 觸發前是 None


class QuestioningState(State):
    def __init__(self, enter: Action, exit: Action, game: Optional[KnowledgeKingGame] = None):
        super().__init__(enter, exit)
        self.game = game  # Bot 建構當下還沒有遊戲，CreateKnowledgeKingGameAction 觸發後才會賦值


class ThanksForJoiningState(State):
    def __init__(self, enter: Action, exit: Action, game: Optional[KnowledgeKingGame] = None):
        super().__init__(enter, exit)
        self.game = game
