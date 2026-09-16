from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, List
from homework8_Waterball.v1.common.enums import CommunityEventType


class CommunityEvent(ABC):
    def __init__(self, event_type: CommunityEventType):
        self.type: CommunityEventType = event_type

    @abstractmethod
    def dispatchTo(self, bot: Any) -> None:
        pass


class CommunityObserver(ABC):
    @abstractmethod
    def update(self, event: CommunityEvent) -> None:
        pass


class Observable(ABC):
    def __init__(self):
        self._observers: List[CommunityObserver] = []

    def register(self, observer: CommunityObserver) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def unregister(self, observer: CommunityObserver) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, event: CommunityEvent) -> None:
        for obs in list(self._observers):
            obs.update(event)
