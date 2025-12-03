from enum import IntEnum

class Rank(IntEnum):
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14
class Suit(IntEnum):
    CLUB = 1      # 梅花
    DIAMOND = 2   # 菱形
    HEART = 3     # 愛心
    SPADE = 4     # 黑桃
class PlyaerId(IntEnum):
    P1 = 1
    P2 = 2
    P3 = 3
    P4 = 4