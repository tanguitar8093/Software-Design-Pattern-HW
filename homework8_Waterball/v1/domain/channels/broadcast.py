from __future__ import annotations
from typing import List, Optional
from homework8_Waterball.v1.common.events import (
    BroadcastStartedEvent,
    BroadcastStoppedEvent,
    VoiceSpokenEvent,
)
from homework8_Waterball.v1.common.observer import Observable


class VoiceMessage:
    def __init__(self, speakerId: str, content: str):
        self.speakerId: str = speakerId
        self.content: str = content


class Broadcast(Observable):
    def __init__(self, output_sink: Optional[List[str]] = None):
        super().__init__()
        self.currentSpeakerId: Optional[str] = None
        self._output_sink: List[str] = output_sink if output_sink is not None else []

    def setOutputSink(self, sink: List[str]) -> None:
        self._output_sink = sink

    def isBroadcasting(self) -> bool:
        return self.currentSpeakerId is not None

    def start(self, speakerId: str) -> None:
        self.currentSpeakerId = speakerId
        if speakerId == "bot":
            self._output_sink.append("🤖 go broadcasting...")
        else:
            self._output_sink.append(f"📢 {speakerId} is broadcasting...")
        self.notify(BroadcastStartedEvent(speakerId))

    def speak(self, voiceMessage: VoiceMessage) -> None:
        if voiceMessage.speakerId == "bot":
            self._output_sink.append(f"🤖 speaking: {voiceMessage.content}")
        else:
            self._output_sink.append(f"📢 {voiceMessage.speakerId}: {voiceMessage.content}")
        self.notify(VoiceSpokenEvent(voiceMessage))

    def stop(self, speakerId: str) -> None:
        if self.currentSpeakerId == speakerId:
            self.currentSpeakerId = None
            if speakerId == "bot":
                self._output_sink.append("🤖 stop broadcasting...")
            else:
                self._output_sink.append(f"📢 {speakerId} stop broadcasting")
            self.notify(BroadcastStoppedEvent(speakerId))
