from ..fsm.core import Action, Event, StateNode, Trigger


class InternalReaction:
    """同一個 leaf state 內、不換狀態也要發生的原地反應（如訊息輪播、留言）。

    刻意不放進 fsm/ 底下：這裡認識「leaf state 是誰」這種 Bot 業務語意，
    FSM 模組本身不能知道 Bot 的存在，只重用 FSM 已經定義好的 Trigger/Action 介面。
    """

    def __init__(self, state: StateNode, trigger: Trigger, action: Action):
        self.state = state
        self.trigger = trigger
        self.action = action

    def isApplicable(self, activeLeafState: StateNode, event: Event) -> bool:
        return activeLeafState is self.state and self.trigger.isTriggeredBy(event)
