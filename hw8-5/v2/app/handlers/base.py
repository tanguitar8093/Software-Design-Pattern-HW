from abc import ABC, abstractmethod
from enum import Enum
from typing import ClassVar, Optional, final

from ..event_line_parser import ParsedEvent
from ..event_type import InputEventType
from ..handler_context import HandlerContext


class HandlingResult(Enum):
    CONTINUE = "continue"
    STOP = "stop"


class EventHandler(ABC):
    """固定的責任鏈流程：先判斷接手者，否則轉交下一節點。"""

    event_types: ClassVar[frozenset[InputEventType]] = frozenset()

    def __init__(self, next_handler: Optional["EventHandler"] = None):
        self._next_handler = next_handler

    def forward(self, request: ParsedEvent, context: HandlerContext) -> HandlingResult:
        if self._next_handler is None:
            raise RuntimeError("event handler chain has no terminal handler")
        return self._next_handler.handle(request, context)

    @final
    def handle(self, request: ParsedEvent, context: HandlerContext) -> HandlingResult:
        if self.can_handle(request):
            return self.execute(request, context)
        return self.forward(request, context)

    def can_handle(self, request: ParsedEvent) -> bool:
        """預設按所負責的事件集合匹配；特殊節點可覆寫此判斷。"""
        return request.name in self.event_types

    @abstractmethod
    def execute(self, request: ParsedEvent, context: HandlerContext) -> HandlingResult:
        raise NotImplementedError
