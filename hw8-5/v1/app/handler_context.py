from dataclasses import dataclass
from typing import Optional

from ..bot.bot import Bot
from ..community.community import WaterCommunity


@dataclass
class HandlerContext:
    """供整條輸入事件責任鏈共享的執行狀態。"""

    output: list[str]
    community: Optional[WaterCommunity] = None
    bot: Optional[Bot] = None
