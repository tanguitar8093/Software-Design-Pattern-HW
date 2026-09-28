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
        if observer not in self.observers:
            self.observers.append(observer)

    def unregister(self, observer: CommunityObserver) -> None:
        if observer in self.observers:
            self.observers.remove(observer)

    def notify(self, event: DomainEvent) -> None:
        for observer in self.observers:
            observer.onEvent(event)
