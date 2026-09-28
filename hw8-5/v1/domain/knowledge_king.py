from datetime import datetime as DateTime


class Question:
    def __init__(self, number: int, description: str, options: list[str], correctAnswer: str):
        self.number = number
        self.description = description
        self.options = options
        self.correctAnswer = correctAnswer

    def isCorrect(self, answer: str) -> bool:
        raise NotImplementedError


class KnowledgeKingGame:
    def __init__(self, currentQuestionIndex: int, startTime: DateTime):
        self.currentQuestionIndex = currentQuestionIndex
        self.startTime = startTime

    def getCurrentQuestion(self) -> Question:
        raise NotImplementedError

    def submitAnswer(self, memberId: str, answer: str) -> bool:
        raise NotImplementedError

    def isFinished(self) -> bool:
        raise NotImplementedError

    def isTimeout(self, currentTime: DateTime) -> bool:
        raise NotImplementedError

    def getWinner(self) -> str:
        raise NotImplementedError
