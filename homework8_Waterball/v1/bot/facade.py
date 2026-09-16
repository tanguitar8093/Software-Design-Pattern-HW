from __future__ import annotations
from typing import Dict, Optional
from homework8_Waterball.v1.bot.bot import Bot
from homework8_Waterball.v1.bot.commands import (
    BotCommand,
    KingCommand,
    KingStopCommand,
    PlayAgainCommand,
    RecordCommand,
    StopRecordingCommand,
)
from homework8_Waterball.v1.bot.states import (
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
from homework8_Waterball.v1.domain.community import WaterballCommunity
from homework8_Waterball.v1.fsm import (
    Action,
    FiniteStateMachine,
    Guard,
    State,
    Transition,
    TransitionContext,
)


class BotFacade:
    def __init__(self, quota: int = 10):
        self._bot: Bot = Bot(quota=quota)
        self._states: Dict[str, State] = {}

    @classmethod
    def create(cls, quota: int = 10) -> BotFacade:
        return cls(quota=quota)

    def buildDefaultBot(self, community: WaterballCommunity) -> Bot:
        self._bot.setCommunity(community)

        # 1. NormalState 內部子狀態機
        default_conv = DefaultConversationState()
        interacting = InteractingState()
        normal_fsm = FiniteStateMachine(initialState=default_conv)
        normal_fsm.setTarget(self._bot)

        normal_fsm.addTransition(
            Transition(
                fromState=default_conv,
                toState=interacting,
                triggerName="online_changed",
                guard=OnlineCountGuard(threshold=10, greater_or_equal=True),
            )
        )
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

        # 2. RecordState 內部子狀態機
        waiting = WaitingState()
        recording = RecordingState()
        record_fsm = FiniteStateMachine(initialState=waiting)
        record_fsm.setTarget(self._bot)

        record_fsm.addTransition(
            Transition(
                fromState=waiting,
                toState=recording,
                triggerName="broadcast_started",
            )
        )

        class FlushReplayAction(Action):
            def __init__(self, bot: Bot, rec_state: RecordState):
                self.bot: Bot = bot
                self.rec_state: RecordState = rec_state

            def execute(self, context: TransitionContext) -> None:
                if self.rec_state.session is not None:
                    replay_text = self.rec_state.session.generateReplay()
                    self.bot.replyChatMessage(replay_text, [self.rec_state.session.recorderId])
                    self.rec_state.session._voices.clear()

        record_state = RecordState(innerFsm=record_fsm)

        record_fsm.addTransition(
            Transition(
                fromState=recording,
                toState=waiting,
                triggerName="broadcast_stopped",
                action=FlushReplayAction(self._bot, record_state),
            )
        )

        # 3. KnowledgeKingState 內部子狀態機
        questioning = QuestioningState()
        thanks = ThanksForJoiningState()
        king_fsm = FiniteStateMachine(initialState=questioning)
        king_fsm.setTarget(self._bot)

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

        class ResetGameAction(Action):
            def __init__(self, bot: Bot, king_state: KnowledgeKingState):
                self.bot: Bot = bot
                self.king_state: KnowledgeKingState = king_state

            def execute(self, context: TransitionContext) -> None:
                game = context.trigger.payload.get("game")
                if game is not None:
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

        # 4. Root FSM
        root_fsm = FiniteStateMachine(initialState=normal_state)
        root_fsm.setTarget(self._bot)

        class SetupRecordSubStateAction(Action):
            def __init__(self, rec_state: RecordState, wait_st: State, rec_st: State):
                self.rec_state: RecordState = rec_state
                self.wait_st: State = wait_st
                self.rec_st: State = rec_st

            def execute(self, context: TransitionContext) -> None:
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

        class StopRecordAndFlushAction(Action):
            def __init__(self, bot: Bot, rec_state: RecordState, rec_st: State):
                self.bot: Bot = bot
                self.rec_state: RecordState = rec_state
                self.rec_st: State = rec_st

            def execute(self, context: TransitionContext) -> None:
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

        root_fsm.addTransition(
            Transition(
                fromState=normal_state,
                toState=king_state,
                triggerName="king",
            )
        )
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

        # 5. 註冊指令
        self._bot.registerCommand("king", KingCommand())
        self._bot.registerCommand("record", RecordCommand())
        self._bot.registerCommand("stop-recording", StopRecordingCommand())
        self._bot.registerCommand("king-stop", KingStopCommand())
        self._bot.registerCommand("play again", PlayAgainCommand())

        # 6. 註冊 Observer
        community.chatRoom.register(self._bot)
        community.forum.register(self._bot)
        community.broadcast.register(self._bot)
        community.register(self._bot)

        community.login(self._bot)

        if community.getOnlineCount() >= 10:
            normal_fsm._currentState = interacting
        else:
            normal_fsm._currentState = default_conv

        return self._bot

    def build(self) -> Bot:
        return self._bot
