import json
from typing import List
from homework8_Waterball.v1.community import Member, Post, Role, WaterballCommunity
from homework8_Waterball.v1.facade import BotFacade


def run_simulation(input_lines: List[str]) -> List[str]:
    """
    應用層主模擬器：
    讀取 JSON 格式事件串流，透過 BotFacade 建立機器人，驅動社群運作並回傳所有輸出行。
    """
    output_lines: List[str] = []
    community: WaterballCommunity = None
    bot = None

    for raw_line in input_lines:
        line = raw_line.strip()
        if not line:
            continue

        if line == "[end]":
            break

        # 1. 時間流逝事件：[<n> <time-unit> elapsed]
        if "elapsed" in line:
            # 格式：[<n> <time-unit> elapsed]
            inner = line[1:-1].strip()
            parts = inner.split()
            amount = int(parts[0])
            unit = parts[1]
            if community is not None:
                community.elapseTime(amount, unit)
            continue

        # 2. JSON 格式事件：[<event's name>] <payload in JSON format>
        idx = line.find("]")
        if idx == -1:
            continue

        event_name = line[1:idx].strip()
        payload_str = line[idx + 1:].strip()
        payload = json.loads(payload_str) if payload_str else {}

        if event_name == "started":
            initial_time = payload.get("time", "2023-08-07 00:00:00")
            quota = payload.get("quota", 10)
            community = WaterballCommunity(initialTime=initial_time, output_sink=output_lines)
            facade = BotFacade.create(quota=quota)
            bot = facade.buildDefaultBot(community)

        elif event_name == "login":
            user_id = str(payload.get("userId"))
            is_admin = payload.get("isAdmin", False)
            role = Role.ADMIN if is_admin else Role.MEMBER
            member = Member(id=user_id, role=role)
            if community is not None:
                community.login(member)

        elif event_name == "logout":
            user_id = str(payload.get("userId"))
            if community is not None:
                community.logout(user_id)

        elif event_name == "new message":
            author_id = str(payload.get("authorId"))
            content = payload.get("content", "")
            tags = payload.get("tags", [])
            if community is not None:
                member = community.getMember(author_id)
                if member is not None:
                    member.sendMessage(community.chatRoom, content, tags)

        elif event_name == "new post":
            post_id = str(payload.get("id"))
            author_id = str(payload.get("authorId"))
            title = payload.get("title", "")
            content = payload.get("content", "")
            tags = payload.get("tags", [])
            post = Post(id=post_id, authorId=author_id, title=title, content=content, tags=tags)
            if community is not None:
                community.forum.createPost(post)

        elif event_name == "go broadcasting":
            speaker_id = str(payload.get("speakerId"))
            if community is not None:
                member = community.getMember(speaker_id)
                if member is not None:
                    member.startBroadcast(community.broadcast)

        elif event_name == "speak":
            speaker_id = str(payload.get("speakerId"))
            content = payload.get("content", "")
            if community is not None:
                member = community.getMember(speaker_id)
                if member is not None:
                    member.speak(community.broadcast, content)

        elif event_name == "stop broadcasting":
            speaker_id = str(payload.get("speakerId"))
            if community is not None:
                member = community.getMember(speaker_id)
                if member is not None:
                    member.stopBroadcast(community.broadcast)

    return output_lines
