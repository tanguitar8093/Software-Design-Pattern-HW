from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from ..common.enums import Role
from ..domain.activities import KnowledgeKingGame, RecordingSession
from ..domain.channels import Message
from ..domain.member import Member
from ..fsm import Trigger

if TYPE_CHECKING:
    from .bot import Bot


class BotCommand(ABC):
    @abstractmethod
    def canExecute(self, bot: Bot, member: Member, message: Message) -> bool:
        pass

    @abstractmethod
    def execute(self, bot: Bot, member: Member, message: Message) -> bool:
        pass


class AbstractBotCommand(BotCommand, ABC):
    def __init__(self, requiredQuota: int = 0, requiredRole: Role = Role.MEMBER):
        self.requiredQuota: int = requiredQuota
        self.requiredRole: Role = requiredRole

    def checkQuota(self, bot: Bot) -> bool:
        return bot.quota >= self.requiredQuota

    def checkPermission(self, member: Member) -> bool:
        if self.requiredRole == Role.ADMIN:
            return member.role == Role.ADMIN
        return True

    def canExecute(self, bot: Bot, member: Member, message: Message) -> bool:
        return self.checkQuota(bot) and self.checkPermission(member)

    def deductQuota(self, bot: Bot) -> None:
        bot.quota -= self.requiredQuota

    @abstractmethod
    def doExecute(self, bot: Bot, member: Member, message: Message) -> bool:
        pass

    def execute(self, bot: Bot, member: Member, message: Message) -> bool:
        if not self.canExecute(bot, member, message):
            return False
        self.deductQuota(bot)
        return self.doExecute(bot, member, message)


class KingCommand(AbstractBotCommand):
    def __init__(self):
        super().__init__(requiredQuota=5, requiredRole=Role.ADMIN)

    def doExecute(self, bot: Bot, member: Member, message: Message) -> bool:
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

    def canExecute(self, bot: Bot, member: Member, message: Message) -> bool:
        if not super().canExecute(bot, member, message):
            return False
        from .states import RecordState
        if bot._rootFsm is not None:
            curr = bot._rootFsm.getCurrentState()
            if isinstance(curr, RecordState) and curr.getSession() is not None:
                return curr.getSession().recorderId == member.id
        return False

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
