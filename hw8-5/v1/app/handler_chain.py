from .handlers.base import EventHandler
from .handlers.broadcast import GoBroadcastingHandler, SpeakHandler, StopBroadcastingHandler
from .handlers.content import NewMessageHandler, NewPostHandler
from .handlers.lifecycle import EndHandler, StartedHandler, UnknownEventHandler
from .handlers.membership import LoginHandler, LogoutHandler
from .handlers.time import ElapsedHandler


def build_handler_chain() -> EventHandler:
    """唯一組裝處；新事件可在此加入新節點，driver 不需要改動。"""
    chain: EventHandler = UnknownEventHandler()
    for handler_type in reversed(
        (
            StartedHandler,
            LoginHandler,
            LogoutHandler,
            ElapsedHandler,
            NewMessageHandler,
            NewPostHandler,
            GoBroadcastingHandler,
            SpeakHandler,
            StopBroadcastingHandler,
            EndHandler,
        )
    ):
        chain = handler_type(next_handler=chain)
    return chain
