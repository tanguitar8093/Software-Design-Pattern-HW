import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Iterable

sys.path.insert(0, str(Path(__file__).resolve().parent))

from models.community import WaterballCommunity
from models.enums import Role
from models.member import Member

_ELAPSED_PATTERN = re.compile(r"^\[(\d+)\s+(seconds|minutes|hours)\s+elapsed\]$")
_EVENT_PATTERN = re.compile(r"^\[([^\]]+)\]\s*(.*)$")


def run(lines: Iterable[str]) -> None:
    community: WaterballCommunity = None

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        if line == "[end]":
            break

        elapsed_match = _ELAPSED_PATTERN.match(line)
        if elapsed_match:
            amount, unit = int(elapsed_match.group(1)), elapsed_match.group(2)
            community.elapse_time(amount, unit)
            continue

        event_match = _EVENT_PATTERN.match(line)
        if not event_match:
            continue
        event_name = event_match.group(1)
        payload_str = event_match.group(2).strip()
        payload = json.loads(payload_str) if payload_str else {}

        if event_name == "started":
            initial_time = datetime.strptime(payload["time"], "%Y-%m-%d %H:%M:%S")
            community = WaterballCommunity(initial_time, payload["quota"])
        elif event_name == "login":
            role = Role.ADMIN if payload.get("isAdmin") else Role.MEMBER
            community.login(Member(str(payload["userId"]), role))
        elif event_name == "logout":
            community.logout(str(payload["userId"]))
        elif event_name == "new message":
            member = community.get_member(str(payload["authorId"]))
            if member is not None:
                member.send_message(community.chat_room, payload.get("content", ""), payload.get("tags", []))
        elif event_name == "new post":
            member = community.get_member(str(payload["authorId"]))
            if member is not None:
                member.publish_post(
                    community.forum,
                    str(payload["id"]),
                    payload.get("title", ""),
                    payload.get("content", ""),
                    payload.get("tags", []),
                )
        elif event_name == "go broadcasting":
            member = community.get_member(str(payload["speakerId"]))
            if member is not None:
                member.start_broadcast(community.broadcast)
        elif event_name == "speak":
            member = community.get_member(str(payload["speakerId"]))
            if member is not None:
                member.speak(community.broadcast, payload.get("content", ""))
        elif event_name == "stop broadcasting":
            member = community.get_member(str(payload["speakerId"]))
            if member is not None:
                member.stop_broadcast(community.broadcast)


def main() -> None:
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            run(f.readlines())
    else:
        run(sys.stdin.readlines())


if __name__ == "__main__":
    main()
