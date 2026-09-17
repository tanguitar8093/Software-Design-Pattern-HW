from __future__ import annotations
from typing import Dict, List, Optional
from .bot import Bot
from .commands import (
    BotCommand,
    KingCommand,
    KingStopCommand,
    PlayAgainCommand,
    RecordCommand,
    StopRecordingCommand,
)
from .states import (
    DefaultConversationState,
    FlushReplayAction,
    InteractingState,
    IsBroadcastingGuard,
    IsRecorderGuard,
    KnowledgeKingState,
    NormalState,
    OnlineCountGuard,
    QuestioningState,
    RecordingState,
    RecordState,
    ResetGameAction,
    ResetReplyCycleAction,
    SetupRecordSubStateAction,
    StopRecordAndFlushAction,
    ThanksForJoiningState,
    WaitingState,
)
from ..domain.community import WaterballCommunity
from ..fsm import (
    Action,
    CompositeState,
    FiniteStateMachine,
    Guard,
    State,
    SubStateMachinePlugin,
    Transition,
)


class BotFacade:
    """
    社群機器人門面 (Bot Facade):
    全面滿足 README 設計需求 - 2：
    1. 雙重介面設計：
       - buildDefaultBot(community)：保留一鍵組裝預設機器人，零感知高難度組裝細節。
       - Fluent Builder API (state, subState, command, transition, build)：
         允許應用層開發者僅用極少量宣告式代碼，高表達力地自訂或打造全新 A/B Test 機器人。
    2. 子系統裝配封裝：
       - 自動為包含 CompositeState 的 FSM 注入 SubStateMachinePlugin。
       - 自動連結 Community 領域觀察者與 Bot。
    """
    def __init__(self, quota: int = 10):
        self._bot: Bot = Bot(quota=quota)
        self._rootFsm: FiniteStateMachine = FiniteStateMachine()
        self._rootFsm.setTarget(self._bot)
        self._states: Dict[str, State] = {}
        self._currentCompositeState: Optional[CompositeState] = None

    @classmethod
    def create(cls, quota: int = 10) -> BotFacade:
        return cls(quota=quota)

    # ------------------------------------------------------------
    # Fluent Builder API (供 A/B Test 及自訂機器人使用，極大化生產力)
    # ------------------------------------------------------------
    def state(self, name: str, state: State, isInitial: bool = False) -> BotFacade:
        """註冊主狀態"""
        self._states[name] = state
        if isInitial or self._rootFsm.getCurrentState() is None:
            self._rootFsm.setCurrentState(state)
        return self

    def compositeState(self, name: str, compState: CompositeState, isInitial: bool = False) -> BotFacade:
        """註冊包含子狀態機的複合狀態，並自動安裝 SubStateMachinePlugin"""
        self._states[name] = compState
        self._currentCompositeState = compState
        if isInitial or self._rootFsm.getCurrentState() is None:
            self._rootFsm.setCurrentState(compState)
        if not any(isinstance(p, SubStateMachinePlugin) for p in self._rootFsm._plugins):
            self._rootFsm.installPlugin(SubStateMachinePlugin())
        return self

    def command(self, name: str, cmd: BotCommand) -> BotFacade:
        """註冊指令"""
        self._bot.registerCommand(name, cmd)
        return self

    def transition(
        self,
        fromState: str,
        toState: str,
        trigger: str,
        guard: Optional[Guard] = None,
        action: Optional[Action] = None,
    ) -> BotFacade:
        """建立主狀態機轉移路由"""
        from_st = self._states.get(fromState)
        to_st = self._states.get(toState)
        if from_st is not None and to_st is not None:
            self._rootFsm.addTransition(
                Transition(
                    fromState=from_st,
                    toState=to_st,
                    triggerName=trigger,
                    guard=guard,
                    action=action,
                )
            )
        return self

    def attachToCommunity(self, community: WaterballCommunity) -> BotFacade:
        """將機器人註冊為社群觀察者並加入社群"""
        self._bot.setCommunity(community)
        community.chatRoom.register(self._bot)
        community.forum.register(self._bot)
        community.broadcast.register(self._bot)
        community.register(self._bot)
        community.login(self._bot)
        return self

    def build(self) -> Bot:
        """產出最終機器人產品"""
        self._bot.setFsm(self._rootFsm)
        return self._bot

    # ------------------------------------------------------------
    # 一鍵組裝官方預設機器人 (Zero-Config Default Bot)
    # ------------------------------------------------------------
    def buildDefaultBot(self, community: WaterballCommunity) -> Bot:
        self._bot.setCommunity(community)

        # 1. NormalState 內部子狀態機 (安裝 SubStateMachinePlugin 支援任意深度)
        default_conv = DefaultConversationState()
        interacting = InteractingState()
        normal_fsm = FiniteStateMachine(initialState=default_conv)
        normal_fsm.setTarget(self._bot)
        normal_fsm.installPlugin(SubStateMachinePlugin())

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
        record_fsm.installPlugin(SubStateMachinePlugin())

        record_fsm.addTransition(
            Transition(
                fromState=waiting,
                toState=recording,
                triggerName="broadcast_started",
            )
        )

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
        king_fsm.installPlugin(SubStateMachinePlugin())

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

        # 4. Root FSM (安裝 SubStateMachinePlugin)
        root_fsm = FiniteStateMachine(initialState=normal_state)
        root_fsm.setTarget(self._bot)
        root_fsm.installPlugin(SubStateMachinePlugin())

        root_fsm.addTransition(
            Transition(
                fromState=normal_state,
                toState=record_state,
                triggerName="record",
                action=SetupRecordSubStateAction(record_state, waiting, recording),
            )
        )

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

        self._rootFsm = root_fsm
        self._bot.setFsm(root_fsm)

        # 5. 註冊指令
        self._bot.registerCommand("king", KingCommand())
        self._bot.registerCommand("record", RecordCommand())
        self._bot.registerCommand("stop-recording", StopRecordingCommand())
        self._bot.registerCommand("king-stop", KingStopCommand())
        self._bot.registerCommand("play again", PlayAgainCommand())

        # 6. 註冊 Observer 並加入社群
        self.attachToCommunity(community)

        # 7. 依初始線上人數決定 NormalState 之子狀態
        if community.getOnlineCount() >= 10:
            normal_fsm.setCurrentState(interacting)
        else:
            normal_fsm.setCurrentState(default_conv)

        return self._bot
