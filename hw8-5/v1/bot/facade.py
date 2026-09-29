from ..activities.knowledge_king import Question
from ..community.community import WaterCommunity
from ..fsm.core import FiniteStateMachine, Transition
from ..fsm.initial_state_selector import GuardedInitialStateSelector
from .actions.composite import CompositeAction, NoopAction
from .actions.concrete import (
    AddVoiceToRecordingSessionAction,
    AnnounceGameResultAction,
    CarryGameToThanksForJoiningAction,
    ClearRecorderAction,
    CommentPostAction,
    CreateKnowledgeKingGameAction,
    CreateRecordingSessionAction,
    DeductQuotaAction,
    FlushRecordReplayAction,
    ResetReplyCycleAction,
    SendChatMessageAction,
    SetRecorderAction,
    SubmitAnswerAction,
)
from .bot import Bot
from .guards.composite import AndGuard, NotGuard
from .guards.concrete import (
    AdminOnlyGuard,
    AnswerCorrectGuard,
    DurationElapsedGuard,
    IsBroadcastingGuard,
    IsRecorderGuard,
    LastQuestionGuard,
    OnlineCountAtLeastGuard,
    QuotaAvailableGuard,
    SubstateActiveGuard,
)
from .internal_reaction import InternalReaction
from .states import (
    DefaultConversationState,
    InteractingState,
    QuestioningState,
    RecordingState,
    ThanksForJoiningState,
    WaitingState,
)
from .triggers.triggers import (
    BroadcastStartedTrigger,
    BroadcastStoppedTrigger,
    CommandTrigger,
    LoginTrigger,
    LogoutTrigger,
    MentionsBotTrigger,
    MessageFromMemberTrigger,
    PostCreatedTrigger,
    TimeElapsedTrigger,
    VoiceSpokenTrigger,
)


class BotFacade:
    """對外唯一入口：把「組一堆 State/Guard/Action/Trigger/Transition 才能生出 Bot」的複雜度包起來。"""

    def __init__(self, community: WaterCommunity, quota: int = 20, description: str = "Waterball 知識王機器人"):
        noop = NoopAction()
        default = DefaultConversationState(noop, noop, messages=["good to hear", "thank you", "How are you"])
        interacting = InteractingState(noop, noop, messages=["Hi hi😁", "I like your idea!"])
        waiting = WaitingState(noop, noop)
        recording = RecordingState(noop, noop)
        questioning = QuestioningState(noop, noop)
        thanksForJoining = ThanksForJoiningState(noop, noop)

        rootInitialStateSelector = GuardedInitialStateSelector([], default)
        rootFsm = FiniteStateMachine(currentState=None, initialStateSelector=rootInitialStateSelector, transitions=[])
        bot = Bot(community=community, quota=quota, description=description, rootFsm=rootFsm)

        # 進場/離場行為要拿到 bot/state 自己的參照才能組，狀態建構完之後才回頭補上
        default.enter = ResetReplyCycleAction(default)
        interacting.enter = ResetReplyCycleAction(interacting)
        recording.enter = CreateRecordingSessionAction(recording, bot)
        recording.exit = FlushRecordReplayAction(bot, recording)
        questioning.enter = SendChatMessageAction(bot, lambda event: self._formatQuestion(questioning))
        thanksForJoining.enter = AnnounceGameResultAction(bot, thanksForJoining)

        normalFsm = FiniteStateMachine(
            currentState=None,
            initialStateSelector=GuardedInitialStateSelector([(OnlineCountAtLeastGuard(bot, 10), interacting)], default),
            transitions=[
                Transition(from_=default, trigger=LoginTrigger(), to=interacting, guard=OnlineCountAtLeastGuard(bot, 10)),
                Transition(
                    from_=interacting,
                    trigger=LogoutTrigger(),
                    to=default,
                    guard=NotGuard(OnlineCountAtLeastGuard(bot, 10)),
                ),
            ],
        )
        recordFsm = FiniteStateMachine(
            currentState=None,
            initialStateSelector=GuardedInitialStateSelector([(IsBroadcastingGuard(bot), recording)], waiting),
            transitions=[
                Transition(from_=waiting, trigger=BroadcastStartedTrigger(), to=recording),
                Transition(from_=recording, trigger=BroadcastStoppedTrigger(), to=waiting),
            ],
        )
        questions = self._buildQuestions()
        answerCorrectGuard = AnswerCorrectGuard(questioning)
        lastQuestionGuard = LastQuestionGuard(questioning)
        knowledgeKingFsm = FiniteStateMachine(
            currentState=None,
            initialStateSelector=GuardedInitialStateSelector([], questioning),
            transitions=[
                Transition(
                    from_=questioning,
                    trigger=MentionsBotTrigger(),
                    to=thanksForJoining,
                    guard=AndGuard([answerCorrectGuard, lastQuestionGuard]),
                    action=CompositeAction(
                        [
                            SubmitAnswerAction(questioning),
                            SendChatMessageAction(
                                bot,
                                lambda event: "Congrats! you got the answer!",
                                tagsProvider=lambda event: [event.getSourceId()],  # type: ignore[union-attr]
                            ),
                            CarryGameToThanksForJoiningAction(questioning, thanksForJoining),
                        ]
                    ),
                ),
                Transition(
                    from_=questioning,
                    trigger=TimeElapsedTrigger(),
                    to=thanksForJoining,
                    guard=DurationElapsedGuard(bot, 1, "hour", lambda: questioning.game.startTime),  # type: ignore[union-attr]
                    action=CarryGameToThanksForJoiningAction(questioning, thanksForJoining),
                ),
            ],
        )
        knowledgeKingFsm.addTransition(
            Transition(
                from_=knowledgeKingFsm,
                trigger=CommandTrigger("play again"),
                to=knowledgeKingFsm,
                guard=QuotaAvailableGuard(bot, 5),
                action=CompositeAction(
                    [
                        DeductQuotaAction(bot, 5),
                        SendChatMessageAction(bot, lambda event: "KnowledgeKing is gonna start again!"),
                        CreateKnowledgeKingGameAction(questioning, bot, questions),
                    ]
                ),
            )
        )  # self-loop：composite 自己轉移到自己，onExit/onEnter 會重新跑，符合「再玩一次」要整個重置的需求

        rootInitialStateSelector.fallback = normalFsm  # 建構順序限制：rootFsm 早於 normalFsm 存在，事後補上真正的初始子狀態
        rootFsm.addTransition(
            Transition(
                from_=normalFsm,
                trigger=CommandTrigger("king"),
                to=knowledgeKingFsm,
                guard=AndGuard([AdminOnlyGuard(bot), QuotaAvailableGuard(bot, 5)]),
                action=CompositeAction(
                    [
                        DeductQuotaAction(bot, 5),
                        CreateKnowledgeKingGameAction(questioning, bot, questions),
                        SendChatMessageAction(bot, lambda event: "KnowledgeKing is started!"),
                    ]
                ),
            )
        )
        rootFsm.addTransition(
            Transition(
                from_=normalFsm,
                trigger=CommandTrigger("record"),
                to=recordFsm,
                guard=QuotaAvailableGuard(bot, 3),
                action=CompositeAction([DeductQuotaAction(bot, 3), SetRecorderAction(bot)]),
            )
        )
        rootFsm.addTransition(
            Transition(
                from_=recordFsm,
                trigger=CommandTrigger("stop-recording"),
                to=normalFsm,
                guard=IsRecorderGuard(bot),
                action=ClearRecorderAction(bot),
            )
        )
        rootFsm.addTransition(
            Transition(
                from_=knowledgeKingFsm,
                trigger=CommandTrigger("king-stop"),
                to=normalFsm,
                guard=AdminOnlyGuard(bot),
            )
        )
        rootFsm.addTransition(
            Transition(
                from_=knowledgeKingFsm,
                trigger=TimeElapsedTrigger(),
                to=normalFsm,
                guard=AndGuard(
                    [
                        SubstateActiveGuard(knowledgeKingFsm, thanksForJoining),
                        DurationElapsedGuard(bot, 20, "second", lambda: thanksForJoining.enteredAt),  # type: ignore[arg-type]
                    ]
                ),
            )
        )

        self._wireInternalReactions(bot, default, interacting, recording, questioning, answerCorrectGuard, lastQuestionGuard)

        rootFsm.onEnter(None)  # 程式啟動時對根 FSM 呼叫一次，決定初始狀態
        self.bot = bot

    def _wireInternalReactions(
        self,
        bot: Bot,
        default: DefaultConversationState,
        interacting: InteractingState,
        recording: RecordingState,
        questioning: QuestioningState,
        answerCorrectGuard: AnswerCorrectGuard,
        lastQuestionGuard: LastQuestionGuard,
    ) -> None:
        bot.addInternalReaction(
            InternalReaction(
                state=default,
                trigger=MessageFromMemberTrigger(),
                action=SendChatMessageAction(
                    bot,
                    lambda event: default.getNextReplyMessage(),
                    tagsProvider=lambda event: [event.getSourceId()],  # type: ignore[union-attr]
                ),
            )
        )
        bot.addInternalReaction(
            InternalReaction(
                state=interacting,
                trigger=MessageFromMemberTrigger(),
                action=SendChatMessageAction(
                    bot,
                    lambda event: interacting.getNextReplyMessage(),
                    tagsProvider=lambda event: [event.getSourceId()],  # type: ignore[union-attr]
                ),
            )
        )
        bot.addInternalReaction(
            InternalReaction(
                state=default,
                trigger=PostCreatedTrigger(),
                action=CommentPostAction(bot, "Nice post", tagsProvider=lambda event: [event.post.authorId]),  # type: ignore[union-attr]
            )
        )
        bot.addInternalReaction(
            InternalReaction(
                state=interacting,
                trigger=PostCreatedTrigger(),
                action=CommentPostAction(
                    bot, "How do you guys think about it?", tagsProvider=lambda event: bot.getOnlineParticipantIds()
                ),
            )
        )
        bot.addInternalReaction(
            InternalReaction(
                state=recording,
                trigger=VoiceSpokenTrigger(),
                action=AddVoiceToRecordingSessionAction(recording),
            )
        )
        bot.addInternalReaction(
            InternalReaction(
                state=questioning,
                trigger=MentionsBotTrigger(),
                guard=AndGuard([answerCorrectGuard, NotGuard(lastQuestionGuard)]),
                action=CompositeAction(
                    [
                        SubmitAnswerAction(questioning),
                        SendChatMessageAction(
                            bot,
                            lambda event: "Congrats! you got the answer!",
                            tagsProvider=lambda event: [event.getSourceId()],  # type: ignore[union-attr]
                        ),
                        SendChatMessageAction(bot, lambda event: self._formatQuestion(questioning)),
                    ]
                ),
            )
        )

    def _formatQuestion(self, questioning: QuestioningState) -> str:
        assert questioning.game is not None
        question = questioning.game.getCurrentQuestion()
        return f"{question.number}. {question.description}"

    def _buildQuestions(self) -> list[Question]:
        return [
            Question(
                0,
                "請問哪個 SQL 語句用於選擇所有的行？(A) SELECT * (B) SELECT ALL (C) SELECT ROWS (D) SELECT DATA",
                ["A", "B", "C", "D"],
                "A",
            ),
            Question(
                1,
                "請問哪個 CSS 屬性可用於設置文字的顏色？(A) text-align (B) font-size (C) color (D) padding",
                ["A", "B", "C", "D"],
                "C",
            ),
            Question(
                2,
                "請問在計算機科學中，「XML」代表什麼？(A) Extensible Markup Language (B) Extensible Modeling Language "
                "(C) Extended Markup Language (D) Extended Modeling Language",
                ["A", "B", "C", "D"],
                "A",
            ),
        ]
