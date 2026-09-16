import pytest


def test_record_enter_when_already_broadcasting_goes_to_recording():
    """
    測項說明：
    測試進入錄音狀態時的初始子狀態判定：
    「如果已經有講者正在廣播，初始狀態為錄音中狀態 (Recording)，否則會直接進入等待狀態 (Waiting)。」
    此測試先有成員 4 開始廣播，成員 3 才下達 record @bot。
    機器人應直接處於 Recording 狀態，講者發言被記錄，講者下麥後立即輸出 Replay。
    """
    from homework8_Waterball.main import run_simulation

    input_lines = [
        '[started] {"time": "2023-08-07 00:00:00", "quota": 10}',
        '[login] {"userId": "3", "isAdmin": false}',
        '[login] {"userId": "4", "isAdmin": false}',
        # 4 先開始廣播
        '[go broadcasting] {"speakerId": "4"}',
        # 3 才進入錄音 -> 直接為 Recording 狀態
        '[new message] {"authorId": "3", "content": "record", "tags": ["bot"]}',
        '[speak] {"speakerId": "4", "content": "正在廣播中的第一句話"}',
        '[stop broadcasting] {"speakerId": "4"}',
        # 結束錄音
        '[new message] {"authorId": "3", "content": "stop-recording", "tags": ["bot"]}',
        "[end]",
    ]
    expected_output = [
        "📢 4 is broadcasting...",
        "💬 3: record @bot",
        "🤖: good to hear @3",
        "📢 4: 正在廣播中的第一句話",
        "📢 4 stop broadcasting",
        "🤖: [Record Replay] 正在廣播中的第一句話 @3",
        "💬 3: stop-recording @bot",
    ]
    actual_output = run_simulation(input_lines)
    assert actual_output == expected_output


def test_record_multiple_speakers_and_no_chat_reply_in_record():
    """
    測項說明：
    測試錄音狀態下的特性：
    1. 在錄音狀態下，一般聊天訊息「不會觸發輪播回覆」。
    2. 多位講者先後上麥、說話、下麥，每次下麥皆產出該講者的 Replay，標記錄音者。
    3. 在 Waiting 狀態下下達 stop-recording，不會輸出任何 Replay，正常回到 Normal 狀態。
    """
    from homework8_Waterball.main import run_simulation

    input_lines = [
        '[started] {"time": "2023-08-07 00:00:00", "quota": 10}',
        '[login] {"userId": "rec", "isAdmin": false}',
        '[login] {"userId": "spk1", "isAdmin": false}',
        '[login] {"userId": "spk2", "isAdmin": false}',
        '[login] {"userId": "other", "isAdmin": false}',
        # rec 啟動錄音 (當前無人廣播 -> 進入 Waiting)
        '[new message] {"authorId": "rec", "content": "record", "tags": ["bot"]}',
        # 聊天訊息在錄音中不回覆！
        '[new message] {"authorId": "other", "content": "這句話機器人不應該回", "tags": []}',
        # spk1 上麥發言
        '[go broadcasting] {"speakerId": "spk1"}',
        '[speak] {"speakerId": "spk1", "content": "講者一 第一句"}',
        '[speak] {"speakerId": "spk1", "content": "講者一 第二句"}',
        '[stop broadcasting] {"speakerId": "spk1"}',
        # spk2 上麥發言
        '[go broadcasting] {"speakerId": "spk2"}',
        '[speak] {"speakerId": "spk2", "content": "講者二 第一句"}',
        '[stop broadcasting] {"speakerId": "spk2"}',
        # 當前處於 Waiting 狀態，rec 下達 stop-recording -> 不產生 Replay 直接結束錄音
        '[new message] {"authorId": "rec", "content": "stop-recording", "tags": ["bot"]}',
        # 回到 Normal 狀態後，發言應恢復輪播（從第 1 則 good to hear 重置）
        '[new message] {"authorId": "other", "content": "回到正常狀態了", "tags": []}',
        "[end]",
    ]
    expected_output = [
        "💬 rec: record @bot",
        "🤖: good to hear @rec",
        "💬 other: 這句話機器人不應該回",
        "📢 spk1 is broadcasting...",
        "📢 spk1: 講者一 第一句",
        "📢 spk1: 講者一 第二句",
        "📢 spk1 stop broadcasting",
        "🤖: [Record Replay] 講者一 第一句",
        "講者一 第二句 @rec",
        "📢 spk2 is broadcasting...",
        "📢 spk2: 講者二 第一句",
        "📢 spk2 stop broadcasting",
        "🤖: [Record Replay] 講者二 第一句 @rec",
        "💬 rec: stop-recording @bot",
        "💬 other: 回到正常狀態了",
        "🤖: good to hear @other",
    ]
    actual_output = run_simulation(input_lines)
    assert actual_output == expected_output


def test_stop_recording_during_recording_flushes_current_replay():
    """
    測項說明：
    測試在「錄音中狀態 (Recording)」下達 stop-recording：
    「如果此時為錄音中狀態，會將講者廣播過程中截至目前錄下的所有語音訊息，
    以 Record Replay 格式輸出、標記錄音者且傳訊到聊天室中，回到正常狀態。」
    """
    from homework8_Waterball.main import run_simulation

    input_lines = [
        '[started] {"time": "2023-08-07 00:00:00", "quota": 10}',
        '[login] {"userId": "rec", "isAdmin": false}',
        '[login] {"userId": "spk", "isAdmin": false}',
        '[new message] {"authorId": "rec", "content": "record", "tags": ["bot"]}',
        '[go broadcasting] {"speakerId": "spk"}',
        '[speak] {"speakerId": "spk", "content": "未結束廣播時的語音 1"}',
        '[speak] {"speakerId": "spk", "content": "未結束廣播時的語音 2"}',
        # 講者尚未 stop broadcasting，錄音者直接 stop-recording
        '[new message] {"authorId": "rec", "content": "stop-recording", "tags": ["bot"]}',
        "[end]",
    ]
    expected_output = [
        "💬 rec: record @bot",
        "🤖: good to hear @rec",
        "📢 spk is broadcasting...",
        "📢 spk: 未結束廣播時的語音 1",
        "📢 spk: 未結束廣播時的語音 2",
        "💬 rec: stop-recording @bot",
        "🤖: [Record Replay] 未結束廣播時的語音 1",
        "未結束廣播時的語音 2 @rec",
    ]
    actual_output = run_simulation(input_lines)
    assert actual_output == expected_output


def test_non_recorder_cannot_stop_recording():
    """
    測項說明：
    測試 stop-recording 權限檢查：
    「只有錄音者 (recorder) 方可使用 stop-recording。」
    非錄音者發送 stop-recording 時靜默失敗，錄音狀態持續進行。
    """
    from homework8_Waterball.main import run_simulation

    input_lines = [
        '[started] {"time": "2023-08-07 00:00:00", "quota": 10}',
        '[login] {"userId": "recorder_user", "isAdmin": false}',
        '[login] {"userId": "hacker_user", "isAdmin": true}',  # 即使是管理員，非錄音者也不能 stop-recording
        '[login] {"userId": "speaker", "isAdmin": false}',
        '[new message] {"authorId": "recorder_user", "content": "record", "tags": ["bot"]}',
        '[go broadcasting] {"speakerId": "speaker"}',
        '[speak] {"speakerId": "speaker", "content": "錄音中"}',
        # 非錄音者嘗試停止錄音 -> 失敗
        '[new message] {"authorId": "hacker_user", "content": "stop-recording", "tags": ["bot"]}',
        '[speak] {"speakerId": "speaker", "content": "繼續錄音"}',
        '[stop broadcasting] {"speakerId": "speaker"}',
        # 真正的錄音者停止錄音 -> 成功
        '[new message] {"authorId": "recorder_user", "content": "stop-recording", "tags": ["bot"]}',
        "[end]",
    ]
    expected_output = [
        "💬 recorder_user: record @bot",
        "🤖: good to hear @recorder_user",
        "📢 speaker is broadcasting...",
        "📢 speaker: 錄音中",
        "💬 hacker_user: stop-recording @bot",
        "📢 speaker: 繼續錄音",
        "📢 speaker stop broadcasting",
        "🤖: [Record Replay] 錄音中",
        "繼續錄音 @recorder_user",
        "💬 recorder_user: stop-recording @bot",
    ]
    actual_output = run_simulation(input_lines)
    assert actual_output == expected_output
