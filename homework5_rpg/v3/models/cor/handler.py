from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.unit import Unit

class Handler(ABC):
    def __init__(self, next_handler: 'Handler' = None):
        self.next = next_handler

    def handle(self, actor: 'Unit', target: 'Unit') -> bool:
        if self.do_handle(actor, target):
            return True
        if self.next:
            return self.next.handle(actor, target)
        return False

    @abstractmethod
    def do_handle(self, actor: 'Unit', target: 'Unit') -> bool:
        pass


class HighHPHandler(Handler):
    def do_handle(self, actor: 'Unit', target: 'Unit') -> bool:
        if target.hp >= 500:
            actor.cause_damage(target, 300)
            return True
        return False


class DebuffHandler(Handler):
    def do_handle(self, actor: 'Unit', target: 'Unit') -> bool:
        state_name = target.current_state.name if target.current_state else "正常"
        if state_name in ["中毒", "石化"]:
            # 打三次，如果中途目標死亡則不再攻擊
            for _ in range(3):
                if target.hp <= 0:
                    break
                actor.cause_damage(target, 80)
            return True
        return False


class CheeredUpHandler(Handler):
    def do_handle(self, actor: 'Unit', target: 'Unit') -> bool:
        state_name = target.current_state.name if target.current_state else "正常"
        if state_name == "受到鼓舞":
            actor.cause_damage(target, 100)
            # 狀態恢復正常
            from models.states.states import NormalState
            target.change_state(NormalState())
            return True
        return False


class NormalHandler(Handler):
    def do_handle(self, actor: 'Unit', target: 'Unit') -> bool:
        state_name = target.current_state.name if target.current_state else "正常"
        if state_name == "正常":
            actor.cause_damage(target, 100)
            return True
        return False
