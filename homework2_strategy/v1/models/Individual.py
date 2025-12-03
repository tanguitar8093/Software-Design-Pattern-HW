from enums import Gender
class Individual:
    def __init__(self,id: int, gender: Gender, age: int, intro: str, habits: list[str], coord: tuple[int, int]) -> None:
        self._id = id
        self._gender = gender
        self._age = age
        self._intro = intro
        self._habits = habits
        self._coord = coord
        if not id > 0:
            raise ValueError("id 必須大於 0")
        if not age >=18:
            raise ValueError("年齡要滿 18 歲")
        if gender not in Gender:
            raise ValueError("性別必須是 MALE 或 FEMALE")
        if not (len(intro)>0 and len(intro)<=200):
            raise ValueError("自我介紹介於 0 到 200 字之間")
        if not all(len(habit) <= 10 and len(habit)>0 for habit in habits):
            raise ValueError("每個興趣習慣介於 1 到 10 字之間")
    @property
    def id(self) -> int:
        return self._id
    @property
    def gender(self) -> Gender:
        return self._gender
    @property
    def age(self) -> int:
        return self._age
    @property
    def intro(self) -> str:
        return self._intro
    @property
    def habits(self) -> list[str]:
        return self._habits
    @property
    def coord(self) -> tuple:
        return self._coord