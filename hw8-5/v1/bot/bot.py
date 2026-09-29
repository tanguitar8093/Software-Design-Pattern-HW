from datetime import datetime as DateTime
from typing import Optional

from ..community.community import Participant, WaterCommunity
from ..events.domain_events import DomainEvent
from ..events.publisher import CommunityObserver
from ..fsm.core import FiniteStateMachine, StateNode
from .internal_reaction import InternalReaction


class Bot(CommunityObserver):
    def __init__(
        self,
        community: WaterCommunity,
        quota: int,
        description: str,
        rootFsm: FiniteStateMachine,
        id: str = "bot",
        internalReactions: Optional[list[InternalReaction]] = None,
    ):
        self.id = id
        self.quota = quota
        self.description = description
        self.rootFsm = rootFsm
        self._community = community  # 全委派型：Bot 不持有 ChatRoom/Forum/Broadcast，一律透過 WaterCommunity 代理
        self._internalReactions = internalReactions or []
        community.getEventPublisher().register(self)

    def getId(self) -> str:
        return self.id

    def addInternalReaction(self, reaction: InternalReaction) -> None:
        self._internalReactions.append(reaction)

    def onEvent(self, event: DomainEvent) -> None:
        self.rootFsm.fire(event)
        activeLeafState = self._getActiveLeafState()
        for reaction in self._internalReactions:
            if reaction.isApplicable(activeLeafState, event):
                reaction.action.execute(event)

    def _getActiveLeafState(self) -> Optional[StateNode]:
        node: Optional[StateNode] = self.rootFsm
        while isinstance(node, FiniteStateMachine):
            node = node.currentState
        return node

    def replyChatMessage(self, content: str, tags: list[str]) -> None:
        self._community.postBotReply(content, tags)

    def commentPost(self, postId: str, content: str, tags: list[str]) -> None:
        self._community.postBotComment(postId, content, tags)

    def broadcastVoice(self, content: str) -> None:
        self._community.postBotVoice(content)

    def getOnlineCount(self) -> int:
        return self._community.getOnlineCount()

    def isBroadcasting(self) -> bool:
        return self._community.isBroadcasting()

    def getParticipant(self, participantId: str) -> Optional[Participant]:
        return self._community.getParticipant(participantId)

    def getCurrentTime(self) -> DateTime:
        return self._community.currentTime
