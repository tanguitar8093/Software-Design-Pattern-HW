from ..events.domain_events import DomainEvent
from ..events.publisher import CommunityObserver
from ..fsm.core import FiniteStateMachine


class Bot(CommunityObserver):
    def __init__(self, quota: int, description: str, rootFsm: FiniteStateMachine, id: str = "bot"):
        self.id = id
        self.quota = quota
        self.description = description
        self.rootFsm = rootFsm

    def getId(self) -> str:
        raise NotImplementedError

    def onEvent(self, event: DomainEvent) -> None:
        raise NotImplementedError

    def replyChatMessage(self, content: str, tags: list[str]) -> None:
        raise NotImplementedError

    def commentPost(self, postId: str, content: str, tags: list[str]) -> None:
        raise NotImplementedError

    def broadcastVoice(self, content: str) -> None:
        raise NotImplementedError
