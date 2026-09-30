import json
import unittest

from v1.app.driver import AppDriver


class AppDriverTest(unittest.TestCase):
    def _start(self, quota: int = 20) -> AppDriver:
        driver = AppDriver()
        driver.run([f'[started] {{"time": "2023-08-07 00:00:00", "quota": {quota}}}'])
        return driver

    def test_started_builds_community_and_bot(self) -> None:
        driver = self._start()
        self.assertIsNotNone(driver.community)
        self.assertIsNotNone(driver.bot)
        assert driver.bot is not None
        self.assertEqual(driver.bot.quota, 20)

    def test_started_accepts_any_positive_integer_quota(self) -> None:
        for quota in (1, 10, 20):
            with self.subTest(quota=quota):
                driver = self._start(quota=quota)
                assert driver.bot is not None
                self.assertEqual(driver.bot.quota, quota)

    def test_started_requires_quota(self) -> None:
        driver = AppDriver()
        with self.assertRaisesRegex(ValueError, "quota must be a positive integer"):
            driver.run(['[started] {"time": "2023-08-07 00:00:00"}'])
        self.assertIsNone(driver.community)
        self.assertIsNone(driver.bot)

    def test_started_rejects_invalid_quota(self) -> None:
        for value in (0, -1, True, False, None, 1.5, "10"):
            with self.subTest(quota=value):
                driver = AppDriver()
                with self.assertRaisesRegex(ValueError, "quota must be a positive integer"):
                    payload = json.dumps({"time": "2023-08-07 00:00:00", "quota": value})
                    driver.run([f"[started] {payload}"])
                self.assertIsNone(driver.community)
                self.assertIsNone(driver.bot)

    def test_unknown_event_is_ignored(self) -> None:
        driver = self._start()
        self.assertEqual(driver.run(['[future event] {"newField": 1}']), [])

    def test_login_and_logout_change_online_count(self) -> None:
        driver = self._start()
        driver.run(['[login] {"userId": "1", "isAdmin": false}'])
        assert driver.community is not None
        self.assertEqual(driver.community.getOnlineCount(), 1)
        driver.run(['[logout] {"userId": "1"}'])
        self.assertEqual(driver.community.getOnlineCount(), 0)

    def test_new_message_produces_transcript_and_bot_reply(self) -> None:
        driver = self._start()
        driver.run(
            [
                '[login] {"userId": "1", "isAdmin": true}',
                '[new message] {"authorId": "1", "content": "hi", "tags": []}',
            ]
        )
        self.assertEqual(driver.output[-2:], ["💬 1: hi", "🤖: good to hear @1"])

    def test_record_command_deducts_quota_and_replays_voice(self) -> None:
        driver = self._start(quota=20)
        driver.run(
            [
                '[login] {"userId": "1", "isAdmin": true}',
                '[new message] {"authorId": "1", "content": "record", "tags": ["bot"]}',
                '[go broadcasting] {"speakerId": "1"}',
                '[speak] {"speakerId": "1", "content": "line one"}',
                '[speak] {"speakerId": "1", "content": "line two"}',
                '[stop broadcasting] {"speakerId": "1"}',
            ]
        )
        assert driver.bot is not None
        self.assertEqual(driver.bot.quota, 17)
        self.assertIn("🤖: line one\nline two @1", driver.output)

    def test_king_flow_reaches_thanks_for_joining_with_winner(self) -> None:
        driver = self._start(quota=20)
        driver.run(
            [
                '[login] {"userId": "1", "isAdmin": true}',
                '[new message] {"authorId": "1", "content": "king", "tags": ["bot"]}',
                '[new message] {"authorId": "1", "content": "A", "tags": ["bot"]}',
                '[new message] {"authorId": "1", "content": "C", "tags": ["bot"]}',
                '[new message] {"authorId": "1", "content": "A", "tags": ["bot"]}',
            ]
        )
        self.assertIn("🤖: KnowledgeKing is started!", driver.output)
        self.assertEqual(driver.output.count("🤖: Congrats! you got the answer! @1"), 3)
        self.assertIn("🤖 speaking: The winner is 1", driver.output)

    def test_new_post_and_bot_comment_are_recorded(self) -> None:
        driver = self._start()
        driver.run(
            [
                '[login] {"userId": "8", "isAdmin": false}',
                '[new post] {"id": "1", "authorId": "8", "title": "t", "content": "c", "tags": []}',
            ]
        )
        self.assertIn("8: 【t】c", driver.output)
        self.assertIn("🤖 comment in post 1: Nice post @8", driver.output)


if __name__ == "__main__":
    unittest.main()
