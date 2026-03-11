from models.Decision.Decision import Decision
from models.Hand import Hand
from models.Card import Card

class CommandLineDecision(Decision):
    def make_choice(self, hand: Hand, top_card: Card = None) -> Card:
        valid_cards = [card for card in hand.cards if top_card is None or card.is_match(top_card)]
        if not valid_cards:
            return None

        print("\nYour current hand:")
        for idx, card in enumerate(hand.cards):
            valid_flag = " (Valid)" if card in valid_cards else ""
            print(f"[{idx}] {card.color.name} {card.number.name}{valid_flag}")

        while True:
            try:
                choice = int(input("Please enter the index of the card you want to play: "))
                if 0 <= choice < len(hand.cards):
                    chosen_card = hand.cards[choice]
                    if chosen_card in valid_cards:
                        hand.remove_card(chosen_card)
                        return chosen_card
                    else:
                        print("Invalid choice! Card must match the top card's color or number.")
                else:
                    print(f"Invalid index. Please enter a number between 0 and {len(hand.cards) - 1}.")
            except ValueError:
                print("Invalid input. Please enter an integer.")
