from ..activities.knowledge_king import Question
from ..community.community import WaterCommunity
from ..fsm.core import Action, Event, FiniteStateMachine, StateNode, Transition
from ..fsm.initial_state_selector import GuardedInitialStateSelector
from .actions.composite import CompositeAction
from .actions.concrete import CreateKnowledgeKingGameAction, DeductQuotaAction, SendChatMessageAction
from .bot import Bot
from .guards.composite import AndGuard
from .guards.concrete import AdminOnlyGuard, QuotaAvailableGuard
from .internal_reaction import InternalReaction
from .states import DefaultConversationState, QuestioningState
from .triggers.triggers import CommandTrigger, MentionsBotTrigger


class _NoopAction(Action):
    """佔位用：示範範圍內的狀態還沒設計 entry/exit 行為，先用不做事的 Action 卡位。"""

    def execute(self, event: Event) -> None:
        pass


class BotFacade:
    """對外唯一入口：把「組一堆 State/Guard/Action/Trigger/Transition 才能生出 Bot」的複雜度包起來。

    TODO（下一輪要補齊，目前只示範 king 指令 + 訊息輪播原地反應這兩條）：
    - Normal/Record 兩個複合狀態（GuardedInitialStateSelector 版本）
    - 剩下 4 個指令：record / stop-recording / play again / king-stop
    - Questioning 答對/答錯/超時分支、ThanksForJoining 20 秒回 Normal
    - 論壇留言（CommentPostAction）原地反應
    """

    def __init__(self, community: WaterCommunity, quota: int = 20, description: str = "Waterball 知識王機器人"):
        states = self._buildStates()
        rootFsm = self._buildRootFsm(states)
        bot = Bot(community=community, quota=quota, description=description, rootFsm=rootFsm)

        self._wireKingTransition(rootFsm, states, bot)
        self._wireInternalReactions(states, bot)
        rootFsm.onEnter(None)  # 程式啟動時對根 FSM 呼叫一次，決定初始狀態

        self.bot = bot

    def _buildStates(self) -> dict[str, StateNode]:
        noop = _NoopAction()
        return {
            "default": DefaultConversationState(noop, noop, messages=["嗨，我是知識王機器人！", "有事叫我就 tag 我 🙂"]),
            "questioning": QuestioningState(noop, noop),
        }

    def _buildRootFsm(self, states: dict[str, StateNode]) -> FiniteStateMachine:
        return FiniteStateMachine(
            currentState=None,
            initialStateSelector=GuardedInitialStateSelector([], states["default"]),
            transitions=[],
        )

    def _wireInternalReactions(self, states: dict[str, StateNode], bot: Bot) -> None:
        defaultState = states["default"]
        assert isinstance(defaultState, DefaultConversationState)
        bot.addInternalReaction(
            InternalReaction(
                state=defaultState,
                trigger=MentionsBotTrigger(),
                action=SendChatMessageAction(bot, lambda event: defaultState.getNextReplyMessage()),
            )
        )

    def _wireKingTransition(self, rootFsm: FiniteStateMachine, states: dict[str, StateNode], bot: Bot) -> None:
        questioningState = states["questioning"]
        assert isinstance(questioningState, QuestioningState)
        questions = self._buildDemoQuestions()
        rootFsm.addTransition(
            Transition(
                from_=states["default"],
                trigger=CommandTrigger("king"),
                to=questioningState,
                guard=AndGuard([AdminOnlyGuard(bot), QuotaAvailableGuard(bot, 5)]),
                action=CompositeAction(
                    [
                        DeductQuotaAction(bot, 5),
                        CreateKnowledgeKingGameAction(questioningState, bot, questions),
                    ]
                ),
            )
        )

    def _buildDemoQuestions(self) -> list[Question]:
        return [
            Question(1, "TODO: 題目 1", ["A", "B", "C"], "A"),
            Question(2, "TODO: 題目 2", ["A", "B", "C"], "B"),
            Question(3, "TODO: 題目 3", ["A", "B", "C"], "C"),
        ]
