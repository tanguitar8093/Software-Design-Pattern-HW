from enum import Enum


class InputEventType(Enum):
    """README 定義的 CLI 輸入事件；UNKNOWN 保留未定義事件供後續處理。"""

    STARTED = "started"
    LOGIN = "login"
    LOGOUT = "logout"
    ELAPSED = "elapsed"
    NEW_MESSAGE = "new message"
    NEW_POST = "new post"
    GO_BROADCASTING = "go broadcasting"
    SPEAK = "speak"
    STOP_BROADCASTING = "stop broadcasting"
    END = "end"
    UNKNOWN = "unknown"
