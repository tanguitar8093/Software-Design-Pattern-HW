from .handlers.base import EventHandler
from .handlers.activity import ActivityHandler
from .handlers.lifecycle import LifecycleHandler, UnknownEventHandler
from .handlers.membership import MembershipHandler


def build_handler_chain() -> EventHandler:
    """按責任組裝處理鏈；新增責任可在此插入節點。"""
    chain: EventHandler = UnknownEventHandler()
    for handler_type in reversed((LifecycleHandler, MembershipHandler, ActivityHandler)):
        chain = handler_type(next_handler=chain)
    return chain
