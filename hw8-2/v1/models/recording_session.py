from typing import List

from .broadcast import VoiceMessage


class RecordingSession:
    """對應 OOA-Clean.mmd RecordingSession：暫存講者語音，結束時組成換行 Replay 文稿。"""

    def __init__(self, recorder_id: str) -> None:
        self.recorder_id = recorder_id
        self._voices: List[str] = []

    def add_voice(self, message: VoiceMessage) -> None:
        self._voices.append(message.content)

    def generate_replay(self) -> str:
        content = "[Record Replay] " + "\n".join(self._voices)
        self._voices = []
        return content
