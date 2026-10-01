from ..community.channels import VoiceMessage


class RecordingSession:
    def __init__(self, recorderId: str):
        self.recorderId = recorderId
        self._voices: list[VoiceMessage] = []  # 圖上沒畫，但 addVoice/generateReplay 缺一不可的內部緩衝

    def addVoice(self, message: VoiceMessage) -> None:
        self._voices.append(message)

    def generateReplay(self) -> str:
        return "\n".join(voice.content for voice in self._voices)
