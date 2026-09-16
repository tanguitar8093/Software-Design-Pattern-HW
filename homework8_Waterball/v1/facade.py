from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Optional
from homework8_Waterball.v1.bot import Bot
from homework8_Waterball.v1.commands import (
    BotCommand,
    KingCommand,
    KingStopCommand,
    PlayAgainCommand,
    RecordCommand,
    StopRecordingCommand,
)
from homework8_Waterball.v1.community import WaterballCommunity
from homework8_Waterball.v1.fsm import (
    Action,
    CompositeState,
    FiniteStateMachine,
    Guard,
    State,
    Transition,
    TransitionContext,
)
from homework8_Waterball.v1.states import (
    DefaultConversationState,
    InteractingState,
    IsBroadcastingGuard,
    KnowledgeKingState,
    NormalState,
    OnlineCountGuard,
    QuestioningState,
    RecordingState,
    RecordState,
    ResetReplyCycleAction,
    ThanksForJoiningState,
    WaitingState,
)


class BotFacade:
    """
    社群機器人門面 (Facade Pattern):
    封裝底層 FSM 與指令子系統的組裝細節，對應用層提供流暢 API。
    """
    def __init__(self, quota: int = 10):
        self._bot: Bot = Bot(quota=quota)
        self._states: Dict[str, State] = {}

    @classmethod
    def create(cls, quota: int = 10) -> BotFacade:
        return cls(quota=quota)

    def buildDefaultBot(self, community: WaterballCommunity) -> Bot:
        """
        按照 OOD v4 架構組裝標準 Waterball 機器人
        """
        self._bot.setCommunity(community)

        # -------------------------------------------------------------
        # 1. 組裝 NormalState 內部子狀態機 (DefaultConversation <-> Interacting)
        # -------------------------------------------------------------
        default_conv = DefaultConversationState()
        interacting = InteractingState()
        normal_fsm = FiniteStateMachine(initialState=default_conv)
        normal_fsm.setTarget(self._bot)

        # 登入達 10 人 (含 bot) 切換至 Interacting
        normal_fsm.addTransition(
            Transition(
                fromState=default_conv,
                toState=interacting,
                triggerName="online_changed",
                guard=OnlineCountGuard(threshold=10, greater_or_equal=True),
            )
        )
        # 登出小於 10 人切換回 DefaultConversation (重置計數)
        normal_fsm.addTransition(
            Transition(
                fromState=interacting,
                toState=default_conv,
                triggerName="online_changed",
                guard=OnlineCountGuard(threshold=10, greater_or_equal=False),
                action=ResetReplyCycleAction(),
            )
        )
        normal_state = NormalState(innerFsm=normal_fsm)

        # -------------------------------------------------------------
        # 2. 組裝 RecordState 內部子狀態機 (Waiting <-> Recording)
        # -------------------------------------------------------------
        waiting = WaitingState()
        recording = RecordingState()
        record_fsm = FiniteStateMachine(initialState=waiting)
        record_fsm.setTarget(self._bot)

        # 講者開始廣播 -> 進入 Recording
        record_fsm.addTransition(
            Transition(
                fromState=waiting,
                toState=recording,
                triggerName="broadcast_started",
            )
        )

        # 講者停止廣播 -> 輸出 Replay 並返回 Waiting
        class FlushReplayAction(Action):
            def __init__(self, bot: Bot, rec_state: RecordState):
                self.bot: Bot = bot
                self.rec_state: RecordState = rec_state

            def execute(self, context: TransitionContext) -> None:
                if self.rec_state.session is not None:
                    replay_text = self.rec_state.session.generateReplay()
                    self.bot.replyChatMessage(replay_text, [self.rec_state.session.recorderId])
                    # 清空 session 內聲音準備下一次講者
                    self.rec_state.session._voices.clear()

        # 預先建立 RecordState 容器以便 FlushReplayAction 引用
        record_state = RecordState(innerFsm=record_fsm)

        record_fsm.addTransition(
            Transition(
                fromState=recording,
                toState=waiting,
                triggerName="broadcast_stopped",
                action=FlushReplayAction(self._bot, record_state),
            )
        )

        # -------------------------------------------------------------
        # 3. 組裝 KnowledgeKingState 內部子狀態機 (Questioning -> ThanksForJoining)
        # -------------------------------------------------------------
        questioning = QuestioningState()
        thanks = ThanksForJoiningState()
        king_fsm = FiniteStateMachine(initialState=questioning)
        king_fsm.setTarget(self._bot)

        # 題目全答完或 1 小時超時 -> 進入 ThanksForJoining
        king_fsm.addTransition(
            Transition(
                fromState=questioning,
                toState=thanks,
                triggerName="all_answered",
            )
        )
        king_fsm.addTransition(
            Transition(
                fromState=questioning,
                toState=thanks,
                triggerName="timeout",
            )
        )

        # play again 指令 -> 重新進入 Questioning
        class ResetGameAction(Action):
            def __init__(self, bot: Bot, king_state: KnowledgeKingState):
                self.bot: Bot = bot
                self.king_state: KnowledgeKingState = king_state

            def execute(self, context: TransitionContext) -> None:
                game = context.trigger.payload.get("game")
                if game is not None:
                    # 標記 is_play_again 避免 QuestioningState.onEnter 重複發送 KnowledgeKing is started!
                    game.is_play_again = True
                    self.king_state.game = game
                    self.bot.replyChatMessage("KnowledgeKing is gonna start again!")
                    q = self.king_state.game.getCurrentQuestion()
                    if q is not None:
                        for line in q.description.split("\n"):
                            self.bot.replyChatMessage(line)

        king_state = KnowledgeKingState(innerFsm=king_fsm)

        king_fsm.addTransition(
            Transition(
                fromState=questioning,
                toState=questioning,
                triggerName="play again",
                action=ResetGameAction(self._bot, king_state),
            )
        )
        king_fsm.addTransition(
            Transition(
                fromState=thanks,
                toState=questioning,
                triggerName="play again",
                action=ResetGameAction(self._bot, king_state),
            )
        )

        # -------------------------------------------------------------
        # 4. 組裝 Root FSM (Normal <-> Record <-> KnowledgeKing)
        # -------------------------------------------------------------
        root_fsm = FiniteStateMachine(initialState=normal_state)
        root_fsm.setTarget(self._bot)

        # Normal -> Record
        class SetupRecordSubStateAction(Action):
            def __init__(self, rec_state: RecordState, wait_st: State, rec_st: State):
                self.rec_state: RecordState = rec_state
                self.wait_st: State = wait_st
                self.rec_st: State = rec_st

            def execute(self, context: TransitionContext) -> None:
                # 初始子狀態判定：若有人廣播則直接為 Recording，否則 Waiting
                bot: Optional[Bot] = context.target
                if bot is not None and bot.getCommunity() is not None and bot.getCommunity().broadcast.isBroadcasting():
                    self.rec_state.getInnerFsm()._currentState = self.rec_st
                else:
                    self.rec_state.getInnerFsm()._currentState = self.wait_st

        root_fsm.addTransition(
            Transition(
                fromState=normal_state,
                toState=record_state,
                triggerName="record",
                action=SetupRecordSubStateAction(record_state, waiting, recording),
            )
        )

        # Record -> Normal (stop-recording)
        class StopRecordAndFlushAction(Action):
            def __init__(self, bot: Bot, rec_state: RecordState, rec_st: State):
                self.bot: Bot = bot
                self.rec_state: RecordState = rec_state
                self.rec_st: State = rec_st

            def execute(self, context: TransitionContext) -> None:
                # 如果此時為錄音中狀態，輸出截至目前錄下的所有語音
                if self.rec_state.getInnerFsm().getCurrentState() == self.rec_st and self.rec_state.session is not None:
                    if self.rec_state.session._voices:
                        replay_text = self.rec_state.session.generateReplay()
                        self.bot.replyChatMessage(replay_text, [self.rec_state.session.recorderId])

        class IsRecorderGuard(Guard):
            def __init__(self, rec_state: RecordState):
                self.rec_state: RecordState = rec_state

            def isSatisfied(self, context: TransitionContext) -> bool:
                sender_id = context.trigger.payload.get("memberId")
                if self.rec_state.session is not None:
                    return sender_id == self.rec_state.session.recorderId
                return False

        root_fsm.addTransition(
            Transition(
                fromState=record_state,
                toState=normal_state,
                triggerName="stop-recording",
                guard=IsRecorderGuard(record_state),
                action=StopRecordAndFlushAction(self._bot, record_state, recording),
            )
        )

        # Normal -> KnowledgeKing
        root_fsm.addTransition(
            Transition(
                fromState=normal_state,
                toState=king_state,
                triggerName="king",
            )
        )

        # KnowledgeKing -> Normal (king-stop 或 20秒滿 thanks_timeout)
        root_fsm.addTransition(
            Transition(
                fromState=king_state,
                toState=normal_state,
                triggerName="king-stop",
            )
        )
        root_fsm.addTransition(
            Transition(
                fromState=king_state,
                toState=normal_state,
                triggerName="thanks_timeout",
            )
        )

        self._bot.setFsm(root_fsm)

        # -------------------------------------------------------------
        # 5. 註冊 BotCommand (Command Pattern)
        # -------------------------------------------------------------
        self._bot.registerCommand("king", KingCommand())
        self._bot.registerCommand("record", RecordCommand())
        self._bot.registerCommand("stop-recording", StopRecordingCommand())
        self._bot.registerCommand("king-stop", KingStopCommand())
        self._bot.registerCommand("play again", PlayAgainCommand())

        # -------------------------------------------------------------
        # 6. 註冊 Observer 至各社群 Subject
        # -------------------------------------------------------------
        community.chatRoom.register(self._bot)
        community.forum.register(self._bot)
        community.broadcast.register(self._bot)
        community.register(self._bot)

        # 將 bot 本身加入在線參與者
        community.login(self._bot)

        # 依初始人數決定初始子狀態 (< 10 人為 DefaultConversation, >= 10 人為 Interacting)
        if community.getOnlineCount() >= 10:
            normal_fsm._currentState = interacting
        else:
            normal_fsm._currentState = default_conv

        return self._bot

    def build(self) -> Bot:
        return self._bot
