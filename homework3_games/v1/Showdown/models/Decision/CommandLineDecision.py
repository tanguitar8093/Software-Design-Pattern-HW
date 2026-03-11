from models.Decision.Decision import Decision
from models.Hand import Hand
from models.Card import Card

class CommandLineDecision(Decision):
    
    def make_decision(self, hand: Hand) -> Card:
        if not hand.cards:
            raise ValueError("Hand is empty!")

        print("\nYour current hand:")
        for idx, card in enumerate(hand.cards):
            print(f"[{idx}] {card.suit.name} {card.rank.name}")

        while True:
            try:
                choice = int(input("Please enter the index of the card you want to play: "))
                if 0 <= choice < len(hand.cards):
                    chosen_card = hand.cards[choice]
                    hand.remove_card(chosen_card)
                    return chosen_card
                else:
                    print(f"Invalid index. Please enter a number between 0 and {len(hand.cards) - 1}.")
            except ValueError:
                print("Invalid input. Please enter an integer.")
        
