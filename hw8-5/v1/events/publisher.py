from abc import ABC, abstractmethod

from .domain_events import DomainEvent


class CommunityObserver(ABC):
    @abstractmethod
    def getId(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def onEvent(self, event: DomainEvent) -> None:
        raise NotImplementedError


class EventPublisher:
    def __init__(self, observers: list[CommunityObserver]):
        self.observers = observers

    def register(self, observer: CommunityObserver) -> None:
        raise NotImplementedError

    def unregister(self, observer: CommunityObserver) -> None:
        raise NotImplementedError

    def notify(self, event: DomainEvent) -> None:
        raise NotImplementedError
