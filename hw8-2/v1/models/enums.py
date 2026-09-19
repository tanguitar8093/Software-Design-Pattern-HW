from enum import Enum, auto


class Role(Enum):
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"


class BotState(Enum):
    """對應 OOA-Clean.mmd：v1 尚未抽出 BotState 類別，僅以列舉表達 Bot 內部狀態欄位。"""

    NORMAL_DEFAULT = auto()
    NORMAL_INTERACTING = auto()
    RECORD_WAITING = auto()
    RECORD_RECORDING = auto()
    KING_QUESTIONING = auto()
    KING_THANKS = auto()
