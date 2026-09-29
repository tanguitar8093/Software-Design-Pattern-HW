from ...fsm.core import Event, Guard


class OnlineCountAtLeastGuard(Guard):
    def __init__(self, threshold: int):
        self.threshold = threshold

    def isSatisfied(self, event: Event) -> bool:
        raise NotImplementedError


class IsBroadcastingGuard(Guard):
    def isSatisfied(self, event: Event) -> bool:
        raise NotImplementedError


class AdminOnlyGuard(Guard):
    def isSatisfied(self, event: Event) -> bool:
        raise NotImplementedError


class QuotaAvailableGuard(Guard):
    def __init__(self, cost: int):
        self.cost = cost

    def isSatisfied(self, event: Event) -> bool:
        raise NotImplementedError


class CorrectAnswerGuard(Guard):
    def isSatisfied(self, event: Event) -> bool:
        raise NotImplementedError


class GameFinishedGuard(Guard):
    def isSatisfied(self, event: Event) -> bool:
        raise NotImplementedError


class IsRecorderGuard(Guard):
    def isSatisfied(self, event: Event) -> bool:
        raise NotImplementedError


class DurationElapsedGuard(Guard):
    def __init__(self, duration: int, unit: str):
        self.duration = duration
        self.unit = unit

    def isSatisfied(self, event: Event) -> bool:
        raise NotImplementedError
