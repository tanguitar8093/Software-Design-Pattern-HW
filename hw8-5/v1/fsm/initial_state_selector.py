from .core import Event, Guard, InitialStateSelector, StateNode


class GuardedInitialStateSelector(InitialStateSelector):
    def __init__(self, candidates: list[tuple[Guard, StateNode]], fallback: StateNode):
        self.candidates = candidates
        self.fallback = fallback

    def select(self, event: Event) -> StateNode:
        for guard, state in self.candidates:
            if guard.isSatisfied(event):
                return state
        return self.fallback
