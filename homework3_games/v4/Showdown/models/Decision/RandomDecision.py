import random
from models.Decision.Decision import Decision
from models.Hand import Hand
from models.Card import Card


class RandomDecision(Decision):
    """AI 玩家：從手牌中隨機選牌（context 不使用）。"""

    def make_decision(self, hand: Hand, context=None) -> Card:
        if not hand.cards:
            raise ValueError("Hand is empty!")
        chosen_card = random.choice(hand.cards)
        hand.remove_card(chosen_card)
        return chosen_card
