import unittest

from v2.app.driver import AppDriver


PLAY_AGAIN = '[new message] {"authorId": "1", "content": "play again", "tags": ["bot"]}'
ANSWER_A = '[new message] {"authorId": "1", "content": "A", "tags": ["bot"]}'
QUESTION_ZERO = "🤖: 0. 請問哪個 SQL 語句用於選擇所有的行？"


class PlayAgainTest(unittest.TestCase):
    def _start_king(self, quota: int) -> AppDriver:
        driver = AppDriver()
        driver.run(
            [
                f'[started] {{"time": "2023-08-07 00:00:00", "quota": {quota}}}',
                '[login] {"userId": "1", "isAdmin": true}',
                '[new message] {"authorId": "1", "content": "king", "tags": ["bot"]}',
            ]
        )
        return driver

    def test_play_again_during_questioning_restarts_from_first_question(self) -> None:
        driver = self._start_king(quota=20)
        driver.run([ANSWER_A, PLAY_AGAIN])
        assert driver.bot is not None
        self.assertEqual(driver.bot.quota, 10)
        self.assertEqual(driver.output[-2], "🤖: KnowledgeKing is gonna start again!")
        self.assertTrue(driver.output[-1].startswith(QUESTION_ZERO))
        driver.run([ANSWER_A])
        self.assertTrue(driver.output[-1].startswith("🤖: 1. 請問哪個 CSS"))

    def test_play_again_during_thanks_for_joining_restarts_game(self) -> None:
        driver = self._start_king(quota=20)
        driver.run([ANSWER_A, '[new message] {"authorId": "1", "content": "C", "tags": ["bot"]}', ANSWER_A])
        self.assertIn("🤖 speaking: The winner is 1", driver.output)
        driver.run([PLAY_AGAIN])
        assert driver.bot is not None
        self.assertEqual(driver.bot.quota, 10)
        self.assertEqual(driver.output[-2], "🤖: KnowledgeKing is gonna start again!")
        self.assertTrue(driver.output[-1].startswith(QUESTION_ZERO))

    def test_play_again_with_insufficient_quota_does_not_restart(self) -> None:
        driver = self._start_king(quota=5)
        driver.run([PLAY_AGAIN])
        assert driver.bot is not None
        self.assertEqual(driver.bot.quota, 0)
        self.assertEqual(driver.output[-1], "💬 1: play again @bot")
        self.assertEqual(sum(line.startswith(QUESTION_ZERO) for line in driver.output), 1)
        driver.run([ANSWER_A])
        self.assertTrue(driver.output[-1].startswith("🤖: 1. 請問哪個 CSS"))


if __name__ == "__main__":
    unittest.main()
