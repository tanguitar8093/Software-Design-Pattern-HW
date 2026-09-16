from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from homework8_Waterball.v1.community import (
    KnowledgeKingGame,
    Member,
    Message,
    RecordingSession,
    Role,
)
from homework8_Waterball.v1.fsm import Trigger

if TYPE_CHECKING:
    from homework8_Waterball.v1.bot import Bot


class BotCommand(ABC):
    @abstractmethod
    def execute(self, bot: Bot, member: Member, message: Message) -> bool:
        pass


class AbstractBotCommand(BotCommand, ABC):
    """
    樣板方法模式 (Template Method Pattern):
    固化指令前置驗證管線：
    1. 驗證 Quota
    2. 驗證角色權限
    3. 扣除 Quota
    4. 執行具體指令業務 (doExecute)
    """
    def __init__(self, requiredQuota: int = 0, requiredRole: Role = Role.MEMBER):
        self.requiredQuota: int = requiredQuota
        self.requiredRole: Role = requiredRole

    def checkQuota(self, bot: Bot) -> bool:
        return bot.quota >= self.requiredQuota

    def checkPermission(self, member: Member) -> bool:
        if self.requiredRole == Role.ADMIN:
            return member.role == Role.ADMIN
        return True

    def deductQuota(self, bot: Bot) -> None:
        bot.quota -= self.requiredQuota

    @abstractmethod
    def doExecute(self, bot: Bot, member: Member, message: Message) -> bool:
        pass

    def execute(self, bot: Bot, member: Member, message: Message) -> bool:
        # 1. 額度不足 -> 靜默失敗
        if not self.checkQuota(bot):
            return False
        # 2. 權限不符 -> 靜默失敗
        if not self.checkPermission(member):
            return False
        # 3. 扣除額度
        self.deductQuota(bot)
        # 4. 具體業務
        return self.doExecute(bot, member, message)


class KingCommand(AbstractBotCommand):
    def __init__(self):
        super().__init__(requiredQuota=5, requiredRole=Role.ADMIN)

    def doExecute(self, bot: Bot, member: Member, message: Message) -> bool:
        # 建立/重設遊戲實例並觸發 FSM 轉移
        if bot._rootFsm is not None:
            trigger = Trigger("king", {"game": KnowledgeKingGame()})
            return bot._rootFsm.fire(trigger)
        return False


class RecordCommand(AbstractBotCommand):
    def __init__(self):
        super().__init__(requiredQuota=3, requiredRole=Role.MEMBER)

    def doExecute(self, bot: Bot, member: Member, message: Message) -> bool:
        session = RecordingSession(member.id)
        if bot._rootFsm is not None:
            trigger = Trigger("record", {"session": session})
            return bot._rootFsm.fire(trigger)
        return False


class StopRecordingCommand(AbstractBotCommand):
    def __init__(self):
        super().__init__(requiredQuota=0, requiredRole=Role.MEMBER)

    def checkPermission(self, member: Member) -> bool:
        # 特殊權限：只有發起錄音的 recorder 才能結束錄音
        # 錄音者資訊自 RecordState 的 session 檢查
        return True

    def doExecute(self, bot: Bot, member: Member, message: Message) -> bool:
        if bot._rootFsm is not None:
            trigger = Trigger("stop-recording", {"memberId": member.id})
            return bot._rootFsm.fire(trigger)
        return False


class KingStopCommand(AbstractBotCommand):
    def __init__(self):
        super().__init__(requiredQuota=0, requiredRole=Role.ADMIN)

    def doExecute(self, bot: Bot, member: Member, message: Message) -> bool:
        if bot._rootFsm is not None:
            trigger = Trigger("king-stop")
            return bot._rootFsm.fire(trigger)
        return False


class PlayAgainCommand(AbstractBotCommand):
    def __init__(self):
        super().__init__(requiredQuota=5, requiredRole=Role.MEMBER)

    def doExecute(self, bot: Bot, member: Member, message: Message) -> bool:
        if bot._rootFsm is not None:
            trigger = Trigger("play again", {"game": KnowledgeKingGame()})
            return bot._rootFsm.fire(trigger)
        return False
