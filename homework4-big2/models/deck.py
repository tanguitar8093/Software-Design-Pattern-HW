import random
from models.card import Card, Suit, Rank

class Deck:
    def __init__(self):
        self._cards = [Card(rank, suit) for suit in Suit for rank in Rank]
        if len(self._cards) != 52:
            raise ValueError(f"牌堆初始化錯誤，應該有 52 張牌，但實際有 {len(self._cards)} 張")
    @property
    def cards(self) -> list[Card]:
        return self._cards[:]

    def shuffle(self) -> None:
        random.shuffle(self._cards)
        
        # 依註解格式 print 洗好的牌堆：最左邊為底部，最右邊為上方
        print(" ".join(str(card) for card in self._cards))

    def deal(self) -> Card:
        if not self._cards:
            raise ValueError("牌堆已空，沒有牌可發")
        return self._cards.pop()

    def __len__(self) -> int:
        return len(self._cards)