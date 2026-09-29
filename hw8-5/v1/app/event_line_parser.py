import json
from dataclasses import dataclass
from typing import Optional


@dataclass
class ParsedEvent:
    name: str
    payload: dict


def parseLine(rawLine: str) -> Optional[ParsedEvent]:
    """把一行輸入轉成 (事件名稱, payload)；空行回傳 None。"""
    line = rawLine.strip()
    if not line:
        return None
    if line == "[end]":
        return ParsedEvent("end", {})
    if line.startswith("[") and line.endswith("elapsed]"):
        amount, unit, _ = line[1:-1].strip().split(maxsplit=2)
        return ParsedEvent("elapsed", {"amount": int(amount), "unit": unit})

    endIdx = line.find("]")
    if endIdx == -1:
        return None
    name = line[1:endIdx].strip()
    payloadStr = line[endIdx + 1 :].strip()
    payload = json.loads(payloadStr) if payloadStr else {}
    return ParsedEvent(name, payload)
