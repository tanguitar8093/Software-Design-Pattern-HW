from __future__ import annotations
from typing import List, Optional
from ..common.events import OnlineChangedEvent, TimeElapsedEvent
from ..common.observer import Observable
from .channels.broadcast import Broadcast
from .channels.chat_room import ChatRoom
from .channels.forum import Forum
from .member import Member, Participant


class WaterballCommunity(Observable):
    def __init__(self, initialTime: str = "2023-08-07 00:00:00", output_sink: Optional[List[str]] = None):
        super().__init__()
        self.currentTime: str = initialTime
        self.chatRoom: ChatRoom = ChatRoom(output_sink)
        self.forum: Forum = Forum(output_sink)
        self.broadcast: Broadcast = Broadcast(output_sink)
        self._onlineParticipants: List[Participant] = []
        self._membersMap: dict[str, Member] = {}
        self._output_sink: List[str] = output_sink if output_sink is not None else []

    def setOutputSink(self, sink: List[str]) -> None:
        self._output_sink = sink
        self.chatRoom.setOutputSink(sink)
        self.forum.setOutputSink(sink)
        self.broadcast.setOutputSink(sink)

    def login(self, participant: Participant) -> None:
        if participant not in self._onlineParticipants:
            self._onlineParticipants.append(participant)
        if isinstance(participant, Member):
            self._membersMap[participant.id] = participant
        self.notify(OnlineChangedEvent(len(self._onlineParticipants)))

    def logout(self, participantId: str) -> None:
        self._onlineParticipants = [p for p in self._onlineParticipants if p.id != participantId]
        self.notify(OnlineChangedEvent(len(self._onlineParticipants)))

    def elapseTime(self, amount: int, unit: str) -> None:
        self._output_sink.append(f"🕑 {amount} {unit} elapsed...")
        seconds = amount
        if unit == "minutes":
            seconds = amount * 60
        elif unit == "hours":
            seconds = amount * 3600
        self.notify(TimeElapsedEvent(seconds))

    def getOnlineParticipants(self) -> List[Participant]:
        return list(self._onlineParticipants)

    def getOnlineCount(self) -> int:
        return len(self._onlineParticipants)

    def getMember(self, memberId: str) -> Optional[Member]:
        return self._membersMap.get(memberId)
