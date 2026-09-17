import pytest


def test_default_conversation_three_message_cycle():
    """
    測項說明：
    測試正常狀態下的「預設對話狀態」（在線人數 < 10，含機器人）：
    1. 當成員在聊天室傳遞訊息時，依序循環回覆三則訊息：
       第 1 則：good to hear @<發送者>
       第 2 則：thank you @<發送者>
       第 3 則：How are you @<發送者>
       第 4 則：回到第 1 則 good to hear @<發送者>
    2. 驗證標記發送者格式正確。
    """
    from main import run_simulation

    input_lines = [
        '[started] {"time": "2023-08-07 00:00:00", "quota": 10}',
        '[login] {"userId": "1", "isAdmin": false}',
        '[login] {"userId": "2", "isAdmin": false}',
        '[new message] {"authorId": "1", "content": "第一則訊息", "tags": []}',
        '[new message] {"authorId": "2", "content": "第二則訊息", "tags": []}',
        '[new message] {"authorId": "1", "content": "第三則訊息", "tags": []}',
        '[new message] {"authorId": "2", "content": "第四則訊息", "tags": []}',
        '[end]',
    ]
    expected_output = [
        "💬 1: 第一則訊息",
        "🤖: good to hear @1",
        "💬 2: 第二則訊息",
        "🤖: thank you @2",
        "💬 1: 第三則訊息",
        "🤖: How are you @1",
        "💬 2: 第四則訊息",
        "🤖: good to hear @2",
    ]
    actual_output = run_simulation(input_lines)
    assert actual_output == expected_output


def test_default_conversation_post_comment():
    """
    測項說明：
    測試「預設對話狀態」下的論壇貼文回覆：
    當成員在論壇發布貼文時，機器人在該貼文底下留言：
    🤖 comment in post <post id>: Nice post @<發文者Id>
    """
    from main import run_simulation

    input_lines = [
        '[started] {"time": "2023-08-07 00:00:00", "quota": 10}',
        '[login] {"userId": "1", "isAdmin": false}',
        '[new post] {"id": "101", "authorId": "1", "title": "測試標題", "content": "貼文內文", "tags": []}',
        '[end]',
    ]
    expected_output = [
        "1: 【測試標題】貼文內文",
        "🤖 comment in post 101: Nice post @1",
    ]
    actual_output = run_simulation(input_lines)
    assert actual_output == expected_output


def test_transition_to_interacting_and_two_message_cycle():
    """
    測項說明：
    測試人數門檻切換至「互動狀態」（在線人數 >= 10，含機器人）：
    1. 機器人本身算 1 人，當登入 9 位成員後，在線人數達 10 人，切換至互動狀態。
    2. 互動狀態下的聊天訊息回覆為兩則循環：
       第 1 則：Hi hi😁 @<發送者>
       第 2 則：I like your idea! @<發送者>
       第 3 則：循環回到 Hi hi😁 @<發送者>
    """
    from main import run_simulation

    input_lines = [
        '[started] {"time": "2023-08-07 00:00:00", "quota": 10}',
    ]
    # 登入 9 人 + 1 bot = 10 人
    for i in range(1, 10):
        input_lines.append(f'[login] {{"userId": "{i}", "isAdmin": false}}')

    input_lines.extend(
        [
            '[new message] {"authorId": "1", "content": "第1則訊息", "tags": []}',
            '[new message] {"authorId": "2", "content": "第2則訊息", "tags": []}',
            '[new message] {"authorId": "3", "content": "第3則訊息", "tags": []}',
            "[end]",
        ]
    )

    expected_output = [
        "💬 1: 第1則訊息",
        "🤖: Hi hi😁 @1",
        "💬 2: 第2則訊息",
        "🤖: I like your idea! @2",
        "💬 3: 第3則訊息",
        "🤖: Hi hi😁 @3",
    ]
    actual_output = run_simulation(input_lines)
    assert actual_output == expected_output


def test_interacting_post_comment_tags_all_online_participants():
    """
    測項說明：
    測試「互動狀態」下的論壇貼文回覆：
    機器人在貼文底下留言：
    🤖 comment in post <post id>: How do you guys think about it? @bot, @<登入者1>, @<登入者2>...
    標記順序規定：@bot 在最前，其餘依成員登入順序排列。
    """
    from main import run_simulation

    input_lines = [
        '[started] {"time": "2023-08-07 00:00:00", "quota": 10}',
    ]
    # 登入順序：2, 1, 3, 4, 5, 6, 7, 8, 9 (共 9 人 + 1 bot = 10 人)
    order = ["2", "1", "3", "4", "5", "6", "7", "8", "9"]
    for uid in order:
        input_lines.append(f'[login] {{"userId": "{uid}", "isAdmin": false}}')

    input_lines.extend(
        [
            '[new post] {"id": "88", "authorId": "2", "title": "熱門討論", "content": "大家覺得如何？", "tags": []}',
            "[end]",
        ]
    )

    expected_tags = "@bot, " + ", ".join([f"@{uid}" for uid in order])
    expected_output = [
        "2: 【熱門討論】大家覺得如何？",
        f"🤖 comment in post 88: How do you guys think about it? {expected_tags}",
    ]
    actual_output = run_simulation(input_lines)
    assert actual_output == expected_output


def test_logout_switches_back_to_default_and_resets_cycle():
    """
    測項說明：
    測試成員登出使在線人數 < 10 人時，切換回「預設對話狀態」，
    並驗證「重新返回預設對話狀態時，會重置從第一則 good to hear 開始回覆」。
    """
    from main import run_simulation

    input_lines = [
        '[started] {"time": "2023-08-07 00:00:00", "quota": 10}',
    ]
    for i in range(1, 10):
        input_lines.append(f'[login] {{"userId": "{i}", "isAdmin": false}}')

    # 在 Interacting 消耗第 1 則輪播
    input_lines.append('[new message] {"authorId": "1", "content": "互動訊息", "tags": []}')
    # 成員 9 登出 -> 剩下 8 人 + 1 bot = 9 人 (< 10) 切回 DefaultConversation
    input_lines.append('[logout] {"userId": "9"}')
    # 切回後發送訊息，必須重置回第 1 則 "good to hear"
    input_lines.append(
        '[new message] {"authorId": "1", "content": "回歸預設狀態第一則", "tags": []}'
    )
    input_lines.append("[end]")

    expected_output = [
        "💬 1: 互動訊息",
        "🤖: Hi hi😁 @1",
        "💬 1: 回歸預設狀態第一則",
        "🤖: good to hear @1",
    ]
    actual_output = run_simulation(input_lines)
    assert actual_output == expected_output
