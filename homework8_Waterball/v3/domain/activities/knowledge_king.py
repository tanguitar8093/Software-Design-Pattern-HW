from __future__ import annotations
from typing import List, Optional


class Question:
    def __init__(self, number: int, description: str, options: List[str], correctAnswer: str):
        self.number: int = number
        self.description: str = description
        self.options: List[str] = options
        self.correctAnswer: str = correctAnswer

    def isCorrect(self, answer: str) -> bool:
        return answer.strip().upper() == self.correctAnswer.strip().upper()


class KnowledgeKingGame:
    def __init__(self):
        self.currentQuestionIndex: int = 0
        self.scores: dict[str, int] = {}
        self.questions: List[Question] = [
            Question(
                0,
                "0. 請問哪個 SQL 語句用於選擇所有的行？\nA) SELECT *\nB) SELECT ALL\nC) SELECT ROWS\nD) SELECT DATA",
                ["A", "B", "C", "D"],
                "A",
            ),
            Question(
                1,
                "1. 請問哪個 CSS 屬性可用於設置文字的顏色？\nA) text-align\nB) font-size\nC) color\nD) padding",
                ["A", "B", "C", "D"],
                "C",
            ),
            Question(
                2,
                "2. 請問在計算機科學中，「XML」代表什麼？\nA) Extensible Markup Language\nB) Extensible Modeling Language\nC) Extended Markup Language\nD) Extended Modeling Language",
                ["A", "B", "C", "D"],
                "A",
            ),
        ]

    def getCurrentQuestion(self) -> Optional[Question]:
        if self.currentQuestionIndex < len(self.questions):
            return self.questions[self.currentQuestionIndex]
        return None

    def submitAnswer(self, memberId: str, answer: str) -> bool:
        q = self.getCurrentQuestion()
        if q is not None and q.isCorrect(answer):
            self.scores[memberId] = self.scores.get(memberId, 0) + 1
            self.currentQuestionIndex += 1
            return True
        return False

    def isFinished(self) -> bool:
        return self.currentQuestionIndex >= len(self.questions)

    def getWinner(self) -> str:
        if not self.scores:
            return "Tie!"
        max_score = max(self.scores.values())
        winners = [uid for uid, s in self.scores.items() if s == max_score]
        if len(winners) > 1:
            return "Tie!"
        return f"The winner is {winners[0]}"
