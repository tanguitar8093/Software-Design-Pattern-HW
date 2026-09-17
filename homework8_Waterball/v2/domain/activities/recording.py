from __future__ import annotations
from typing import List
from ..channels.broadcast import VoiceMessage


class RecordingSession:
    def __init__(self, recorderId: str):
        self.recorderId: str = recorderId
        self._voices: List[VoiceMessage] = []

    def addVoice(self, message: VoiceMessage) -> None:
        self._voices.append(message)

    def generateReplay(self) -> str:
        content = "\n".join([v.content for v in self._voices])
        return f"[Record Replay] {content}"
