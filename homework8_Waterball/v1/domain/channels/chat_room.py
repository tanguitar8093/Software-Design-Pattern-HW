from __future__ import annotations
from typing import List, Optional
from homework8_Waterball.v1.common.events import MessageReceivedEvent
from homework8_Waterball.v1.common.observer import Observable


class Message:
    def __init__(self, authorId: str, content: str, tags: Optional[List[str]] = None):
        self.authorId: str = authorId
        self.content: str = content
        self.tags: List[str] = tags if tags is not None else []


class ChatRoom(Observable):
    def __init__(self, output_sink: Optional[List[str]] = None):
        super().__init__()
        self._output_sink: List[str] = output_sink if output_sink is not None else []

    def setOutputSink(self, sink: List[str]) -> None:
        self._output_sink = sink

    def postMessage(self, message: Message) -> None:
        tags_str = ""
        if message.tags:
            tags_str = " " + ", ".join([f"@{t}" for t in message.tags])

        # 機器人發言與一般成員發言輸出格式
        if message.authorId == "bot":
            # 判斷是否為題目的選項行（如 A) ..., B) ..., C) ..., D) ...）
            is_option_line = len(message.content) >= 3 and message.content[0] in "ABCD" and message.content[1] == ")"
            if is_option_line:
                self._output_sink.append(f"{message.content}{tags_str}")
            elif "\n" in message.content:
                # 處理多行訊息（例如 Record Replay）
                lines = message.content.split("\n")
                for i, l in enumerate(lines):
                    if i == 0:
                        self._output_sink.append(f"🤖: {l}")
                    elif i == len(lines) - 1:
                        self._output_sink.append(f"{l}{tags_str}")
                    else:
                        self._output_sink.append(l)
            else:
                self._output_sink.append(f"🤖: {message.content}{tags_str}")
        else:
            self._output_sink.append(f"💬 {message.authorId}: {message.content}{tags_str}")

        # 推播事件通知所有 Observer (Bot)
        self.notify(MessageReceivedEvent(message))
