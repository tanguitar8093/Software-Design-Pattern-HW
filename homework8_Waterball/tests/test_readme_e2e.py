import pytest

README_INPUT = """[started] {"time": "2023-08-07 00:00:00", "quota": 20}
[login] {"userId": "1", "isAdmin": true}
[login] {"userId": "2", "isAdmin": false}
[login] {"userId": "3", "isAdmin": false}
[login] {"userId": "4", "isAdmin": false}
[3 seconds elapsed]
[login] {"userId": "5", "isAdmin": false}
[login] {"userId": "6", "isAdmin": false}
[new message] {"authorId": "1", "content": "大家早安，今天我第一天上班呢", "tags": []}
[login] {"userId": "7", "isAdmin": false}
[new message] {"authorId": "4", "content": "祝大家今天事事順利", "tags": ["1"]}
[login] {"userId": "8", "isAdmin": false}
[login] {"userId": "9", "isAdmin": false}
[10 seconds elapsed]
[new message] {"authorId": "1", "content": "wow 有 10 個人在線上了呢（包含機器人）", "tags": []}
[new message] {"authorId": "1", "content": "大家早安，今天要吃麥當勞嗎？", "tags": []}
[new message] {"authorId": "8", "content": "發了一個文，分享笑話，哈哈", "tags": []}
[new post]  {"id": "1", "authorId": "8", "title": "分享一個關於 單一職責原則 的笑話，每次講起來都還是覺得很好笑", "content": "(1) 欸你這個類別這樣做太多事了吧，違反單一職責原則啊，每個類別只能有一個職責，只能做一件事。 (2) 這個類別，確實只做一件事，那就是實現需求！", "tags": ["1", "2", "3"]}
[new message] {"authorId": "1", "content": "king", "tags": ["bot"]}
[new message] {"authorId": "6", "content": "A", "tags": ["bot"]}
[new message] {"authorId": "8", "content": "C", "tags": ["bot"]}
[3 seconds elapsed]
[new message] {"authorId": "3", "content": "C", "tags": ["bot"]}
[new message] {"authorId": "2", "content": "A", "tags": ["bot"]}
[20 seconds elapsed]
[new message] {"authorId": "3", "content": "record", "tags": ["bot"]}
[go broadcasting] {"speakerId": "4"}
[speak] {"speakerId": "4", "content": "大家早安"}
[speak] {"speakerId": "4", "content": "各位有吃早餐嗎？"}
[stop broadcasting] {"speakerId": "4"}
[new message] {"authorId": "3", "content": "stop-recording", "tags": ["bot"]}
[logout] {"userId": "9"}
[logout] {"userId": "8"}
[3 seconds elapsed]
[logout] {"userId": "7"}
[logout] {"userId": "6"}
[new message] {"authorId": "1", "content": "呀，大家下線了", "tags": []}
[end]"""

README_EXPECTED_OUTPUT = """🕑 3 seconds elapsed...
💬 1: 大家早安，今天我第一天上班呢
🤖: good to hear @1
💬 4: 祝大家今天事事順利 @1
🤖: thank you @4
🕑 10 seconds elapsed...
💬 1: wow 有 10 個人在線上了呢（包含機器人）
🤖: Hi hi😁 @1
💬 1: 大家早安，今天要吃麥當勞嗎？
🤖: I like your idea! @1
💬 8: 發了一個文，分享笑話，哈哈
🤖: Hi hi😁 @8
8: 【分享一個關於 單一職責原則 的笑話，每次講起來都還是覺得很好笑】(1) 欸你這個類別這樣做太多事了吧，違反單一職責原則啊，每個類別只能有一個職責，只能做一件事。 (2) 這個類別，確實只做一件事，那就是實現需求！ @1, @2, @3
🤖 comment in post 1: How do you guys think about it? @bot, @1, @2, @3, @4, @5, @6, @7, @8, @9
💬 1: king @bot
🤖: I like your idea! @1
🤖: KnowledgeKing is started!
🤖: 0. 請問哪個 SQL 語句用於選擇所有的行？
A) SELECT *
B) SELECT ALL
C) SELECT ROWS
D) SELECT DATA
💬 6: A @bot
🤖: Congrats! you got the answer! @6
🤖: 1. 請問哪個 CSS 屬性可用於設置文字的顏色？
A) text-align
B) font-size
C) color
D) padding
💬 8: C @bot
🤖: Congrats! you got the answer! @8
🤖: 2. 請問在計算機科學中，「XML」代表什麼？
A) Extensible Markup Language
B) Extensible Modeling Language
C) Extended Markup Language
D) Extended Modeling Language
🕑 3 seconds elapsed...
💬 3: C @bot
💬 2: A @bot
🤖: Congrats! you got the answer! @2
🤖 go broadcasting...
🤖 speaking: Tie!
🤖 stop broadcasting...
🕑 20 seconds elapsed...
💬 3: record @bot
🤖: Hi hi😁 @3
📢 4 is broadcasting...
📢 4: 大家早安
📢 4: 各位有吃早餐嗎？
📢 4 stop broadcasting
🤖: [Record Replay] 大家早安
各位有吃早餐嗎？ @3
💬 3: stop-recording @bot
🕑 3 seconds elapsed...
💬 1: 呀，大家下線了
🤖: good to hear @1"""


def test_readme_official_example_e2e():
    """
    測項說明：
    驗收 README.md 中的官方完整範例端到端全流程。
    涵蓋：
    1. 初始小於 10 人在線 -> 預設對話狀態 (Default Conversation) 輪播回覆
    2. 登入達 10 人（含 bot）-> 切換互動狀態 (Interacting) 輪播回覆與全體標記留言
    3. 管理員發送 king @bot -> 進入知識王狀態，出題與計分，平手語音廣播結算，20 秒超時退出回正常
    4. 成員發送 record @bot -> 進入錄音狀態，講者上麥發言錄音，下麥輸出 Replay
    5. 錄音者發送 stop-recording @bot -> 結束錄音返回正常
    6. 成員登出使人數小於 10 人 -> 切換回預設對話狀態，輪播重置為第一則
    """
    from homework8_Waterball.main import run_simulation

    input_lines = [line for line in README_INPUT.strip().split("\n") if line.strip()]
    expected_lines = [line for line in README_EXPECTED_OUTPUT.strip().split("\n")]

    actual_output = run_simulation(input_lines)
    assert actual_output == expected_lines
