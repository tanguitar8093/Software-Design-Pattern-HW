import importlib
import json
import sys
from pathlib import Path
from typing import Any, List, Optional

# 當直接以 `python main.py` 執行或以 `import main` 匯入時，Python 的 __package__ 為 None 或空字串。
# 為了讓套件內部的相對 import (如 .bot, ..common) 均能自動正確生效，
# 動態取得所在目錄名稱並向 sys.path 及 sys.modules 註冊套件。
if not __package__:
    pkg_dir = Path(__file__).resolve().parent
    pkg_parent = pkg_dir.parent
    if str(pkg_parent) not in sys.path:
        sys.path.insert(0, str(pkg_parent))
    __package__ = pkg_dir.name
    importlib.import_module(pkg_dir.name)

from .bot import Bot, BotFacade
from .common import Role, TimeUnit
from .domain import Member, Post, WaterballCommunity


class Client:
    """
    應用層客戶端驅動器 (Application Layer Client):
    依據 OODv5-1.mmd 規格，負責解析輸入事件，協同領域頻道與 BotFacade 進行社群模擬。
    """
    def __init__(self, outputSink: Optional[List[str]] = None):
        self.outputSink: List[str] = outputSink if outputSink is not None else []
        self.community: Optional[WaterballCommunity] = None
        self.bot: Optional[Bot] = None

        self._handlers = {
            "started": self._handleStarted,
            "login": self._handleLogin,
            "logout": self._handleLogout,
            "new message": self._handleNewMessage,
            "new post": self._handleNewPost,
            "go broadcasting": self._handleGoBroadcasting,
            "speak": self._handleSpeak,
            "stop broadcasting": self._handleStopBroadcasting,
        }

    def run(self, inputLines: List[str]) -> List[str]:
        for line in inputLines:
            if line.strip() == "[end]":
                break
            self.executeLine(line)
        return self.outputSink

    def executeLine(self, rawLine: str) -> None:
        line = rawLine.strip()
        if not line or line == "[end]":
            return

        # 1. 時間流逝事件：[<n> <time-unit> elapsed]
        if "elapsed" in line:
            inner = line[1:-1].strip()
            parts = inner.split()
            amount = int(parts[0])
            unit_str = parts[1]
            unit = TimeUnit(unit_str) if unit_str in TimeUnit._value2member_map_ else TimeUnit.SECONDS
            self._handleElapsed(amount, unit)
            return

        # 2. JSON 事件格式：[<event_name>] <payload>
        idx = line.find("]")
        if idx == -1:
            return

        event_name = line[1:idx].strip()
        payload_str = line[idx + 1:].strip()
        payload = json.loads(payload_str) if payload_str else {}

        handler = self._handlers.get(event_name)
        if handler:
            handler(payload)

    execute_line = executeLine

    def _handleStarted(self, payload: dict) -> None:
        initial_time = payload.get("time", "2023-08-07 00:00:00")
        quota = payload.get("quota", 10)
        self.community = WaterballCommunity(initialTime=initial_time, output_sink=self.outputSink)
        self.bot = BotFacade.createDefaultBot(self.community, quota=quota)

    def _handleLogin(self, payload: dict) -> None:
        if self.community is None:
            return
        user_id = str(payload.get("userId"))
        role = Role.ADMIN if payload.get("isAdmin", False) else Role.MEMBER
        self.community.login(Member(id=user_id, role=role))

    def _handleLogout(self, payload: dict) -> None:
        if self.community is None:
            return
        self.community.logout(str(payload.get("userId")))

    def _handleNewMessage(self, payload: dict) -> None:
        if self.community is None:
            return
        member = self.community.getMember(str(payload.get("authorId")))
        if member is not None:
            member.sendMessage(self.community.chatRoom, payload.get("content", ""), payload.get("tags", []))

    def _handleNewPost(self, payload: dict) -> None:
        if self.community is None:
            return
        post = Post(
            id=str(payload.get("id")),
            authorId=str(payload.get("authorId")),
            title=payload.get("title", ""),
            content=payload.get("content", ""),
            tags=payload.get("tags", []),
        )
        self.community.forum.createPost(post)

    def _handleGoBroadcasting(self, payload: dict) -> None:
        if self.community is None:
            return
        member = self.community.getMember(str(payload.get("speakerId")))
        if member is not None:
            member.startBroadcast(self.community.broadcast)

    def _handleSpeak(self, payload: dict) -> None:
        if self.community is None:
            return
        member = self.community.getMember(str(payload.get("speakerId")))
        if member is not None:
            member.speak(self.community.broadcast, payload.get("content", ""))

    def _handleStopBroadcasting(self, payload: dict) -> None:
        if self.community is None:
            return
        member = self.community.getMember(str(payload.get("speakerId")))
        if member is not None:
            member.stopBroadcast(self.community.broadcast)

    def _handleElapsed(self, amount: int, unit: TimeUnit) -> None:
        if self.community is None:
            return
        self.community.elapseTime(amount, unit.value)


# 相容別名
CommunitySimulationDriver = Client


def run_simulation(input_lines: List[str]) -> List[str]:
    """
    應用層主模擬器：建立 Client 執行批次輸入行並回傳結果清單
    """
    output_lines: List[str] = []
    client = Client(outputSink=output_lines)
    return client.run(input_lines)


def main() -> None:
    # 1. 檔案參數模式（例如：python main.py input.txt）
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            for out in run_simulation(f.readlines()):
                print(out)

    # 2. 管道串接模式（例如：cat input.txt | python main.py）
    elif not sys.stdin.isatty():
        for out in run_simulation(sys.stdin.readlines()):
            print(out)

    # 3. 終端機手動即時互動模式（REPL）
    else:
        output_buffer: List[str] = []
        client = Client(outputSink=output_buffer)
        print("=== Waterball 互動式模擬環境已啟動 (輸入 [end] 結束) ===")

        while True:
            try:
                line = input()
                if line.strip() == "[end]":
                    break
                before_len = len(output_buffer)
                client.executeLine(line)
                for out in output_buffer[before_len:]:
                    print(out)
            except EOFError:
                break


if __name__ == "__main__":
    main()
