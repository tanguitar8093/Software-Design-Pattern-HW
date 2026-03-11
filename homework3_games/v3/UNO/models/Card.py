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
        return self.color == other.color or self.number == other.number
