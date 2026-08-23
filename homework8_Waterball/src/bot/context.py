from typing import List, Dict, Set
from ..domain.entities import Member

class BotContext:
    def __init__(self):
        self.members: Dict[str, Member] = {}
        self.online_users: Set[str] = set()
        self.quota: int = 0
        self.current_time_str: str = ""
        # You can store output messages here to print them out at the end, or print them directly
        self.speakers: Set[str] = set()
        self.recorded_messages: List[str] = []
        self.record_caller_id: str = ""
        
        # Used for default conversation
        self.default_conversation_messages = ["good to hear", "thank you", "How are you"]
        self.default_conv_idx = 0
        
        # Used for interaction conversation
        self.interacting_messages = ["Hi hi😁", "I like your idea!"]
        self.interacting_idx = 0

    def add_online_user(self, member: Member):
        self.members[member.id] = member
        self.online_users.add(member.id)
        
    def remove_online_user(self, user_id: str):
        if user_id in self.online_users:
            self.online_users.remove(user_id)
            
    def get_online_count(self) -> int:
        # Includes bot itself
        return len(self.online_users) + 1

