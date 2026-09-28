from ..domain.knowledge_king import KnowledgeKingGame
from ..domain.recording import RecordingSession
from ..fsm.core import Action, State


class DefaultConversationState(State):
    def __init__(self, enter: Action, exit: Action, replyCycleIndex: int):
        super().__init__(enter, exit)
        self.replyCycleIndex = replyCycleIndex

    def getNextReplyMessage(self) -> str:
        raise NotImplementedError


class InteractingState(State):
    def __init__(self, enter: Action, exit: Action, replyCycleIndex: int):
        super().__init__(enter, exit)
        self.replyCycleIndex = replyCycleIndex

    def getNextReplyMessage(self) -> str:
        raise NotImplementedError


class WaitingState(State):
    pass


class RecordingState(State):
    def __init__(self, enter: Action, exit: Action, session: RecordingSession):
        super().__init__(enter, exit)
        self.session = session


class QuestioningState(State):
    def __init__(self, enter: Action, exit: Action, game: KnowledgeKingGame):
        super().__init__(enter, exit)
        self.game = game


class ThanksForJoiningState(State):
    def __init__(self, enter: Action, exit: Action, game: KnowledgeKingGame):
        super().__init__(enter, exit)
        self.game = game
