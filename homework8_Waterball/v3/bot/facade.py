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
    Action,
    DefaultConversationState,
    FlushReplayAction,
    Guard,
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
    SelectRecordSubStateAction,
    State,
    StopRecordAction,
    ThanksForJoiningState,
    WaitingState,
)
from ..domain.community import WaterballCommunity
from ..fsm import (
    CompositeState,
    FiniteStateMachine,
    FsmPlugin,
    SubStateMachinePlugin,
    Transition,
)


class BotDefinition:
    """
    社群機器人組態定義 (Bot Module Configuration):
    依照 OODv5-1.mmd 規格，允許開發者以簡潔物件定義組裝機器人，
    支援 A/B Test 及各類客製化機器人行為配置。
    """
    def __init__(self):
        self._rootState: Optional[State] = None
        self._rootTransitions: List[Transition] = []
        self._commands: Dict[str, BotCommand] = {}
        self._plugins: List[FsmPlugin] = []

    def setInitialState(self, state: State) -> BotDefinition:
        self._rootState = state
        return self

    def addTransition(self, transition: Transition) -> BotDefinition:
        self._rootTransitions.append(transition)
        return self

    def addCommand(self, name: str, command: BotCommand) -> BotDefinition:
        self._commands[name] = command
        return self

    def installPlugin(self, plugin: FsmPlugin) -> BotDefinition:
        self._plugins.append(plugin)
        return self

    def buildFsm(self, target: any) -> FiniteStateMachine:
        fsm = FiniteStateMachine(initialState=self._rootState, target=target)
        for plugin in self._plugins:
            fsm.installPlugin(plugin)
        for transition in self._rootTransitions:
            fsm.addTransition(transition)
        return fsm


class BotFacade:
    """
    社群機器人門面 (Bot Facade):
    對 Application Layer (Client) 提供最簡潔之高階組裝介面：
    1. createDefaultBot(community, quota)：一鍵產生官方規格預設機器人。
    2. createBot(community, definition, quota)：依 BotDefinition 產出客製化機器人。
    """

    @classmethod
    def createBot(
        cls,
        community: WaterballCommunity,
        definition: BotDefinition,
        quota: int = 10,
    ) -> Bot:
        bot = Bot(quota=quota)
        root_fsm = definition.buildFsm(target=bot)
        bot.setFsm(root_fsm)

        for name, cmd in definition._commands.items():
            bot.registerCommand(name, cmd)

        community.chatRoom.register(bot)
        community.forum.register(bot)
        community.broadcast.register(bot)
        community.register(bot)

        bot.setCommunity(community)
        community.login(bot)
        return bot

    @classmethod
    def createDefaultBot(
        cls,
        community: WaterballCommunity,
        quota: int = 10,
    ) -> Bot:
        # 1. NormalState 內部子狀態機
        default_conv = DefaultConversationState()
        interacting = InteractingState()
        normal_fsm = FiniteStateMachine(initialState=default_conv)
        normal_fsm.installPlugin(SubStateMachinePlugin())

        normal_fsm.addTransition(
            Transition(
                fromState=default_conv,
                toState=interacting,
                triggerName="online_changed",
                guard=OnlineCountGuard(threshold=10, greaterOrEqual=True),
            )
        )
        normal_fsm.addTransition(
            Transition(
                fromState=interacting,
                toState=default_conv,
                triggerName="online_changed",
                guard=OnlineCountGuard(threshold=10, greaterOrEqual=False),
                action=ResetReplyCycleAction(),
            )
        )
        normal_state = NormalState(innerFsm=normal_fsm)

        # 2. RecordState 內部子狀態機
        waiting = WaitingState()
        recording = RecordingState()
        record_fsm = FiniteStateMachine(initialState=waiting)
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
                action=FlushReplayAction(recordState=record_state),
            )
        )

        # 3. KnowledgeKingState 內部子狀態機
        questioning = QuestioningState()
        thanks = ThanksForJoiningState()
        king_fsm = FiniteStateMachine(initialState=questioning)
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
                action=ResetGameAction(knowledgeKingState=king_state),
            )
        )
        king_fsm.addTransition(
            Transition(
                fromState=thanks,
                toState=questioning,
                triggerName="play again",
                action=ResetGameAction(knowledgeKingState=king_state),
            )
        )

        # 4. Root 轉移與指令定義
        definition = BotDefinition()
        definition.setInitialState(normal_state)
        definition.installPlugin(SubStateMachinePlugin())

        definition.addTransition(
            Transition(
                fromState=normal_state,
                toState=record_state,
                triggerName="record",
                action=SelectRecordSubStateAction(record_state, waiting, recording),
            )
        )
        definition.addTransition(
            Transition(
                fromState=record_state,
                toState=normal_state,
                triggerName="stop-recording",
                guard=IsRecorderGuard(record_state),
                action=StopRecordAction(record_state, recording),
            )
        )
        definition.addTransition(
            Transition(
                fromState=normal_state,
                toState=king_state,
                triggerName="king",
            )
        )
        definition.addTransition(
            Transition(
                fromState=king_state,
                toState=normal_state,
                triggerName="king-stop",
            )
        )
        definition.addTransition(
            Transition(
                fromState=king_state,
                toState=normal_state,
                triggerName="thanks_timeout",
            )
        )

        definition.addCommand("king", KingCommand())
        definition.addCommand("record", RecordCommand())
        definition.addCommand("stop-recording", StopRecordingCommand())
        definition.addCommand("king-stop", KingStopCommand())
        definition.addCommand("play again", PlayAgainCommand())

        bot = cls.createBot(community=community, definition=definition, quota=quota)

        normal_fsm.setTarget(bot)
        record_fsm.setTarget(bot)
        king_fsm.setTarget(bot)

        # 依初始在線人數設定 normal 初始子狀態
        if community.getOnlineCount() >= 10:
            normal_fsm.setCurrentState(interacting)
        else:
            normal_fsm.setCurrentState(default_conv)

        return bot

    # ------------------------------------------------------------
    # 相容介面
    # ------------------------------------------------------------
    @classmethod
    def create(cls, quota: int = 10) -> BotFacadeHelper:
        return BotFacadeHelper(quota=quota)


class BotFacadeHelper:
    def __init__(self, quota: int = 10):
        self.quota = quota

    def buildDefaultBot(self, community: WaterballCommunity) -> Bot:
        return BotFacade.createDefaultBot(community, quota=self.quota)
