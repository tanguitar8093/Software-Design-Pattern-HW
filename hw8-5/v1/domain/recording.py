from ..community.channels import VoiceMessage


class RecordingSession:
    def __init__(self, recorderId: str):
        self.recorderId = recorderId

    def addVoice(self, message: VoiceMessage) -> None:
        raise NotImplementedError

    def generateReplay(self) -> str:
        raise NotImplementedError
