from abc import ABC


class Participant(ABC):
    """對應 OOA-Clean.mmd Participant (abstract)：Member 與 Bot 的共通父類別。"""

    def __init__(self, id: str) -> None:
        self.id = id
