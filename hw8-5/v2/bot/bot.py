from datetime import datetime as DateTime
from typing import Optional

from ..community.community import Participant, WaterCommunity
from ..events.domain_events import DomainEvent
from ..events.publisher import CommunityObserver
from ..fsm.core import FiniteStateMachine


class Bot(CommunityObserver):
    def __init__(
        self,
        community: WaterCommunity,
        quota: int,
        description: str,
        rootFsm: FiniteStateMachine,
        id: str = "bot",
    ):
        self.id = id
        self.quota = quota
        self.description = description
        self.rootFsm = rootFsm
        self.recorderId: Optional[str] = None  # 目前這輪錄音的錄音者（下 record 指令的人），跨廣播週期不變
        self._community = community  # 全委派型：Bot 不持有 ChatRoom/Forum/Broadcast，一律透過 WaterCommunity 代理
        community.getEventPublisher().register(self)

    def getId(self) -> str:
        return self.id

    def onEvent(self, event: DomainEvent) -> None:
        # leaf state 的 fire() 先處理原地反應並回傳 False，讓外層 FSM 接著檢查轉移。
        self.rootFsm.fire(event)

    def getOnlineParticipantIds(self) -> list[str]:
        return [self.id] + [participant.id for participant in self._community.getOnlineParticipants()]

    def replyChatMessage(self, content: str, tags: list[str]) -> None:
        self._community.postBotReply(content, tags)

    def commentPost(self, postId: str, content: str, tags: list[str]) -> None:
        self._community.postBotComment(postId, content, tags)

    def broadcastVoice(self, content: str) -> None:
        self._community.postBotVoice(content)

    def getOnlineCount(self) -> int:
        return self._community.getOnlineCount() + 1  # 在線人數計算包含機器人自己（README 明定）

    def isBroadcasting(self) -> bool:
        return self._community.isBroadcasting()

    def getParticipant(self, participantId: str) -> Optional[Participant]:
        return self._community.getParticipant(participantId)

    def getCurrentTime(self) -> DateTime:
        return self._community.currentTime
