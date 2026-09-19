from dataclasses import dataclass
from typing import Optional


@dataclass
class VoiceMessage:
    speaker_id: str
    content: str


class Broadcast:
    """對應 OOA-Clean.mmd Broadcast：把關麥克風獨佔權，並於上麥/發言/下麥時通報 Bot。"""

    def __init__(self) -> None:
        self.bot: Optional["Bot"] = None  # noqa: F821 (由 WaterballCommunity 組裝時注入)
        self.current_speaker_id: Optional[str] = None

    def start(self, speaker_id: str) -> None:
        self.current_speaker_id = speaker_id
        if speaker_id == "bot":
            print("🤖 go broadcasting...")
        else:
            print(f"📢 {speaker_id} is broadcasting...")
        self.bot.on_broadcast_started(speaker_id)

    def speak(self, voice_message: VoiceMessage) -> None:
        if voice_message.speaker_id == "bot":
            print(f"🤖 speaking: {voice_message.content}")
        else:
            print(f"📢 {voice_message.speaker_id}: {voice_message.content}")
        self.bot.on_voice_spoken(voice_message)

    def stop(self, speaker_id: str) -> None:
        self.current_speaker_id = None
        if speaker_id == "bot":
            print("🤖 stop broadcasting...")
        else:
            print(f"📢 {speaker_id} stop broadcasting")
        self.bot.on_broadcast_stopped(speaker_id)

    def is_broadcasting(self) -> bool:
        return self.current_speaker_id is not None
