from datetime import datetime, timedelta
from typing import Dict, List, Optional

from .bot import Bot
from .broadcast import Broadcast
from .chat_room import ChatRoom
from .forum import Forum
from .member import Member

_UNIT_SECONDS = {"seconds": 1, "minutes": 60, "hours": 3600}


class WaterballCommunity:
    """對應 OOA-Clean.mmd WaterballCommunity：組裝各頻道與 Bot，維護在線名冊並推進時間。"""

    def __init__(self, current_time: datetime, quota: int) -> None:
        self.current_time = current_time
        self.chat_room = ChatRoom()
        self.forum = Forum()
        self.broadcast = Broadcast()
        self.bot = Bot(quota, self)
        self.bot.bind_channels(self.chat_room, self.forum, self.broadcast)
        self.chat_room.bot = self.bot
        self.forum.bot = self.bot
        self.broadcast.bot = self.bot

        self._members: Dict[str, Member] = {}
        self._member_order: List[str] = []

    def login(self, member: Member) -> None:
        self._members[member.id] = member
        self._member_order.append(member.id)
        self.bot.on_participant_logged_in()

    def logout(self, participant_id: str) -> None:
        if participant_id in self._members:
            del self._members[participant_id]
            self._member_order.remove(participant_id)
        self.bot.on_participant_logged_out()

    def elapse_time(self, amount: int, unit: str) -> None:
        print(f"🕑 {amount} {unit} elapsed...")
        self.current_time += timedelta(seconds=amount * _UNIT_SECONDS[unit])
        self.bot.on_time_elapsed(amount * _UNIT_SECONDS[unit])

    def get_online_count(self) -> int:
        return len(self._members) + 1  # +1 為常駐的 Bot

    def get_online_member_ids(self) -> List[str]:
        return list(self._member_order)

    def get_member(self, member_id: str) -> Optional[Member]:
        return self._members.get(member_id)
