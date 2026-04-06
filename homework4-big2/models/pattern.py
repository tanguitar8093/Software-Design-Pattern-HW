from abc import ABC, abstractmethod
from typing import List, Any
from models.card import Card

RANK_ORDER = {"3": 1, "4": 2, "5": 3, "6": 4, "7": 5, "8": 6, "9": 7, "10": 8, "J": 9, "Q": 10, "K": 11, "A": 12, "2": 13}
SUIT_ORDER = {"C": 1, "D": 2, "H": 3, "S": 4}

def _is_card_less_than(c1: Card, c2: Card) -> bool:
    r1, r2 = RANK_ORDER[c1.rank.value], RANK_ORDER[c2.rank.value]
    if r1 != r2:
        return r1 < r2
    return SUIT_ORDER[c1.suit.value] < SUIT_ORDER[c2.suit.value]

def _get_max_card(cards: List[Card]) -> Card:
    max_card = cards[0]
    for c in cards[1:]:
        if _is_card_less_than(max_card, c):
            max_card = c
    return max_card

class CardPattern(ABC):
    def __init__(self, cards: List[Card]):
        self._cards = cards

    @property
    def cards(self) -> List[Card]:
        return self._cards[:]

    @abstractmethod
    def get_pattern_name(self) -> str:
        pass

    @abstractmethod
    def validate(self) -> bool:
        pass

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, CardPattern):
            return NotImplemented
        if type(self) is not type(other):
            raise TypeError("不同牌型不能比較大小")
        return _is_card_less_than(self._get_compare_card(), other._get_compare_card())

    @abstractmethod
    def _get_compare_card(self) -> Card:
        """回傳在此牌型中，用來比較大小的代表牌 (最大牌)"""
        pass

class Single(CardPattern):
    def get_pattern_name(self) -> str:
        return "單張"

    def validate(self) -> bool:
        return len(self.cards) == 1

    def _get_compare_card(self) -> Card:
        return self.cards[0]

class Pair(CardPattern):
    def get_pattern_name(self) -> str:
        return "對子"

    def validate(self) -> bool:
        if len(self.cards) != 2:
            return False
        return self.cards[0].rank == self.cards[1].rank

    def _get_compare_card(self) -> Card:
        return _get_max_card(self.cards)

class Straight(CardPattern):
    def get_pattern_name(self) -> str:
        return "順子"

    def validate(self) -> bool:
        if len(self.cards) != 5:
            return False
        # 判斷是否為連續順子
        # 先取得 5 張牌的 rank order (1~13)
        ranks = sorted(list(set(RANK_ORDER[c.rank.value] for c in self.cards)))
        
        if len(ranks) != 5: # 不可以有重複數字
            return False
            
        # 檢查間距，如果排序後的 cyclic 差距中，剛好有 4 個差距是 1，1 個差距是 9，或是最尾減最頭是 4
        # a. 正常情況 (例如 3 4 5 6 7): 最大值 - 最小值 = 4
        if ranks[4] - ranks[0] == 4:
            return True
            
        # b. 跨越情況 (例如 K A 2 3 4 -> 1 2 11 12 13)
        # 用 cyclic gaps 來檢查：
        gaps = [ranks[i+1] - ranks[i] for i in range(4)]
        gaps.append(ranks[0] + 13 - ranks[4])
        # 若它是個順子，則剛好有一個 gap 會是 9 (13-5+1)，其他都是 1
        if sorted(gaps) == [1, 1, 1, 1, 9]:
            return True

        return False

    def _get_compare_card(self) -> Card:
        return _get_max_card(self.cards)

class FullHouse(CardPattern):
    def get_pattern_name(self) -> str:
        return "葫蘆"

    def validate(self) -> bool:
        if len(self.cards) != 5:
            return False
        # 判斷是否為 3 + 2
        rank_counts = {}
        for c in self.cards:
            rank_counts[c.rank] = rank_counts.get(c.rank, 0) + 1
        counts = sorted(rank_counts.values())
        return counts == [2, 3]

    def _get_compare_card(self) -> Card:
        # 以三張數字相同的牌中，最大的那張作為比較基準
        rank_counts = {}
        for c in self.cards:
            rank_counts[c.rank] = rank_counts.get(c.rank, 0) + 1
        
        # 找出數量為 3 的 Rank
        three_of_a_kind_rank = None
        for rank, count in rank_counts.items():
            if count == 3:
                three_of_a_kind_rank = rank
                break
                
        # 找出該 Rank 的 3 張牌，取最大的一張
        three_cards = [c for c in self.cards if c.rank == three_of_a_kind_rank]
        return _get_max_card(three_cards)
