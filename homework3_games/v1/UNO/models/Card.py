from models.enums import Color, Number

class Card:
    def __init__(self, color: Color, number: Number):
        self._color = color
        self._number = number

    @property
    def color(self) -> Color:
        return self._color

    @property
    def number(self) -> Number:
        return self._number

    def is_match(self, other: 'Card') -> bool:
        """UNO 的核心：顏色相同或數字相同即可出牌"""
        return self.color == other.color or self.number == other.number
