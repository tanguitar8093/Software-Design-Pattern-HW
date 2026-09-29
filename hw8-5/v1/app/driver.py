from datetime import datetime as DateTime
from typing import Callable, Optional

from ..bot.bot import Bot
from ..bot.facade import BotFacade
from ..community.community import Member, Role, WaterCommunity
from .event_line_parser import ParsedEvent, parseLine
from .transcript_observer import TranscriptObserver


class AppDriver:
    """應用層唯一入口：把輸入行轉呼叫 WaterCommunity/BotFacade，並用 TranscriptObserver 收集輸出。"""

    def __init__(self, output: Optional[list[str]] = None):
        self.output: list[str] = output if output is not None else []
        self.community: Optional[WaterCommunity] = None
        self.bot: Optional[Bot] = None
        self._handlers: dict[str, Callable[[dict], None]] = {
            "started": self._handleStarted,
            "login": self._handleLogin,
            "logout": self._handleLogout,
            "new message": self._handleNewMessage,
            "new post": self._handleNewPost,
            "go broadcasting": self._handleGoBroadcasting,
            "speak": self._handleSpeak,
            "stop broadcasting": self._handleStopBroadcasting,
        }

    def run(self, lines: list[str]) -> list[str]:
        for rawLine in lines:
            parsed = parseLine(rawLine)
            if parsed is None:
                continue
            if parsed.name == "end":
                break
            self._dispatch(parsed)
        return self.output

    def _dispatch(self, parsed: ParsedEvent) -> None:
        if parsed.name == "elapsed":
            self._handleElapsed(parsed.payload)
            return
        handler = self._handlers.get(parsed.name)
        if handler is not None:
            handler(parsed.payload)

    def _handleStarted(self, payload: dict) -> None:
        currentTime = DateTime.strptime(payload["time"], "%Y-%m-%d %H:%M:%S")
        self.community = WaterCommunity(currentTime)
        self.community.getEventPublisher().register(TranscriptObserver(self.output))
        facade = BotFacade(self.community, quota=payload.get("quota", 20))
        self.bot = facade.bot

    def _handleLogin(self, payload: dict) -> None:
        if self.community is None:
            return
        role = Role.ADMIN if payload.get("isAdmin", False) else Role.MEMBER
        self.community.login(Member(str(payload["userId"]), role))

    def _handleLogout(self, payload: dict) -> None:
        if self.community is None:
            return
        self.community.logout(str(payload["userId"]))

    def _handleElapsed(self, payload: dict) -> None:
        if self.community is None:
            return
        self.community.elapseTime(payload["amount"], payload["unit"])

    def _handleNewMessage(self, payload: dict) -> None:
        if self.community is None:
            return
        self.community.postMessage(str(payload["authorId"]), payload.get("content", ""), payload.get("tags", []))

    def _handleNewPost(self, payload: dict) -> None:
        if self.community is None:
            return
        self.community.createPost(
            str(payload["id"]),
            str(payload["authorId"]),
            payload.get("title", ""),
            payload.get("content", ""),
            payload.get("tags", []),
        )

    def _handleGoBroadcasting(self, payload: dict) -> None:
        if self.community is None:
            return
        self.community.startBroadcast(str(payload["speakerId"]))

    def _handleSpeak(self, payload: dict) -> None:
        if self.community is None:
            return
        self.community.speak(str(payload["speakerId"]), payload.get("content", ""))

    def _handleStopBroadcasting(self, payload: dict) -> None:
        if self.community is None:
            return
        self.community.stopBroadcast(str(payload["speakerId"]))
