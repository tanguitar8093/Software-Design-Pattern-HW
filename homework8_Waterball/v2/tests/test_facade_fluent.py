import pytest
from v2.bot import BotFacade
from v2.bot.commands import KingCommand
from v2.bot.states import (
    DefaultConversationState,
    InteractingState,
    NormalState,
    OnlineCountGuard,
)
from v2.domain import Member, WaterballCommunity
from v2.fsm import (
    FiniteStateMachine,
    SubStateMachinePlugin,
    Transition,
)


def test_fluent_builder_api_custom_bot():
    """
    測試 BotFacade 的 Fluent API 能以極簡宣告式組裝出新的客製化機器人 (A/B Test 情境)
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
            guard=OnlineCountGuard(threshold=5, greater_or_equal=True),
        )
    )

    # 2. 透過 BotFacade Fluent API 鏈式宣告組裝
    facade = (
        BotFacade.create(quota=50)
        .compositeState("NORMAL", NormalState(innerFsm=sub_fsm), isInitial=True)
        .command("king", KingCommand())
        .attachToCommunity(community)
    )
    custom_bot = facade.build()

    assert custom_bot.quota == 50
    assert custom_bot.getCommunity() == community
    assert "king" in custom_bot._commands
    assert custom_bot._rootFsm is not None
    assert any(isinstance(p, SubStateMachinePlugin) for p in custom_bot._rootFsm._plugins)
