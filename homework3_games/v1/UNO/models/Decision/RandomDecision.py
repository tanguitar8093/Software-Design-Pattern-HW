from models.Decision.Decision import Decision
from models.Hand import Hand
from models.Card import Card
import random

class RandomDecision(Decision):
    
    def make_choice(self, hand: Hand, top_card: Card = None) -> Card:
        valid_cards = [card for card in hand.cards if top_card is None or card.is_match(top_card)]
        if not valid_cards:
            return None
            
        chosen_card = random.choice(valid_cards)
        hand.remove_card(chosen_card)
        return chosen_card
