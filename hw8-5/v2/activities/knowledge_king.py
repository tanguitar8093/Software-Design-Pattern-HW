from datetime import datetime as DateTime


class Question:
    def __init__(self, number: int, description: str, options: list[str], correctAnswer: str):
        self.number = number
        self.description = description
        self.options = options
        self.correctAnswer = correctAnswer

    def isCorrect(self, answer: str) -> bool:
        return answer == self.correctAnswer


class KnowledgeKingGame:
    def __init__(self, questions: list[Question], startTime: DateTime, currentQuestionIndex: int = 0):
        self.questions = questions  # 對應圖上被跳過的 KnowledgeKingGame o-- "3" Question 組合線
        self.currentQuestionIndex = currentQuestionIndex
        self.startTime = startTime
        self._scores: dict[str, int] = {}

    def getCurrentQuestion(self) -> Question:
        return self.questions[self.currentQuestionIndex]

    def submitAnswer(self, memberId: str, answer: str) -> bool:
        is_correct = self.getCurrentQuestion().isCorrect(answer)
        if is_correct:
            self._scores[memberId] = self._scores.get(memberId, 0) + 1
            self.currentQuestionIndex += 1
        return is_correct

    def isFinished(self) -> bool:
        return self.currentQuestionIndex >= len(self.questions)

    def isTimeout(self, currentTime: DateTime) -> bool:
        return (currentTime - self.startTime).total_seconds() >= 3600

    def getWinner(self) -> str:
        if not self._scores:
            return "Tie"
        highest = max(self._scores.values())
        winners = [memberId for memberId, score in self._scores.items() if score == highest]
        return winners[0] if len(winners) == 1 else "Tie"
