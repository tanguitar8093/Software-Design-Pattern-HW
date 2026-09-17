import pytest
from v3.bot import BotDefinition, BotFacade
from v3.bot.commands import KingCommand
from v3.bot.states import (
    DefaultConversationState,
    InteractingState,
    NormalState,
    OnlineCountGuard,
)
from v3.domain import Member, WaterballCommunity
from v3.fsm import (
    FiniteStateMachine,
    SubStateMachinePlugin,
    Transition,
)


def test_bot_definition_custom_bot():
    """
    測試依據 OODv5-1.mmd 規格之 BotDefinition 與 BotFacade.createBot：
    允許開發者以宣告式組態自訂全新機器人 (A/B Test 情境)
    """
    community = WaterballCommunity()
    admin = Member(id="admin_1")
    community.login(admin)

    # 1. 建立子狀態機
    sub_fsm = FiniteStateMachine(initialState=DefaultConversationState())
    sub_fsm.addTransition(
        Transition(
            fromState=sub_fsm.getCurrentState(),
            toState=InteractingState(),
            triggerName="online_changed",
            guard=OnlineCountGuard(threshold=5, greaterOrEqual=True),
        )
    )

    # 2. 透過 BotDefinition 定義組態
    definition = BotDefinition()
    definition.setInitialState(NormalState(innerFsm=sub_fsm))
    definition.installPlugin(SubStateMachinePlugin())
    definition.addCommand("king", KingCommand())

    # 3. 透過 BotFacade 建立產品
    custom_bot = BotFacade.createBot(community, definition=definition, quota=50)

    assert custom_bot.quota == 50
    assert custom_bot.getCommunity() == community
    assert "king" in custom_bot._commands
    assert custom_bot._rootFsm is not None
    assert any(isinstance(p, SubStateMachinePlugin) for p in custom_bot._rootFsm._plugins)
