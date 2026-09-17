import pytest


def test_command_replies_chat_first_then_executes_transition():
    """
    測項說明：
    驗證題目核心規則：
    「當社群成員傳送訊息並標記機器人時，若該訊息符合合法指令格式與權限條件，
    機器人仍會先依據當前狀態處理該訊息，之後再執行指令（如：切換狀態）。」
    例如：在預設對話狀態下，管理員發送 king @bot，
    機器人會先回覆預設輪播訊息 good to hear @<發送者>，
    然後再進入知識王狀態並開始出題。
    """
    from main import run_simulation

    input_lines = [
        '[started] {"time": "2023-08-07 00:00:00", "quota": 10}',
        '[login] {"userId": "admin_user", "isAdmin": true}',
        '[new message] {"authorId": "admin_user", "content": "king", "tags": ["bot"]}',
        "[end]",
    ]
    expected_output = [
        "💬 admin_user: king @bot",
        "🤖: good to hear @admin_user",
        "🤖: KnowledgeKing is started!",
        "🤖: 0. 請問哪個 SQL 語句用於選擇所有的行？",
        "A) SELECT *",
        "B) SELECT ALL",
        "C) SELECT ROWS",
        "D) SELECT DATA",
    ]
    actual_output = run_simulation(input_lines)
    assert actual_output == expected_output


def test_command_fails_silently_on_permission_denied():
    """
    測項說明：
    驗證權限不足時的「靜默失敗」政策：
    1. 一般成員 (isAdmin: false) 嘗試執行 king @bot（king 限管理員）。
    2. 機器人不會產生任何錯誤訊息，指令靜默失敗（不進入知識王、不扣額度）。
    3. 但因該指令本身是一則聊天訊息，機器人仍會依當前狀態回覆輪播訊息。
    4. 隨後下達正常聊天訊息，可證明機器人仍處於正常狀態（繼續第二則輪播）。
    """
    from main import run_simulation

    input_lines = [
        '[started] {"time": "2023-08-07 00:00:00", "quota": 10}',
        '[login] {"userId": "normal_user", "isAdmin": false}',
        '[new message] {"authorId": "normal_user", "content": "king", "tags": ["bot"]}',
        '[new message] {"authorId": "normal_user", "content": "哈囉", "tags": []}',
        "[end]",
    ]
    expected_output = [
        "💬 normal_user: king @bot",
        "🤖: good to hear @normal_user",
        "💬 normal_user: 哈囉",
        "🤖: thank you @normal_user",
    ]
    actual_output = run_simulation(input_lines)
    assert actual_output == expected_output


def test_command_fails_silently_on_insufficient_quota():
    """
    測項說明：
    驗證額度不足時的「靜默失敗」政策：
    1. 初始 Quota 為 4。
    2. 管理員嘗試執行 king @bot（需要 Quota 5）。
    3. Quota 4 < 5，指令靜默失敗（不進入知識王、不扣額度）。
    4. 機器人仍回覆當前狀態輪播訊息。
    5. 接著任何成員執行 record @bot（需要 Quota 3，4 >= 3），成功扣額度並進入錄音狀態。
    """
    from main import run_simulation

    input_lines = [
        '[started] {"time": "2023-08-07 00:00:00", "quota": 4}',
        '[login] {"userId": "admin", "isAdmin": true}',
        # king 需要 5 額度，目前只有 4 -> 失敗但正常回覆
        '[new message] {"authorId": "admin", "content": "king", "tags": ["bot"]}',
        # record 需要 3 額度，目前 4 額度足夠 -> 成功回覆並進入錄音
        '[new message] {"authorId": "admin", "content": "record", "tags": ["bot"]}',
        "[end]",
    ]
    expected_output = [
        "💬 admin: king @bot",
        "🤖: good to hear @admin",
        "💬 admin: record @bot",
        "🤖: thank you @admin",
    ]
    actual_output = run_simulation(input_lines)
    assert actual_output == expected_output


def test_shared_quota_depletion_across_multiple_users():
    """
    測項說明：
    驗證全社群「共用額度」之累加扣除：
    1. 初始 Quota 為 8。
    2. 用戶 1 執行 record（扣 3，剩餘 5），隨後下達 stop-recording（額度 0，限錄音者）。
    3. 管理員執行 king（扣 5，剩餘 0）。
    4. 管理員執行 king-stop（額度 0）回到正常狀態。
    5. 用戶 2 再次嘗試執行 record（需要 3，目前剩 0）-> 額度不足靜默失敗。
    """
    from main import run_simulation

    input_lines = [
        '[started] {"time": "2023-08-07 00:00:00", "quota": 8}',
        '[login] {"userId": "admin", "isAdmin": true}',
        '[login] {"userId": "user1", "isAdmin": false}',
        '[login] {"userId": "user2", "isAdmin": false}',
        # user1 執行 record (扣 3，剩 5)
        '[new message] {"authorId": "user1", "content": "record", "tags": ["bot"]}',
        # user1 停止錄音回正常 (扣 0，剩 5)
        '[new message] {"authorId": "user1", "content": "stop-recording", "tags": ["bot"]}',
        # admin 執行 king (扣 5，剩 0)
        '[new message] {"authorId": "admin", "content": "king", "tags": ["bot"]}',
        # admin 結束知識王回正常 (扣 0，剩 0)
        '[new message] {"authorId": "admin", "content": "king-stop", "tags": ["bot"]}',
        # user2 嘗試 record (需要 3，剩 0 -> 失敗)
        '[new message] {"authorId": "user2", "content": "record", "tags": ["bot"]}',
        "[end]",
    ]
    expected_output = [
        "💬 user1: record @bot",
        "🤖: good to hear @user1",
        "💬 user1: stop-recording @bot",
        "💬 admin: king @bot",
        "🤖: good to hear @admin",
        "🤖: KnowledgeKing is started!",
        "🤖: 0. 請問哪個 SQL 語句用於選擇所有的行？",
        "A) SELECT *",
        "B) SELECT ALL",
        "C) SELECT ROWS",
        "D) SELECT DATA",
        "💬 admin: king-stop @bot",
        "💬 user2: record @bot",
        "🤖: good to hear @user2",
    ]
    actual_output = run_simulation(input_lines)
    assert actual_output == expected_output
