class State:
    def __init__(self):
        self.normal = True
        self.petrochemical = False
        self.poisoned = False
        self.cheerup = False
        self.duration = 0

    def __str__(self):
        if self.petrochemical: return f"Petrochemical({self.duration})"
        if self.poisoned: return f"Poisoned({self.duration})"
        if self.cheerup: return f"Cheerup({self.duration})"
        return "Normal"

    def set_state(self, state_name, duration=3):
        self.normal = self.petrochemical = self.poisoned = self.cheerup = False
        setattr(self, state_name, True)
        self.duration = duration

    def tick(self):
        if self.duration > 0:
            self.duration -= 1
        if self.duration == 0:
            self.set_state("normal", 0)
# forces: 需重構為狀態模式
# 1. 若需擴充狀態, 就必須改核心檔案, 違反 OCP
# 2. 狀態不同會造成不同的行為
