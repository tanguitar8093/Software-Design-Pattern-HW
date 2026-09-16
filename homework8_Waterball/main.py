import json
import sys
from pathlib import Path
from typing import Any, List, Optional

# 確保可以直接以 python main.py 執行時找到套件
workspace_dir = Path(__file__).resolve().parent.parent
if str(workspace_dir) not in sys.path:
    sys.path.insert(0, str(workspace_dir))

from homework8_Waterball.v1.bot import BotFacade
from homework8_Waterball.v1.common import Role
from homework8_Waterball.v1.domain import Member, Post, WaterballCommunity


class CommunitySimulationDriver:
    """
    應用層事件驅動器 (Application Layer Driver / CLI Entrypoint):
    負責將 README 規範的 JSON 字串輸入，映射調用對應的領域頻道與 BotFacade。
    使用 Handler 查表分派 (Table-Driven Dispatcher)，消除冗長且重複的 if-else 階梯。
    注意：此處為單純的 I/O 驅動器與反序列化，非 GoF 轉接器模式 (Adapter Pattern)。
    """
    def __init__(self, output_sink: Optional[List[str]] = None):
        self.output_sink: List[str] = output_sink if output_sink is not None else []
        self.community: Optional[WaterballCommunity] = None
        self.bot: Optional[Any] = None

        # 事件名稱與對應處理函式對映表 (查表法符合 OCP)
        self._handlers = {
            "started": self._handle_started,
            "login": self._handle_login,
            "logout": self._handle_logout,
            "new message": self._handle_new_message,
            "new post": self._handle_new_post,
            "go broadcasting": self._handle_go_broadcasting,
            "speak": self._handle_speak,
            "stop broadcasting": self._handle_stop_broadcasting,
        }

    def execute_line(self, raw_line: str) -> None:
        line = raw_line.strip()
        if not line or line == "[end]":
            return

        # 1. 時間流逝事件：[<n> <time-unit> elapsed]
        if "elapsed" in line:
            self._handle_elapsed(line)
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

    def _handle_started(self, payload: dict) -> None:
        initial_time = payload.get("time", "2023-08-07 00:00:00")
        quota = payload.get("quota", 10)
        self.community = WaterballCommunity(initialTime=initial_time, output_sink=self.output_sink)
        facade = BotFacade.create(quota=quota)
        self.bot = facade.buildDefaultBot(self.community)

    def _handle_login(self, payload: dict) -> None:
        if self.community is None:
            return
        user_id = str(payload.get("userId"))
        role = Role.ADMIN if payload.get("isAdmin", False) else Role.MEMBER
        self.community.login(Member(id=user_id, role=role))

    def _handle_logout(self, payload: dict) -> None:
        if self.community is None:
            return
        self.community.logout(str(payload.get("userId")))

    def _handle_new_message(self, payload: dict) -> None:
        if self.community is None:
            return
        member = self.community.getMember(str(payload.get("authorId")))
        if member is not None:
            member.sendMessage(self.community.chatRoom, payload.get("content", ""), payload.get("tags", []))

    def _handle_new_post(self, payload: dict) -> None:
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

    def _handle_go_broadcasting(self, payload: dict) -> None:
        if self.community is None:
            return
        member = self.community.getMember(str(payload.get("speakerId")))
        if member is not None:
            member.startBroadcast(self.community.broadcast)

    def _handle_speak(self, payload: dict) -> None:
        if self.community is None:
            return
        member = self.community.getMember(str(payload.get("speakerId")))
        if member is not None:
            member.speak(self.community.broadcast, payload.get("content", ""))

    def _handle_stop_broadcasting(self, payload: dict) -> None:
        if self.community is None:
            return
        member = self.community.getMember(str(payload.get("speakerId")))
        if member is not None:
            member.stopBroadcast(self.community.broadcast)

    def _handle_elapsed(self, line: str) -> None:
        if self.community is None:
            return
        inner = line[1:-1].strip()
        parts = inner.split()
        amount = int(parts[0])
        unit = parts[1]
        self.community.elapseTime(amount, unit)


def run_simulation(input_lines: List[str]) -> List[str]:
    """
    應用層主模擬器：建立驅動器批次執行所有輸入行並回傳結果清單
    """
    output_lines: List[str] = []
    driver = CommunitySimulationDriver(output_sink=output_lines)
    for line in input_lines:
        if line.strip() == "[end]":
            break
        driver.execute_line(line)
    return output_lines


if __name__ == "__main__":
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
        driver = CommunitySimulationDriver(output_sink=output_buffer)
        print("=== Waterball 互動式模擬環境已啟動 (輸入 [end] 結束) ===")

        while True:
            try:
                line = input().strip()
            except EOFError:
                break

            if not line:
                continue
            if line == "[end]":
                print("=== 模擬結束 ===")
                break

            prev_len = len(output_buffer)
            driver.execute_line(line)

            for item in output_buffer[prev_len:]:
                print(item)
