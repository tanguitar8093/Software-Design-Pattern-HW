from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from ..domain.activities import KnowledgeKingGame, RecordingSession
from ..fsm import (
    Action,
    AtomicState,
    CompositeState,
    FiniteStateMachine,
    Guard,
    State,
    TransitionContext,
    Trigger,
)

if TYPE_CHECKING:
    from .bot import Bot


# ================================================================
# 具體 Guard 策略 (Strategy Pattern)
# ================================================================
class OnlineCountGuard(Guard):
    def __init__(self, threshold: int, greaterOrEqual: bool = True):
        self.threshold: int = threshold
        self.greaterOrEqual: bool = greaterOrEqual

    def isSatisfied(self, context: TransitionContext) -> bool:
        bot: Optional[Bot] = context.target
        if bot is not None and bot.getCommunity() is not None:
            count = bot.getCommunity().getOnlineCount()
            if self.greaterOrEqual:
                return count >= self.threshold
            return count < self.threshold
        return False


class IsBroadcastingGuard(Guard):
    def __init__(self, expected: bool = True):
        self.expected: bool = expected

    def isSatisfied(self, context: TransitionContext) -> bool:
        bot: Optional[Bot] = context.target
        if bot is not None and bot.getCommunity() is not None:
            return bot.getCommunity().broadcast.isBroadcasting() == self.expected
        return False


class IsRecorderGuard(Guard):
    def __init__(self, recordState: RecordState):
        self.recordState: RecordState = recordState

    def isSatisfied(self, context: TransitionContext) -> bool:
        sender_id = context.trigger.payload.get("memberId")
        if self.recordState.getSession() is not None:
            return sender_id == self.recordState.getSession().recorderId
        return False


# ================================================================
# 具體 Action 策略 (Strategy Pattern)
# ================================================================
class ResetReplyCycleAction(Action):
    def execute(self, context: TransitionContext) -> None:
        bot: Optional[Bot] = context.target
        if bot is not None:
            bot.resetReplyCycle()


class FlushReplayAction(Action):
    def __init__(self, recordState: RecordState):
        self.recordState: RecordState = recordState

    def execute(self, context: TransitionContext) -> None:
        bot: Optional[Bot] = context.target
        session = self.recordState.getSession()
        if bot is not None and session is not None:
            replay_text = session.generateReplay()
            bot.replyChatMessage(replay_text, [session.recorderId])
            session.clear()


class ResetGameAction(Action):
    def __init__(self, knowledgeKingState: KnowledgeKingState):
        self.knowledgeKingState: KnowledgeKingState = knowledgeKingState

    def execute(self, context: TransitionContext) -> None:
        bot: Optional[Bot] = context.target
        game = context.trigger.payload.get("game")
        if bot is not None and game is not None:
            game.is_play_again = True
            self.knowledgeKingState.game = game
            bot.replyChatMessage("KnowledgeKing is gonna start again!")
            q = game.getCurrentQuestion()
            if q is not None:
                for line in q.description.split("\n"):
                    bot.replyChatMessage(line)


class SelectRecordSubStateAction(Action):
    def __init__(self, recordState: RecordState, waitingState: State, recordingState: State):
        self.recordState: RecordState = recordState
        self.waitingState: State = waitingState
        self.recordingState: State = recordingState

    def execute(self, context: TransitionContext) -> None:
        bot: Optional[Bot] = context.target
        if bot is not None and bot.getCommunity() is not None and bot.getCommunity().broadcast.isBroadcasting():
            self.recordState.getInnerFsm().setCurrentState(self.recordingState)
        else:
            self.recordState.getInnerFsm().setCurrentState(self.waitingState)


class StopRecordAction(Action):
    def __init__(self, recordState: RecordState, recordingState: State):
        self.recordState: RecordState = recordState
        self.recordingState: State = recordingState

    def execute(self, context: TransitionContext) -> None:
        bot: Optional[Bot] = context.target
        if self.recordState.getInnerFsm().getCurrentState() == self.recordingState:
            session = self.recordState.getSession()
            if bot is not None and session is not None and session.hasRecordedVoice():
                replay_text = session.generateReplay()
                bot.replyChatMessage(replay_text, [session.recorderId])


# ================================================================
# 具體 Composite 主狀態 (Composite Pattern)
# ================================================================
class NormalState(CompositeState):
    def __init__(self, innerFsm: FiniteStateMachine):
        super().__init__("NORMAL", innerFsm)


class RecordState(CompositeState):
    def __init__(self, innerFsm: FiniteStateMachine):
        super().__init__("RECORD", innerFsm)
        self.session: Optional[RecordingSession] = None

    def onEnter(self, context: TransitionContext) -> None:
        session = context.trigger.payload.get("session")
        if session is not None:
            self.session = session
        super().onEnter(context)

    def getSession(self) -> Optional[RecordingSession]:
        return self.session


class KnowledgeKingState(CompositeState):
    def __init__(self, innerFsm: FiniteStateMachine):
        super().__init__("KNOWLEDGE_KING", innerFsm)
        self.game: Optional[KnowledgeKingGame] = None

    def onEnter(self, context: TransitionContext) -> None:
        game = context.trigger.payload.get("game")
        if game is not None:
            self.game = game
        super().onEnter(context)

    def getGame(self) -> Optional[KnowledgeKingGame]:
        return self.game


# ================================================================
# 具體 Leaf 葉狀態 (Composite Leaf)
# ================================================================
class DefaultConversationState(AtomicState):
    def __init__(self):
        super().__init__("DEFAULT_CONVERSATION")

    def onEnter(self, context: TransitionContext) -> None:
        bot: Optional[Bot] = context.target
        if bot is not None:
            bot.resetReplyCycle()

    def handle(self, context: TransitionContext) -> bool:
        bot: Optional[Bot] = context.target
        trigger = context.trigger
        if bot is None:
            return False

        if trigger.name == "message":
            msg = trigger.payload.get("message")
            if msg is not None:
                reply = bot.getNextReplyMessage()
                bot.replyChatMessage(reply, [msg.authorId])
                return True
        elif trigger.name == "post":
            post = trigger.payload.get("post")
            if post is not None:
                bot.commentPost(post.id, "Nice post", [post.authorId])
                return True
        return False


class InteractingState(AtomicState):
    def __init__(self):
        super().__init__("INTERACTING")

    def onEnter(self, context: TransitionContext) -> None:
        bot: Optional[Bot] = context.target
        if bot is not None:
            bot.resetReplyCycle()

    def handle(self, context: TransitionContext) -> bool:
        bot: Optional[Bot] = context.target
        trigger = context.trigger
        if bot is None:
            return False

        if trigger.name == "message":
            msg = trigger.payload.get("message")
            if msg is not None:
                reply = bot.getNextInteractingMessage()
                bot.replyChatMessage(reply, [msg.authorId])
                return True
        elif trigger.name == "post":
            post = trigger.payload.get("post")
            if post is not None and bot.getCommunity() is not None:
                participants = bot.getCommunity().getOnlineParticipants()
                tags = ["bot"] + [p.id for p in participants if p.id != "bot"]
                bot.commentPost(post.id, "How do you guys think about it?", tags)
                return True
        return False


class WaitingState(AtomicState):
    def __init__(self):
        super().__init__("WAITING")

    def handle(self, context: TransitionContext) -> bool:
        if context.trigger.name == "message":
            return True
        return False


class RecordingState(AtomicState):
    def __init__(self):
        super().__init__("RECORDING")

    def handle(self, context: TransitionContext) -> bool:
        bot: Optional[Bot] = context.target
        trigger = context.trigger
        if trigger.name == "message":
            return True
        if trigger.name == "voice":
            voiceMsg = trigger.payload.get("voiceMessage")
            if bot is not None and bot._rootFsm is not None:
                curr = bot._rootFsm.getCurrentState()
                if isinstance(curr, RecordState) and curr.getSession() is not None and voiceMsg is not None:
                    curr.getSession().addVoice(voiceMsg)
                    return True
        return False


class QuestioningState(AtomicState):
    def __init__(self):
        super().__init__("QUESTIONING")
        self.elapsedSeconds: int = 0

    def onEnter(self, context: TransitionContext) -> None:
        self.elapsedSeconds = 0
        bot: Optional[Bot] = context.target
        if bot is not None and bot._rootFsm is not None:
            curr = bot._rootFsm.getCurrentState()
            if isinstance(curr, KnowledgeKingState) and curr.getGame() is not None:
                game = curr.getGame()
                if game.currentQuestionIndex == 0 and not getattr(game, "is_play_again", False):
                    bot.replyChatMessage("KnowledgeKing is started!")
                    q = game.getCurrentQuestion()
                    if q is not None:
                        for line in q.description.split("\n"):
                            bot.replyChatMessage(line)

    def handle(self, context: TransitionContext) -> bool:
        bot: Optional[Bot] = context.target
        trigger = context.trigger
        if bot is None or bot._rootFsm is None:
            return False

        curr = bot._rootFsm.getCurrentState()
        if not isinstance(curr, KnowledgeKingState) or curr.getGame() is None:
            return False

        game = curr.getGame()
        if trigger.name == "message":
            msg = trigger.payload.get("message")
            if msg is not None:
                if "bot" in msg.tags:
                    ans = msg.content.strip()
                    correct = game.submitAnswer(msg.authorId, ans)
                    if correct:
                        bot.replyChatMessage("Congrats! you got the answer!", [msg.authorId])
                        if not game.isFinished():
                            next_q = game.getCurrentQuestion()
                            if next_q is not None:
                                for line in next_q.description.split("\n"):
                                    bot.replyChatMessage(line)
                        else:
                            curr.getInnerFsm().fire(Trigger("all_answered"))
                    return True
                else:
                    return True

        if trigger.name == "time_elapsed":
            seconds = trigger.payload.get("seconds", 0)
            self.elapsedSeconds += seconds
            if self.elapsedSeconds >= 3600:
                curr.getInnerFsm().fire(Trigger("timeout"))
                return True

        return False


class ThanksForJoiningState(AtomicState):
    def __init__(self):
        super().__init__("THANKS_FOR_JOINING")
        self.elapsedSeconds: int = 0

    def onEnter(self, context: TransitionContext) -> None:
        self.elapsedSeconds = 0
        bot: Optional[Bot] = context.target
        if bot is not None and bot._rootFsm is not None and bot.getCommunity() is not None:
            curr = bot._rootFsm.getCurrentState()
            if isinstance(curr, KnowledgeKingState) and curr.getGame() is not None:
                winner_msg = curr.getGame().getWinner()
                if not bot.getCommunity().broadcast.isBroadcasting():
                    bot.broadcastVoice(winner_msg)
                else:
                    bot.replyChatMessage(winner_msg)

    def handle(self, context: TransitionContext) -> bool:
        bot: Optional[Bot] = context.target
        trigger = context.trigger
        if trigger.name == "time_elapsed":
            secs = trigger.payload.get("seconds", 0)
            self.elapsedSeconds += secs
            if self.elapsedSeconds >= 20:
                if bot is not None and bot._rootFsm is not None:
                    bot._rootFsm.fire(Trigger("thanks_timeout"))
                return True
        if trigger.name == "message":
            return True
        return False
