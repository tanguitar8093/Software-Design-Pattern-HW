import random
from models.Decision.Decision import Decision
from models.Hand import Hand
from models.Card import Card


class RandomDecision(Decision):
    """
    AI 玩家：從合法牌中隨機選牌。
    context 為頂牌（Card），用於篩選可出的牌。
    """

    def make_decision(self, hand: Hand, context: Card = None) -> Card:
        valid_cards = [card for card in hand.cards
                       if context is None or card.is_match(context)]
        if not valid_cards:
            return None
        chosen_card = random.choice(valid_cards)
        hand.remove_card(chosen_card)
        return chosen_card
