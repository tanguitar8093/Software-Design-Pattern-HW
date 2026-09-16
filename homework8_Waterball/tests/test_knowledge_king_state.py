import pytest


def test_knowledge_king_with_clear_winner_and_chat_announcement_if_broadcasting():
    """
    測項說明：
    測試知識王完整答題與結算：
    1. 驗證首位正確答對者得分，答錯或未標記機器人靜默忽略。
    2. 三題答完後，有明確單一獲勝者 (The winner is <userId>)。
    3. 若結算時「已有成員正在廣播」，機器人改透過「聊天室訊息」公布遊戲結果，而非廣播。
    4. 結算後經過 20 秒，知識王結束返回正常狀態。
    """
    from homework8_Waterball.main import run_simulation

    input_lines = [
        '[started] {"time": "2023-08-07 00:00:00", "quota": 10}',
        '[login] {"userId": "admin", "isAdmin": true}',
        '[login] {"userId": "p1", "isAdmin": false}',
        '[login] {"userId": "p2", "isAdmin": false}',
        '[login] {"userId": "spk", "isAdmin": false}',
        # 啟動知識王
        '[new message] {"authorId": "admin", "content": "king", "tags": ["bot"]}',
        # 第 0 題（答案 A）：
        # p2 答錯（B）-> 靜默忽略
        '[new message] {"authorId": "p2", "content": "B", "tags": ["bot"]}',
        # p1 沒 tag bot 答 A -> 靜默忽略
        '[new message] {"authorId": "p1", "content": "A", "tags": []}',
        # p1 正確答 A 並 tag bot -> p1 得 1 分，出第 1 題
        '[new message] {"authorId": "p1", "content": "A", "tags": ["bot"]}',
        # 第 1 題（答案 C）：
        # p1 正確答 C -> p1 再得 1 分，出第 2 題
        '[new message] {"authorId": "p1", "content": "C", "tags": ["bot"]}',
        # 此時 spk 開始廣播（有人正在廣播）
        '[go broadcasting] {"speakerId": "spk"}',
        # 第 2 題（答案 A）：
        # p2 正確答 A -> p2 得 1 分。全部 3 題答完進入結算！
        # p1 得 2 分，p2 得 1 分 -> 獲勝者為 p1。
        # 因當前 spk 正在廣播，機器人透過聊天室訊息公布！
        '[new message] {"authorId": "p2", "content": "A", "tags": ["bot"]}',
        # 20 秒過後退出知識王回正常狀態
        '[20 seconds elapsed]',
        # 驗證回到正常狀態
        '[new message] {"authorId": "p1", "content": "回到正常了嗎", "tags": []}',
        "[end]",
    ]
    expected_output = [
        "💬 admin: king @bot",
        "🤖: good to hear @admin",
        "🤖: KnowledgeKing is started!",
        "🤖: 0. 請問哪個 SQL 語句用於選擇所有的行？",
        "A) SELECT *",
        "B) SELECT ALL",
        "C) SELECT ROWS",
        "D) SELECT DATA",
        "💬 p2: B @bot",
        "💬 p1: A",
        "💬 p1: A @bot",
        "🤖: Congrats! you got the answer! @p1",
        "🤖: 1. 請問哪個 CSS 屬性可用於設置文字的顏色？",
        "A) text-align",
        "B) font-size",
        "C) color",
        "D) padding",
        "💬 p1: C @bot",
        "🤖: Congrats! you got the answer! @p1",
        "🤖: 2. 請問在計算機科學中，「XML」代表什麼？",
        "A) Extensible Markup Language",
        "B) Extensible Modeling Language",
        "C) Extended Markup Language",
        "D) Extended Modeling Language",
        "📢 spk is broadcasting...",
        "💬 p2: A @bot",
        "🤖: Congrats! you got the answer! @p2",
        "🤖: The winner is p1",
        "🕑 20 seconds elapsed...",
        "💬 p1: 回到正常了嗎",
        "🤖: good to hear @p1",
    ]
    actual_output = run_simulation(input_lines)
    assert actual_output == expected_output


def test_knowledge_king_one_hour_timeout_settlement():
    """
    測項說明：
    測試知識王 1 小時超時結算：
    「若在 1 小時之後，這 3 題尚未全部答完，那麼也會立即中斷且進入感謝參與狀態。」
    若此時無人廣播，透過語音廣播公布結果。
    """
    from homework8_Waterball.main import run_simulation

    input_lines = [
        '[started] {"time": "2023-08-07 00:00:00", "quota": 10}',
        '[login] {"userId": "admin", "isAdmin": true}',
        '[login] {"userId": "user1", "isAdmin": false}',
        '[new message] {"authorId": "admin", "content": "king", "tags": ["bot"]}',
        # user1 答對第 0 題
        '[new message] {"authorId": "user1", "content": "A", "tags": ["bot"]}',
        # 第 1 題無人回答，經過 1 小時
        '[1 hours elapsed]',
        # 進入 ThanksForJoining，因無人廣播，由機器人語音廣播獲勝者 user1
        # 再過 20 秒回到正常狀態
        '[20 seconds elapsed]',
        '[end]',
    ]
    expected_output = [
        "💬 admin: king @bot",
        "🤖: good to hear @admin",
        "🤖: KnowledgeKing is started!",
        "🤖: 0. 請問哪個 SQL 語句用於選擇所有的行？",
        "A) SELECT *",
        "B) SELECT ALL",
        "C) SELECT ROWS",
        "D) SELECT DATA",
        "💬 user1: A @bot",
        "🤖: Congrats! you got the answer! @user1",
        "🤖: 1. 請問哪個 CSS 屬性可用於設置文字的顏色？",
        "A) text-align",
        "B) font-size",
        "C) color",
        "D) padding",
        "🕑 1 hours elapsed...",
        "🤖 go broadcasting...",
        "🤖 speaking: The winner is user1",
        "🤖 stop broadcasting...",
        "🕑 20 seconds elapsed...",
    ]
    actual_output = run_simulation(input_lines)
    assert actual_output == expected_output


def test_knowledge_king_play_again_command():
    """
    測項說明：
    測試在知識王中下達 play again @bot 指令（額度 5，任何成員）：
    機器人在聊天室傳遞：KnowledgeKing is gonna start again!，
    並重開遊戲、出第 0 題。
    """
    from homework8_Waterball.main import run_simulation

    input_lines = [
        '[started] {"time": "2023-08-07 00:00:00", "quota": 20}',
        '[login] {"userId": "admin", "isAdmin": true}',
        '[login] {"userId": "player", "isAdmin": false}',
        '[new message] {"authorId": "admin", "content": "king", "tags": ["bot"]}',
        # 進行中下達 play again (需要 Quota 5)
        '[new message] {"authorId": "player", "content": "play again", "tags": ["bot"]}',
        # 正確回答重開後的第 0 題
        '[new message] {"authorId": "player", "content": "A", "tags": ["bot"]}',
        '[end]',
    ]
    expected_output = [
        "💬 admin: king @bot",
        "🤖: good to hear @admin",
        "🤖: KnowledgeKing is started!",
        "🤖: 0. 請問哪個 SQL 語句用於選擇所有的行？",
        "A) SELECT *",
        "B) SELECT ALL",
        "C) SELECT ROWS",
        "D) SELECT DATA",
        "💬 player: play again @bot",
        "🤖: KnowledgeKing is gonna start again!",
        "🤖: 0. 請問哪個 SQL 語句用於選擇所有的行？",
        "A) SELECT *",
        "B) SELECT ALL",
        "C) SELECT ROWS",
        "D) SELECT DATA",
        "💬 player: A @bot",
        "🤖: Congrats! you got the answer! @player",
        "🤖: 1. 請問哪個 CSS 屬性可用於設置文字的顏色？",
        "A) text-align",
        "B) font-size",
        "C) color",
        "D) padding",
    ]
    actual_output = run_simulation(input_lines)
    assert actual_output == expected_output


def test_knowledge_king_king_stop_command():
    """
    測項說明：
    測試 king-stop 指令（額度 0，限管理員）：
    管理員下達 king-stop @bot，立即中斷知識王遊戲返回正常狀態。
    若非管理員下達則靜默失敗。
    """
    from homework8_Waterball.main import run_simulation

    input_lines = [
        '[started] {"time": "2023-08-07 00:00:00", "quota": 10}',
        '[login] {"userId": "admin", "isAdmin": true}',
        '[login] {"userId": "normal_user", "isAdmin": false}',
        '[new message] {"authorId": "admin", "content": "king", "tags": ["bot"]}',
        # 一般成員嘗試 king-stop -> 失敗（知識王繼續）
        '[new message] {"authorId": "normal_user", "content": "king-stop", "tags": ["bot"]}',
        # 管理員下達 king-stop -> 成功退出回正常狀態
        '[new message] {"authorId": "admin", "content": "king-stop", "tags": ["bot"]}',
        # 驗證回到正常狀態（第一則輪播回覆）
        '[new message] {"authorId": "normal_user", "content": "大家都還在嗎", "tags": []}',
        "[end]",
    ]
    expected_output = [
        "💬 admin: king @bot",
        "🤖: good to hear @admin",
        "🤖: KnowledgeKing is started!",
        "🤖: 0. 請問哪個 SQL 語句用於選擇所有的行？",
        "A) SELECT *",
        "B) SELECT ALL",
        "C) SELECT ROWS",
        "D) SELECT DATA",
        "💬 normal_user: king-stop @bot",
        "💬 admin: king-stop @bot",
        "💬 normal_user: 大家都還在嗎",
        "🤖: good to hear @normal_user",
    ]
    actual_output = run_simulation(input_lines)
    assert actual_output == expected_output
