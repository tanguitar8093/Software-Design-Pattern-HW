from models.Decision.Decision import Decision
from models.Hand import Hand
from models.Card import Card
import random

class RandomDecision(Decision):
    def make_decision(self, hand: Hand) -> Card:
        if not hand.cards:
            raise ValueError("Hand is empty!")
        chosen_card = random.choice(hand.cards)
        hand.remove_card(chosen_card)
        return chosen_card
