from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional


@dataclass
class Question:
    number: int
    description: str
    options: List[str]
    correct_answer: str

    def is_correct(self, answer: str) -> bool:
        return answer.strip().upper() == self.correct_answer.upper()


QUESTION_BANK: List[Question] = [
    Question(
        0,
        "請問哪個 SQL 語句用於選擇所有的行？",
        ["A) SELECT *", "B) SELECT ALL", "C) SELECT ROWS", "D) SELECT DATA"],
        "A",
    ),
    Question(
        1,
        "請問哪個 CSS 屬性可用於設置文字的顏色？",
        ["A) text-align", "B) font-size", "C) color", "D) padding"],
        "C",
    ),
    Question(
        2,
        "請問在計算機科學中，「XML」代表什麼？",
        [
            "A) Extensible Markup Language",
            "B) Extensible Modeling Language",
            "C) Extended Markup Language",
            "D) Extended Modeling Language",
        ],
        "A",
    ),
]


class KnowledgeKingGame:
    """對應 OOA-Clean.mmd KnowledgeKingGame：掌握題庫進度、作答評分與勝負結算。"""

    def __init__(self, start_time: datetime) -> None:
        self.current_question_index = 0
        self.start_time = start_time
        self.scores: Dict[str, int] = {}

    def get_current_question(self) -> Question:
        return QUESTION_BANK[self.current_question_index]

    def submit_answer(self, member_id: str, answer: str) -> bool:
        if not self.get_current_question().is_correct(answer):
            return False
        self.scores[member_id] = self.scores.get(member_id, 0) + 1
        self.current_question_index += 1
        return True

    def is_finished(self) -> bool:
        return self.current_question_index >= len(QUESTION_BANK)

    def is_timeout(self, current_time: datetime) -> bool:
        return (current_time - self.start_time) >= timedelta(hours=1)

    def get_winner(self) -> Optional[str]:
        if not self.scores:
            return None
        max_score = max(self.scores.values())
        winners = [member_id for member_id, score in self.scores.items() if score == max_score]
        return winners[0] if len(winners) == 1 else None
