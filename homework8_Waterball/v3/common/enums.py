from enum import Enum


class Role(Enum):
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"


class TimeUnit(Enum):
    SECONDS = "seconds"
    MINUTES = "minutes"
    HOURS = "hours"


class CommunityEventType(Enum):
    MESSAGE_RECEIVED = "MESSAGE_RECEIVED"
    POST_PUBLISHED = "POST_PUBLISHED"
    BROADCAST_STARTED = "BROADCAST_STARTED"
    VOICE_SPOKEN = "VOICE_SPOKEN"
    BROADCAST_STOPPED = "BROADCAST_STOPPED"
    TIME_ELAPSED = "TIME_ELAPSED"
    ONLINE_CHANGED = "ONLINE_CHANGED"
