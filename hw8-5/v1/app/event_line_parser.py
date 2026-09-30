import json
from dataclasses import dataclass
from typing import Optional

from .event_type import InputEventType


@dataclass
class ParsedEvent:
    name: InputEventType
    payload: dict
    rawName: Optional[str] = None  # 未知事件保留原名稱，未來可交給 fallback handler。


def parseLine(rawLine: str) -> Optional[ParsedEvent]:
    """把一行輸入轉成 (事件名稱, payload)；空行回傳 None。"""
    line = rawLine.strip()
    if not line:
        return None
    if line == f"[{InputEventType.END.value}]":
        return ParsedEvent(InputEventType.END, {})
    if line.startswith("[") and line.endswith(f"{InputEventType.ELAPSED.value}]"):
        amount, unit, _ = line[1:-1].strip().split(maxsplit=2)
        return ParsedEvent(InputEventType.ELAPSED, {"amount": int(amount), "unit": unit})

    endIdx = line.find("]")
    if endIdx == -1:
        return None
    name = line[1:endIdx].strip()
    payloadStr = line[endIdx + 1 :].strip()
    payload = json.loads(payloadStr) if payloadStr else {}
    try:
        eventType = InputEventType(name)
    except ValueError:
        return ParsedEvent(InputEventType.UNKNOWN, payload, rawName=name)
    if eventType is InputEventType.UNKNOWN:
        return ParsedEvent(eventType, payload, rawName=name)
    return ParsedEvent(eventType, payload)
