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
        """同色或同數字即可出牌。"""
        return self._color == other._color or self._number == other._number

    def __repr__(self) -> str:
        return f"{self._color.name} {self._number.name}"
