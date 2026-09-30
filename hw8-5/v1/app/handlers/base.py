from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional

from ..event_line_parser import ParsedEvent
from ..handler_context import HandlerContext


class HandlingResult(Enum):
    CONTINUE = "continue"
    STOP = "stop"


class EventHandler(ABC):
    """無法處理的事件交給下一節點；此階段由 concrete handler 自行判斷是否接手。"""

    def __init__(self, next_handler: Optional["EventHandler"] = None):
        self._next_handler = next_handler

    def forward(self, request: ParsedEvent, context: HandlerContext) -> HandlingResult:
        if self._next_handler is None:
            raise RuntimeError("event handler chain has no terminal handler")
        return self._next_handler.handle(request, context)

    @abstractmethod
    def handle(self, request: ParsedEvent, context: HandlerContext) -> HandlingResult:
        raise NotImplementedError
