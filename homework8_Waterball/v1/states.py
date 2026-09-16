from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from homework8_Waterball.v1.community import KnowledgeKingGame, RecordingSession
from homework8_Waterball.v1.fsm import (
    Action,
    AtomicState,
    CompositeState,
    FiniteStateMachine,
    Guard,
    TransitionContext,
    Trigger,
)

if TYPE_CHECKING:
    from homework8_Waterball.v1.bot import Bot


# ================================================================
# 具體 Guard 策略 (Strategy Pattern)
# ================================================================
class OnlineCountGuard(Guard):
    def __init__(self, threshold: int, greater_or_equal: bool = True):
        self.threshold: int = threshold
        self.greater_or_equal: bool = greater_or_equal

    def isSatisfied(self, context: TransitionContext) -> bool:
        bot: Optional[Bot] = context.target
        if bot is not None and bot.getCommunity() is not None:
            count = bot.getCommunity().getOnlineCount()
            if self.greater_or_equal:
                return count >= self.threshold
            return count < self.threshold
        return False


class IsBroadcastingGuard(Guard):
    def __init__(self, is_broadcasting: bool = True):
        self._expected: bool = is_broadcasting

    def isSatisfied(self, context: TransitionContext) -> bool:
        bot: Optional[Bot] = context.target
        if bot is not None and bot.getCommunity() is not None:
            return bot.getCommunity().broadcast.isBroadcasting() == self._expected
        return False


# ================================================================
# 具體 Action 策略 (Strategy Pattern)
# ================================================================
class ResetReplyCycleAction(Action):
    def execute(self, context: TransitionContext) -> None:
        bot: Optional[Bot] = context.target
        if bot is not None:
            bot.resetReplyCycle()


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
                # 標記順序：bot 排最前，接著依成員登入順序排列
                participants = bot.getCommunity().getOnlineParticipants()
                tags = ["bot"] + [p.id for p in participants if p.id != "bot"]
                bot.commentPost(post.id, "How do you guys think about it?", tags)
                return True
        return False


class WaitingState(AtomicState):
    def __init__(self):
        super().__init__("WAITING")

    def handle(self, context: TransitionContext) -> bool:
        # 在 Waiting 狀態下，聊天室訊息不觸發輪播回覆
        if context.trigger.name == "message":
            return True
        return False


class RecordingState(AtomicState):
    def __init__(self):
        super().__init__("RECORDING")

    def handle(self, context: TransitionContext) -> bool:
        bot: Optional[Bot] = context.target
        trigger = context.trigger
        # 1. 聊天室訊息在錄音中不回覆
        if trigger.name == "message":
            return True
        # 2. 語音訊息逐筆記錄
        if trigger.name == "voice":
            voiceMsg = trigger.payload.get("voiceMessage")
            # 找到外層 RecordState 取得 session
            if bot is not None and bot._rootFsm is not None:
                curr = bot._rootFsm.getCurrentState()
                if isinstance(curr, RecordState) and curr.session is not None and voiceMsg is not None:
                    curr.session.addVoice(voiceMsg)
                    return True
        return False


class QuestioningState(AtomicState):
    def __init__(self):
        super().__init__("QUESTIONING")

    def onEnter(self, context: TransitionContext) -> None:
        bot: Optional[Bot] = context.target
        if bot is not None and bot._rootFsm is not None:
            curr = bot._rootFsm.getCurrentState()
            if isinstance(curr, KnowledgeKingState) and curr.game is not None:
                # 只有首次進入且非 play again 重開時印出起始與第 0 題
                if curr.game.currentQuestionIndex == 0 and not getattr(curr.game, "is_play_again", False):
                    bot.replyChatMessage("KnowledgeKing is started!")
                    q = curr.game.getCurrentQuestion()
                    if q is not None:
                        for line in q.description.split("\n"):
                            bot.replyChatMessage(line)

    def handle(self, context: TransitionContext) -> bool:
        bot: Optional[Bot] = context.target
        trigger = context.trigger
        if bot is None or bot._rootFsm is None:
            return False

        curr = bot._rootFsm.getCurrentState()
        if not isinstance(curr, KnowledgeKingState) or curr.game is None:
            return False

        # 1. 處理答題訊息
        if trigger.name == "message":
            msg = trigger.payload.get("message")
            if msg is not None:
                # 必須 tag bot 才算答題，未 tag 忽略
                if "bot" in msg.tags:
                    ans = msg.content.strip()
                    correct = curr.game.submitAnswer(msg.authorId, ans)
                    if correct:
                        bot.replyChatMessage(f"Congrats! you got the answer!", [msg.authorId])
                        if not curr.game.isFinished():
                            next_q = curr.game.getCurrentQuestion()
                            if next_q is not None:
                                for line in next_q.description.split("\n"):
                                    bot.replyChatMessage(line)
                        else:
                            # 題目全答完，切換至 ThanksForJoiningState
                            curr.getInnerFsm().fire(Trigger("all_answered"))
                    # 答錯或答對皆被知識王消化，不進行聊天室常態輪播
                    return True
                else:
                    # 沒 tag bot，靜默忽略
                    return True

        # 2. 超時處理（1 小時 = 3600 秒）
        if trigger.name == "time_elapsed":
            seconds = trigger.payload.get("seconds", 0)
            if seconds >= 3600:
                curr.getInnerFsm().fire(Trigger("timeout"))
                return True

        return False


class ThanksForJoiningState(AtomicState):
    def __init__(self):
        super().__init__("THANKS_FOR_JOINING")
        self.elapsed_after_thanks: int = 0

    def onEnter(self, context: TransitionContext) -> None:
        self.elapsed_after_thanks = 0
        bot: Optional[Bot] = context.target
        if bot is not None and bot._rootFsm is not None and bot.getCommunity() is not None:
            curr = bot._rootFsm.getCurrentState()
            if isinstance(curr, KnowledgeKingState) and curr.game is not None:
                winner_msg = curr.game.getWinner()
                # 若無人廣播，語音廣播；若有人正在廣播，聊天訊息公布
                if not bot.getCommunity().broadcast.isBroadcasting():
                    bot.broadcastVoice(winner_msg)
                else:
                    bot.replyChatMessage(winner_msg)

    def handle(self, context: TransitionContext) -> bool:
        bot: Optional[Bot] = context.target
        trigger = context.trigger
        if trigger.name == "time_elapsed":
            secs = trigger.payload.get("seconds", 0)
            self.elapsed_after_thanks += secs
            if self.elapsed_after_thanks >= 20:
                # 滿 20 秒，退回 Normal 狀態
                if bot is not None and bot._rootFsm is not None:
                    bot._rootFsm.fire(Trigger("thanks_timeout"))
                return True
        if trigger.name == "message":
            return True
        return False


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
        # 自 Trigger payload 取得 session
        session = context.trigger.payload.get("session")
        if session is not None:
            self.session = session
        super().onEnter(context)


class KnowledgeKingState(CompositeState):
    def __init__(self, innerFsm: FiniteStateMachine):
        super().__init__("KNOWLEDGE_KING", innerFsm)
        self.game: Optional[KnowledgeKingGame] = None

    def onEnter(self, context: TransitionContext) -> None:
        game = context.trigger.payload.get("game")
        if game is not None:
            self.game = game
        super().onEnter(context)
