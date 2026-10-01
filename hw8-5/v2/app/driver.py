from typing import Optional

from ..bot.bot import Bot
from ..community.community import WaterCommunity
from .event_line_parser import parseLine
from .handler_chain import build_handler_chain
from .handler_context import HandlerContext
from .handlers.base import EventHandler, HandlingResult


class AppDriver:
    """讀取輸入行並交給可替換的事件處理鏈；不再負責各事件的社群操作。"""

    def __init__(self, output: Optional[list[str]] = None, handler_chain: Optional[EventHandler] = None):
        self._context = HandlerContext(output if output is not None else [])
        self._handler_chain = handler_chain if handler_chain is not None else build_handler_chain()

    @property
    def output(self) -> list[str]:
        return self._context.output

    @property
    def community(self) -> Optional[WaterCommunity]:
        return self._context.community

    @property
    def bot(self) -> Optional[Bot]:
        return self._context.bot

    def run(self, lines: list[str]) -> list[str]:
        for raw_line in lines:
            parsed = parseLine(raw_line)
            if parsed is None:
                continue
            if self._handler_chain.handle(parsed, self._context) is HandlingResult.STOP:
                break
        return self.output
