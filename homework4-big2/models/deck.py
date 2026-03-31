import random
from typing import List
from models.card import Card, Suit, Rank
from models.validator import Validator

class Deck:
    # 1. 依然使用 Validator 保護資料，但對象改為私有的 _cards
    # 驗證規則保持不變，確保進入 _cards 的資料都是合法的
    _cards = Validator(list, rule=lambda lst: all(isinstance(c, Card) for c in lst) and len(lst) <= 52)
    
    def __init__(self):
        # 2. 初始化時，將生成的牌組賦值給私有屬性 _cards
        self._cards = [Card(rank, suit) for suit in Suit for rank in Rank]

    @property
    def cards(self) -> List[Card]:
        """
        3. 提供對外的唯讀接口。
        使用 [:] 回傳 list 的副本 (Shallow Copy)，
        這樣外部執行 deck.cards.append(...) 只會改到副本，不會影響內部的 _cards。
        """
        return self._cards[:]

    def shuffle(self) -> None:
        """打亂牌堆：直接操作內部私有屬性"""
        print("正在洗牌...")
        random.shuffle(self._cards)

    def deal(self) -> Card:
        """發牌：直接操作內部私有屬性，並回傳一張牌"""
        if not self._cards:
            raise ValueError("牌堆已空，沒有牌可發")
        return self._cards.pop()

    def __len__(self) -> int:
        """方便外部查詢剩餘張數：len(deck)"""
        return len(self._cards)